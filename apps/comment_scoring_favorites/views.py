from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.decorators.http import require_POST

from apps.products.models import Product

from .forms import CommentForm
from .models import Comment, Favorite, Scoring


def ajax_login_required(view):
    """Like ``login_required`` but answers AJAX calls with 401 instead of a redirect to the login page."""

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponse('برای این کار ابتدا وارد حساب کاربری خود شوید', status=401)
        return view(request, *args, **kwargs)

    return wrapper


class CommentView(LoginRequiredMixin, View):
    template_name = "csf_app/partials/create_comment.html"

    def get(self, request, *args, **kwargs):
        initial = {
            'product_id': request.GET.get('productId'),
            'comment_id': request.GET.get('commentId'),
        }
        form = CommentForm(initial=initial)
        return render(request, self.template_name, {"form": form, "slug": kwargs['slug']})

    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Product, slug=kwargs['slug'])
        form = CommentForm(request.POST)
        if not form.is_valid():
            messages.error(request, 'خطا در ارسال نظر')
            return redirect("products:product_detail", product.slug)

        cd = form.cleaned_data
        parent = None
        if cd['comment_id']:
            parent = get_object_or_404(Comment, id=cd['comment_id'], product=product)

        Comment.objects.create(
            product=product,
            commenting_user=request.user,
            comment_text=cd['comment_text'],
            comment_parent=parent,
        )
        messages.success(request, 'نظر شما با موفقیت ثبت شد و پس از تایید نمایش داده می شود')
        return redirect("products:product_detail", product.slug)


@ajax_login_required
def add_score(request):
    product = get_object_or_404(Product, id=request.GET.get('productId'))
    try:
        score = int(request.GET.get('score'))
    except (TypeError, ValueError):
        return HttpResponseBadRequest("امتیاز نامعتبر است")
    if not 0 <= score <= 5:
        return HttpResponseBadRequest("امتیاز باید بین 0 تا 5 باشد")

    # one score per user and product: update instead of piling up duplicates
    Scoring.objects.update_or_create(
        product=product, scoring_user=request.user, defaults={'score': score}
    )
    return HttpResponse("امتیاز شما با موفقیت ثبت شد")


@require_POST
@ajax_login_required
def toggle_favorite(request):
    """Add the product to the user's favourites, or remove it if it is already there."""
    product = get_object_or_404(Product, id=request.POST.get('productId'))
    favorite, created = Favorite.objects.get_or_create(product=product, favorite_user=request.user)
    if created:
        return JsonResponse({'favorite': True, 'message': 'کالا به لیست علاقه‌مندی‌ها اضافه شد'})
    favorite.delete()
    return JsonResponse({'favorite': False, 'message': 'کالا از لیست علاقه‌مندی‌ها حذف شد'})


@login_required
def remove_from_favorite(request):
    if request.method == 'POST':
        Favorite.objects.filter(
            favorite_user=request.user, product_id=request.POST.get('productId')
        ).delete()
        messages.success(request, 'کالا از لیست علاقه‌مندی‌ها حذف شد')
    return redirect('csf:user_favorite')


class UserFavoriteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        favorites = Favorite.objects.filter(favorite_user=request.user).select_related('product')
        return render(request, 'csf_app/user_favorite.html', {'favorites': favorites})
