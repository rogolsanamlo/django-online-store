from django.contrib import admin

from .models import Order, OrderDetails, OrderState, PaymentType


class OrderDetailsInline(admin.TabularInline):
    model = OrderDetails
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'order_state', 'register_date', 'is_finally', 'discount']
    list_filter = ['is_finally', 'order_state']
    inlines = [OrderDetailsInline]


@admin.register(OrderState)
class OrderStateAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_state_title']


@admin.register(PaymentType)
class PaymentTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'payment_title']
