import jdatetime
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.accounts.models import Customer
from apps.orders.models import Order


class Payment(models.Model):
    """One attempt to pay an order through the ZarinPal gateway.

    ``amount`` is stored in Toman (same unit as the rest of the shop);
    it is converted to Rial when talking to the gateway.
    """

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name='payment_order', verbose_name='سفارش',
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE,
        related_name='payment_customer', verbose_name='مشتری',
    )
    register_date = models.DateTimeField(default=timezone.now, verbose_name='تاریخ پرداخت')
    update_date = models.DateTimeField(auto_now=True, verbose_name='تاریخ ویرایش پرداخت')
    amount = models.PositiveIntegerField(
        verbose_name='مبلغ پرداخت (تومان)', validators=[MinValueValidator(0)]
    )
    description = models.TextField(verbose_name='توضیحات پرداخت', blank=True)
    is_finally = models.BooleanField(default=False, verbose_name='وضعیت پرداخت')
    status_code = models.IntegerField(
        verbose_name='کد وضعیت درگاه پرداخت', null=True, blank=True
    )
    ref_id = models.CharField(
        max_length=50, verbose_name='شماره پیگیری پرداخت', null=True, blank=True
    )
    authority = models.CharField(
        max_length=100, null=True, blank=True, db_index=True,
        verbose_name='شناسه پرداخت زرین پال',
    )

    class Meta:
        verbose_name = 'پرداخت'
        verbose_name_plural = 'پرداخت ها'
        ordering = ('-register_date',)

    def __str__(self):
        return f"{self.order}\t{self.customer}\t{self.ref_id}"

    def payment_register_date_jalali_type(self):
        return jdatetime.datetime.fromgregorian(datetime=self.register_date)

    payment_register_date_jalali_type.short_description = 'تاریخ پرداخت'
