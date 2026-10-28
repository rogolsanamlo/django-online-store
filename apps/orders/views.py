from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

import utils
from apps.accounts.models import Customer
from apps.discounts.forms import CouponForm
from apps.discounts.models import Coupon
from apps.products.models import Product

from .forms import OrderForm
from .models import Order, OrderDetails, PaymentType
from .shop_cart import ShopCart


class ShopCartView(View):
    """Shopping cart page (the table itself is rendered by ``show_shop_cart``)."""

    def get(self, request, *args, **kwargs):
        return render(request, 'orders_app/shop_cart.html', {"shop_cart": ShopCart(request)})


def show_shop_cart(request):
    shop_cart = ShopCart(request)
    total_price = shop_cart.calc_total_price()
    order_final_price, delivery, tax = utils.price_by_delivery_tax(total_price)
    context = {
        "shop_cart": shop_cart,
        "shop_cart_count": shop_cart.count,
        "total_price": total_price,
        "delivery": delivery,
        "tax": tax,
        "order_final_price": order_final_price,
    }
    return render(request, 'orders_app/partials/show_shop_cart.html', context)


def add_to_shop_cart(request):
    product = get_object_or_404(Product, id=request.GET.get('product_id'), is_active=True)
    try:
        qty = int(request.GET.get('qty', 1))
    except (TypeError, ValueError):
        qty = 1
    shop_cart = ShopCart(request)
    shop_cart.add_to_shop_cart(product, qty)
    return HttpResponse(shop_cart.count)


def delete_from_shop_cart(request):
    product = get_object_or_404(Product, id=request.GET.get('product_id'))
    ShopCart(request).delete_from_shop_cart(product)
    return redirect("orders:show_shop_cart")


def update_shop_cart(request):
    product_id_list = request.GET.getlist('product_id_list[]')
    qty_list = request.GET.getlist('qty_list[]')
    ShopCart(request).update(product_id_list, qty_list)
    return show_shop_cart(request)


def status_of_shop_cart(request):
    return HttpResponse(ShopCart(request).count)


class CreateOrderView(LoginRequiredMixin, View):
    """Turns the session cart into a real ``Order`` and goes to checkout."""

    def get(self, request):
        shop_cart = ShopCart(request)
        items = list(shop_cart)
        if not items:
            messages.error(request, 'سبد خرید شما خالی است')
            return redirect('orders:shop_cart')

        customer, _ = Customer.objects.get_or_create(user=request.user)

        with transaction.atomic():
            order = Order.objects.create(customer=customer, payment_type=PaymentType.get_default())
            for item in items:
                product = item['product']
                OrderDetails.objects.create(
                    order=order,
                    product=product,
                    qty=item['qty'],
                    # always trust the DB price, not the one stored in the session
                    price=product.get_price_by_discount(),
                )
        return redirect('orders:checkout_order', order.id)


class CheckoutOrderView(LoginRequiredMixin, View):
    template_name = 'orders_app/checkout.html'

    def get_order(self, request, order_id):
        # only the owner can see/pay an order, and only while it is unpaid
        return get_object_or_404(
            Order, id=order_id, customer__user=request.user, is_finally=False
        )

    def get(self, request, order_id):
        user = request.user
        order = self.get_order(request, order_id)
        customer = order.customer

        total_price = order.get_items_total_price()
        order_final_price, delivery, tax = utils.price_by_delivery_tax(total_price, order.discount)

        form = OrderForm(initial={
            'name': user.name,
            'family': user.family,
            'email': user.email,
            'phone_number': customer.phone_number,
            'address': customer.address,
            'description': order.description,
            'payment_type': order.payment_type_id,
        })
        context = {
            'order_items': order.orders_details1.select_related('product'),
            'shop_cart': ShopCart(request),
            'total_price': total_price,
            'delivery': delivery,
            'tax': tax,
            'order_final_price': order_final_price,
            'form': form,
            'form_coupon': CouponForm(),
            'order': order,
        }
        return render(request, self.template_name, context)

    def post(self, request, order_id):
        order = self.get_order(request, order_id)
        form = OrderForm(request.POST)
        if not form.is_valid():
            messages.error(request, 'اطلاعات وارد شده نامعتبر است، لطفاً فرم را بررسی کنید')
            return redirect('orders:checkout_order', order_id)

        cd = form.cleaned_data
        with transaction.atomic():
            order.description = cd['description']
            order.payment_type = cd['payment_type']
            order.save()

            user = request.user
            user.name = cd['name']
            user.family = cd['family']
            user.email = cd['email']
            user.save()

            customer = order.customer
            customer.phone_number = cd['phone_number']
            customer.address = cd['address']
            customer.save()

        return redirect('payments:zarinpal_payment', order_id)


class ApplyCoupon(LoginRequiredMixin, View):
    """Validates a coupon code and stores its percentage on the order."""

    def post(self, request, order_id):
        order = get_object_or_404(
            Order, id=order_id, customer__user=request.user, is_finally=False
        )
        form = CouponForm(request.POST)
        if not form.is_valid():
            messages.error(request, 'کد تخفیف را وارد کنید')
            return redirect('orders:checkout_order', order_id)

        now = datetime.now()
        coupon = Coupon.objects.filter(
            Q(coupon_code=form.cleaned_data['coupon_code'])
            & Q(is_active=True)
            & Q(start_date__lte=now)
            & Q(end_date__gte=now)
        ).first()

        if coupon:
            order.discount = coupon.discount
            order.save()
            messages.success(request, 'اعمال کوپن با موفقیت انجام شد')
        else:
            order.discount = 0
            order.save()
            messages.error(request, 'کد وارد شده معتبر نیست')
        return redirect('orders:checkout_order', order_id)
