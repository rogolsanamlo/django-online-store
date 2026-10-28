from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

import utils
from apps.orders.models import Order
from apps.payments.models import Payment

from .forms import (
    ChangePasswordForm,
    ProfilePasswordForm,
    LoginUserForm,
    RegisterUserForm,
    RememberPasswordForm,
    UpdateProfileForm,
    VerifyRegisterForm,
)
from .models import Customer, CustomUser

USER_SESSION_KEY = 'user_session'


class AnonymousOnlyMixin:
    """Redirect already authenticated users away from auth pages."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('main:index')
        return super().dispatch(request, *args, **kwargs)


class RegisterUserView(AnonymousOnlyMixin, View):
    template_name = "accounts_app/register.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"form": RegisterUserForm()})

    def post(self, request, *args, **kwargs):
        # someone who registered earlier but never confirmed the SMS code may try again
        CustomUser.objects.filter(
            mobile_number=request.POST.get('mobile_number'), is_active=False, is_admin=False
        ).delete()

        form = RegisterUserForm(request.POST)
        if not form.is_valid():
            messages.error(request, 'خطا در ثبت نام')
            return render(request, self.template_name, {"form": form})

        data = form.cleaned_data
        active_code = utils.create_random_code(5)
        CustomUser.objects.create_user(
            mobile_number=data['mobile_number'],
            active_code=active_code,
            password=data['password1'],
        )
        utils.send_sms(data['mobile_number'], f'کد فعال سازی حساب شما {active_code} می باشد')
        request.session[USER_SESSION_KEY] = {
            'active_code': str(active_code),
            'mobile_number': data['mobile_number'],
            'remember_password': False,
        }
        messages.success(request, 'اطلاعات شما ثبت شد کد فعال سازی را وارد کنید')
        return redirect('accounts:verify')


class VerifyRegisterCodeView(AnonymousOnlyMixin, View):
    template_name = "accounts_app/verify_register_code.html"

    def get(self, request, *args, **kwargs):
        if USER_SESSION_KEY not in request.session:
            return redirect('accounts:register')
        return render(request, self.template_name, {"form": VerifyRegisterForm()})

    def post(self, request, *args, **kwargs):
        user_session = request.session.get(USER_SESSION_KEY)
        if not user_session:
            messages.error(request, 'نشست شما منقضی شده است، دوباره تلاش کنید')
            return redirect('accounts:register')

        form = VerifyRegisterForm(request.POST)
        if not form.is_valid():
            messages.error(request, 'اطلاعات وارد شده اشتباه است')
            return render(request, self.template_name, {"form": form})

        if form.cleaned_data['active_code'] != user_session['active_code']:
            messages.error(request, 'کد فعال سازی وارد شده اشتباه است')
            return render(request, self.template_name, {"form": form})

        if not user_session['remember_password']:
            user = CustomUser.objects.get(mobile_number=user_session['mobile_number'])
            user.is_active = True
            user.active_code = utils.create_random_code(5)
            user.save()
            request.session.pop(USER_SESSION_KEY, None)
            messages.success(request, 'ثبت نام با موفقیت انجام شد')
            return redirect('accounts:login')

        # forgot-password flow: mark the mobile number as verified
        user_session['verified'] = True
        request.session[USER_SESSION_KEY] = user_session
        messages.success(request, 'شماره موبایل تایید شد رمز جدید را وارد کنید')
        return redirect('accounts:change_password')


class LoginUserView(AnonymousOnlyMixin, View):
    template_name = "accounts_app/login.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"form": LoginUserForm()})

    def post(self, request, *args, **kwargs):
        form = LoginUserForm(request.POST)
        if not form.is_valid():
            messages.error(request, 'اطلاعات وارد شده نامعتبر')
            return render(request, self.template_name, {"form": form})

        data = form.cleaned_data
        user = authenticate(request, username=data['mobile_number'], password=data['password'])
        if user is None:
            messages.error(request, 'اطلاعات وارد شده نادرست')
            return render(request, self.template_name, {"form": form})

        if user.is_admin:
            messages.warning(request, 'کاربر ادمین نمی تواند از اینجا وارد شود')
            return render(request, self.template_name, {"form": form})

        login(request, user)
        messages.success(request, 'ورود با موفقیت انجام شد')
        next_url = request.GET.get('next')
        if next_url and next_url.startswith('/') and not next_url.startswith('//'):
            return redirect(next_url)
        return redirect('main:index')


class LogoutUserView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('main:index')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # keep the shopping cart after logout (logout flushes the session)
        shop_cart = request.session.get('shop_cart')
        logout(request)
        if shop_cart:
            request.session['shop_cart'] = shop_cart
        return redirect('main:index')


class ChangePasswordView(View):
    """Last step of the 'forgot password' flow.

    Only reachable after the mobile number has been verified by SMS code
    (stored in the session), never for arbitrary users.
    """

    template_name = "accounts_app/change_password.html"

    def dispatch(self, request, *args, **kwargs):
        user_session = request.session.get(USER_SESSION_KEY)
        if not user_session or not user_session.get('verified'):
            messages.error(request, 'ابتدا شماره موبایل خود را تایید کنید')
            return redirect('accounts:remember_password')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"form": ChangePasswordForm()})

    def post(self, request, *args, **kwargs):
        form = ChangePasswordForm(request.POST)
        if not form.is_valid():
            messages.error(request, 'اطلاعات وارد شده نامعتبر')
            return render(request, self.template_name, {"form": form})

        user_session = request.session[USER_SESSION_KEY]
        user = CustomUser.objects.get(mobile_number=user_session['mobile_number'])
        user.set_password(form.cleaned_data['password1'])
        user.active_code = utils.create_random_code(5)
        user.save()
        request.session.pop(USER_SESSION_KEY, None)
        messages.success(request, 'رمز عبور شما با موفقیت تغییر کرد')
        return redirect('accounts:login')


class ChangeMyPasswordView(LoginRequiredMixin, View):
    """Password change from the user panel (for a logged-in user who knows the current password)."""

    template_name = 'accounts_app/change_my_password.html'

    def get(self, request):
        return render(request, self.template_name, {'form': ProfilePasswordForm()})

    def post(self, request):
        form = ProfilePasswordForm(request.POST)
        if form.is_valid():
            if not request.user.check_password(form.cleaned_data['current_password']):
                form.add_error('current_password', 'رمز عبور فعلی نادرست است')
            else:
                request.user.set_password(form.cleaned_data['password1'])
                request.user.save()
                update_session_auth_hash(request, request.user)  # stay logged in
                messages.success(request, 'رمز عبور شما با موفقیت تغییر کرد')
                return redirect('accounts:userpanel')
        messages.error(request, 'اطلاعات وارد شده نامعتبر است')
        return render(request, self.template_name, {'form': form})


class RememberPasswordView(AnonymousOnlyMixin, View):
    template_name = "accounts_app/remember_password.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"form": RememberPasswordForm()})

    def post(self, request, *args, **kwargs):
        form = RememberPasswordForm(request.POST)
        if not form.is_valid():
            messages.error(request, 'اطلاعات وارد شده نامعتبر')
            return render(request, self.template_name, {"form": form})

        mobile_number = form.cleaned_data['mobile_number']
        try:
            user = CustomUser.objects.get(mobile_number=mobile_number)
        except CustomUser.DoesNotExist:
            messages.error(request, 'شماره موبایل وارد شده نامعتبر')
            return render(request, self.template_name, {"form": form})

        active_code = utils.create_random_code(5)
        user.active_code = active_code
        user.save()
        utils.send_sms(mobile_number, f'کد تایید شماره موبایل شما {active_code} می باشد')
        request.session[USER_SESSION_KEY] = {
            'active_code': str(active_code),
            'mobile_number': mobile_number,
            'remember_password': True,
        }
        messages.success(request, 'جهت تغییر رمز عبور خود کد دریافتی را ارسال کنید')
        return redirect('accounts:verify')


class UserPanelView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        user_info = {"name": user.name, "family": user.family, "email": user.email}
        customer = Customer.objects.filter(user=user).first()
        if customer:
            user_info.update({
                "phone_number": customer.phone_number,
                "address": customer.address,
                "image": customer.image_name,
            })
        return render(request, "accounts_app/userpanel.html", {"user_info": user_info})


class UpdateProfileView(LoginRequiredMixin, View):
    template_name = "accounts_app/update_profile.html"

    def get(self, request):
        user = request.user
        customer = Customer.objects.filter(user=user).first()
        initial = {
            "name": user.name,
            "family": user.family,
            "email": user.email,
            "mobile_number": user.mobile_number,
        }
        if customer:
            initial.update({"phone_number": customer.phone_number, "address": customer.address})
        form = UpdateProfileForm(initial=initial)
        return render(request, self.template_name, {
            "form": form,
            "image_url": customer.image_name if customer else None,
        })

    def post(self, request):
        form = UpdateProfileForm(request.POST, request.FILES)
        customer = Customer.objects.filter(user=request.user).first()
        if not form.is_valid():
            messages.error(request, 'اطلاعات وارد شده نامعتبر')
            return render(request, self.template_name, {
                "form": form,
                "image_url": customer.image_name if customer else None,
            })

        cd = form.cleaned_data
        user = request.user
        user.name = cd['name']
        user.family = cd['family']
        user.email = cd['email']
        user.save()

        customer, _ = Customer.objects.get_or_create(user=user)
        customer.phone_number = cd['phone_number']
        customer.address = cd['address']
        if cd.get('image'):  # keep the old picture when nothing new is uploaded
            customer.image_name = cd['image']
        customer.save()

        messages.success(request, 'ویرایش پروفایل با موفقیت انجام شد')
        return redirect('accounts:userpanel')


@login_required
def show_last_orders(request):
    # Customer's primary key is the user id
    orders = Order.objects.filter(customer_id=request.user.id).order_by('-register_date')[:4]
    return render(request, "accounts_app/partials/show_last_orders.html", {'orders': orders})


@login_required
def show_user_payments(request):
    payments = Payment.objects.filter(customer_id=request.user.id).order_by('-register_date')
    return render(request, "accounts_app/show_user_payments.html", {'payments': payments})
