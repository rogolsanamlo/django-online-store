import uuid

from django.db import models
from django.utils import timezone

import utils
from apps.accounts.models import Customer
from apps.products.models import Product


class PaymentType(models.Model):
    DEFAULT_ID = 1

    payment_title = models.CharField(max_length=50, verbose_name='نوع پرداخت')

    def __str__(self):
        return self.payment_title

    @classmethod
    def get_default(cls):
        obj, _ = cls.objects.get_or_create(
            id=cls.DEFAULT_ID, defaults={'payment_title': 'پرداخت آنلاین'}
        )
        return obj

    class Meta:
        verbose_name = 'نوع پرداخت'
        verbose_name_plural = 'انواع روش پرداخت'


class OrderState(models.Model):
    """Order lifecycle state. ``PAID_ID`` is the state set after a successful payment."""

    PAID_ID = 1

    order_state_title = models.CharField(max_length=50, verbose_name='عنوان وضعیت سفارش')

    def __str__(self):
        return self.order_state_title

    @classmethod
    def get_paid(cls):
        obj, _ = cls.objects.get_or_create(
            id=cls.PAID_ID, defaults={'order_state_title': 'پرداخت شده'}
        )
        return obj

    class Meta:
        verbose_name = 'وضعیت سفارش'
        verbose_name_plural = 'انواع وضعیتهای سفارش'


class Order(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='orders', verbose_name='مشتری'
    )
    register_date = models.DateField(default=timezone.now, verbose_name='تاریخ درج سفارش')
    update_date = models.DateField(auto_now=True, verbose_name='تاریخ ویرایش سفارش')
    is_finally = models.BooleanField(default=False, verbose_name='نهایی شده')
    order_code = models.UUIDField(
        unique=True, default=uuid.uuid4, editable=False, verbose_name='کد تولیدی برای سفارش'
    )
    discount = models.IntegerField(
        blank=True, null=True, default=0, verbose_name='تخفیف روی فاکتور (درصد)'
    )
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    payment_type = models.ForeignKey(
        PaymentType, default=None, on_delete=models.CASCADE, null=True, blank=True,
        related_name='payment_types', verbose_name='نوع پرداخت',
    )
    order_state = models.ForeignKey(
        OrderState, on_delete=models.CASCADE, null=True, blank=True,
        related_name='orders_states', verbose_name='وضعیت سفارش',
    )

    def get_items_total_price(self):
        """Sum of (unit price at order time x qty) in Toman."""
        return sum(item.get_total_price() for item in self.orders_details1.all())

    def get_order_total_price(self):
        """Final payable amount in **Toman**: items + delivery + tax - coupon."""
        final_price, _delivery, _tax = utils.price_by_delivery_tax(
            self.get_items_total_price(), self.discount
        )
        return final_price

    def get_order_total_price_rial(self):
        """Final payable amount in **Rial** (what the payment gateway expects)."""
        return self.get_order_total_price() * 10

    def __str__(self):
        return f"{self.customer}\t{self.id}\t{self.is_finally}"

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارشات'


class OrderDetails(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='orders_details1', verbose_name='سفارش'
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='orders_details2', verbose_name='کالا'
    )
    qty = models.PositiveIntegerField(default=1, verbose_name='تعداد')
    price = models.IntegerField(verbose_name='قیمت واحد کالا در فاکتور (پس از تخفیف)')

    def get_total_price(self):
        return self.price * self.qty

    def __str__(self):
        return f"{self.order}\t{self.product}\t{self.qty}\t{self.price}"

    class Meta:
        verbose_name = 'جزئیات سفارش'
        verbose_name_plural = 'جزئیات سفارشات'
