from django.conf import settings
from django.db import models

from apps.products.models import Product


class WarehouseType(models.Model):
    """Type of a warehouse record: incoming (ورود) or outgoing (خروج)."""

    INPUT_ID = 1
    OUTPUT_ID = 2

    warehouse_type_title = models.CharField(max_length=50, verbose_name='نوع انبار')

    def __str__(self):
        return self.warehouse_type_title

    @classmethod
    def get_input(cls):
        obj, _ = cls.objects.get_or_create(
            id=cls.INPUT_ID, defaults={'warehouse_type_title': 'ورود به انبار'}
        )
        return obj

    @classmethod
    def get_output(cls):
        obj, _ = cls.objects.get_or_create(
            id=cls.OUTPUT_ID, defaults={'warehouse_type_title': 'خروج از انبار'}
        )
        return obj

    class Meta:
        verbose_name = 'نوع انبار'
        verbose_name_plural = 'انواع روش انبار'


class Warehouse(models.Model):
    warehouse_type = models.ForeignKey(
        WarehouseType, on_delete=models.CASCADE,
        related_name='warehouses', verbose_name='نوع انبار',
    )
    user_registered = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='warehouse_user_registered', verbose_name='کاربر ثبت کننده',
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name='warehouse_products', verbose_name='کالا',
    )
    qty = models.IntegerField(verbose_name='تعداد')
    price = models.IntegerField(verbose_name='قیمت واحد', null=True, blank=True)
    register_date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')

    def __str__(self):
        return f"{self.warehouse_type}-{self.product}"

    class Meta:
        verbose_name = 'انبار'
        verbose_name_plural = 'انبارها'
