from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id", "order", "customer", "amount", "is_finally",
        "status_code", "ref_id", "payment_register_date_jalali_type",
    )
    list_filter = ("is_finally", "status_code")
    search_fields = ("authority", "ref_id", "customer__user__mobile_number")
    readonly_fields = (
        "order", "customer", "amount", "authority", "ref_id",
        "status_code", "is_finally", "register_date", "update_date",
    )

    def has_add_permission(self, request):
        # payments are created only by the checkout flow
        return False
