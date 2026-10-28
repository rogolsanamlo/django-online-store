import re

from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import CustomUser

REQUIRED_MESSAGE = {'required': 'این فیلد نمی‌تواند خالی باشد'}
PASSWORD_MISMATCH = 'رمز عبور و تکرار آن با هم مغایرت دارند'
MOBILE_PATTERN = re.compile(r'09\d{9}')


def text_input(placeholder, **extra):
    return forms.TextInput(attrs={'class': 'form-control', 'placeholder': placeholder, **extra})


def password_input(placeholder):
    return forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': placeholder})


def check_new_password(form):
    """Shared ``clean_password2``: both passwords match and satisfy Django's validators."""
    password1 = form.cleaned_data.get('password1')
    password2 = form.cleaned_data['password2']
    if password1 and password2 and password1 != password2:
        raise ValidationError(PASSWORD_MISMATCH)
    validate_password(password2)
    return password2


def check_mobile_number(mobile_number):
    if not MOBILE_PATTERN.fullmatch(mobile_number):
        raise ValidationError('شماره موبایل باید ۱۱ رقم باشد و با 09 شروع شود')
    return mobile_number


class UserCreationForm(forms.ModelForm):
    """Used by the admin to create users."""

    password1 = forms.CharField(label='رمز عبور', widget=forms.PasswordInput)
    password2 = forms.CharField(label='تکرار رمز عبور', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['mobile_number', 'email', 'name', 'family', 'gender']

    def clean_password2(self):
        return check_new_password(self)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """Used by the admin to edit users."""

    password = ReadOnlyPasswordHashField(
        label='رمز عبور',
        help_text="رمز عبور ذخیره نمی‌شود؛ برای تغییر آن از <a href='../password'>این فرم</a> استفاده کنید.",
    )

    class Meta:
        model = CustomUser
        fields = ['mobile_number', 'password', 'email', 'name', 'family', 'gender', 'is_active', 'is_admin']


class RegisterUserForm(forms.ModelForm):
    password1 = forms.CharField(label='رمز عبور', widget=password_input('رمز را وارد کنید'))
    password2 = forms.CharField(label='تکرار رمز عبور', widget=password_input('رمز اولی را دوباره وارد کنید'))

    class Meta:
        model = CustomUser
        fields = ['mobile_number']
        widgets = {'mobile_number': text_input('شماره موبایل را وارد کنید')}
        error_messages = {
            'mobile_number': {'unique': 'این شماره موبایل قبلاً ثبت نام کرده است'},
        }

    def clean_mobile_number(self):
        return check_mobile_number(self.cleaned_data['mobile_number'])

    def clean_password2(self):
        return check_new_password(self)


class VerifyRegisterForm(forms.Form):
    active_code = forms.CharField(
        label='کد فعال سازی',
        error_messages=REQUIRED_MESSAGE,
        widget=text_input('کد دریافتی را وارد کنید'),
    )


class LoginUserForm(forms.Form):
    mobile_number = forms.CharField(
        label='شماره موبایل',
        error_messages=REQUIRED_MESSAGE,
        widget=text_input('شماره موبایل را وارد کنید'),
    )
    password = forms.CharField(
        label='رمز عبور',
        error_messages=REQUIRED_MESSAGE,
        widget=password_input('رمز عبور را وارد کنید'),
    )


class RememberPasswordForm(forms.Form):
    mobile_number = forms.CharField(
        label='شماره موبایل',
        error_messages=REQUIRED_MESSAGE,
        widget=text_input('شماره موبایل را وارد کنید'),
    )


class ChangePasswordForm(forms.Form):
    password1 = forms.CharField(
        label='رمز عبور جدید',
        error_messages=REQUIRED_MESSAGE,
        widget=password_input('رمز عبور جدید را وارد کنید'),
    )
    password2 = forms.CharField(
        label='تکرار رمز عبور',
        error_messages=REQUIRED_MESSAGE,
        widget=password_input('رمز عبور را دوباره وارد کنید'),
    )

    def clean_password2(self):
        return check_new_password(self)


class ProfilePasswordForm(forms.Form):
    """Change the password of the logged-in user (the current password is required)."""

    current_password = forms.CharField(
        label='رمز عبور فعلی',
        error_messages=REQUIRED_MESSAGE,
        widget=password_input('رمز عبور فعلی'),
    )
    password1 = forms.CharField(
        label='رمز عبور جدید',
        error_messages=REQUIRED_MESSAGE,
        widget=password_input('رمز عبور جدید'),
    )
    password2 = forms.CharField(
        label='تکرار رمز عبور جدید',
        error_messages=REQUIRED_MESSAGE,
        widget=password_input('رمز عبور جدید را دوباره وارد کنید'),
    )

    def clean_password2(self):
        return check_new_password(self)


class UpdateProfileForm(forms.Form):
    name = forms.CharField(label='', error_messages=REQUIRED_MESSAGE, widget=text_input('نام'))
    family = forms.CharField(label='', error_messages=REQUIRED_MESSAGE, widget=text_input('نام خانوادگی'))
    email = forms.EmailField(
        label='',
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ایمیل'}),
    )
    mobile_number = forms.CharField(
        label='', widget=text_input('شماره موبایل', readonly='readonly')
    )
    phone_number = forms.CharField(label='', widget=text_input('شماره تلفن'))
    address = forms.CharField(
        label='',
        error_messages=REQUIRED_MESSAGE,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'آدرس', 'rows': '2'}),
    )
    image = forms.ImageField(required=False)
