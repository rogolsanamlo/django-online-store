from django.urls import path

from .views import show_verify_message, ZarinPalPaymentVerifyView, ZarinPalPaymentView

app_name = "payments"

urlpatterns = [
    path("request/<int:order_id>/", ZarinPalPaymentView.as_view(), name="zarinpal_payment"),
    path("verify/", ZarinPalPaymentVerifyView.as_view(), name="zarinpal_verify"),
    path("verify-message/", show_verify_message, name="show_verify_message"),
]
