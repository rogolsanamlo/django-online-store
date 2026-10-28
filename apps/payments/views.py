import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from apps.orders.models import Order, OrderState
from apps.warehouses.models import Warehouse, WarehouseType

from . import gateway
from .models import Payment

logger = logging.getLogger(__name__)

# ZarinPal verify() result codes
CODE_VERIFIED = 100
CODE_ALREADY_VERIFIED = 101


def redirect_to_payment_message(request, message):
    """Store the result in the session and show it on the result page.

    The message is kept in the session (not in the URL) so nobody can fake a
    "payment succeeded" page by crafting a link.
    """
    request.session["payment_message"] = message
    return redirect("payments:show_verify_message")


def finalize_payment(payment, status_code, ref_id, user):
    """Mark ``payment`` and its order as paid and take the goods out of the warehouse.

    Safe to call more than once: a payment that is already final is ignored,
    so stock is never deducted twice (e.g. user refreshes the callback URL).
    Returns True if this call did the finalization.
    """
    with transaction.atomic():
        payment = Payment.objects.select_for_update().get(pk=payment.pk)
        if payment.is_finally:
            return False

        payment.is_finally = True
        payment.status_code = status_code
        payment.ref_id = str(ref_id)
        payment.save()

        order = payment.order
        order.is_finally = True
        order.order_state = OrderState.get_paid()
        order.save()

        output_type = WarehouseType.get_output()
        for item in order.orders_details1.select_related("product"):
            Warehouse.objects.create(
                warehouse_type=output_type,
                user_registered=user,
                product=item.product,
                qty=item.qty,
                price=item.price,
            )
    return True


class ZarinPalPaymentView(LoginRequiredMixin, View):
    """Step 1: create a payment request and send the user to the gateway."""

    def get(self, request, order_id):
        user = request.user

        order = get_object_or_404(Order, id=order_id, customer__user=user)

        if not order.customer.address:
            messages.error(request, "برای ثبت سفارش ابتدا اطلاعات و آدرس خود را تکمیل کنید")
            return redirect("orders:checkout_order", order.id)

        if order.is_finally:
            return redirect_to_payment_message(request, "این سفارش قبلاً پرداخت شده است.")

        amount = order.get_order_total_price()  # Toman
        if amount <= 0:
            return redirect_to_payment_message(request, "مبلغ سفارش نامعتبر است.")

        payment = Payment.objects.create(
            order=order,
            customer=order.customer,
            amount=amount,
            description="پرداخت از طریق درگاه زرین پال",
        )

        try:
            response = gateway.request_payment(
                amount=order.get_order_total_price_rial(),
                callback_url=request.build_absolute_uri(reverse("payments:zarinpal_verify")),
                description=f"پرداخت سفارش شماره {order.id}",
                mobile=user.mobile_number,
                email=user.email,
            )

            data = response.get("data") if isinstance(response, dict) else None
            if not isinstance(data, dict) or not data:
                logger.warning("ZarinPal request failed for order %s: %s", order.id, response)
                return redirect_to_payment_message(request, "خطا در ایجاد درخواست پرداخت.")

            authority = data.get("authority")
            if not authority:
                return redirect_to_payment_message(request, "Authority از زرین پال دریافت نشد.")

            payment.authority = authority
            payment.save()

            return redirect(gateway.payment_url(authority))

        except Exception:
            logger.exception("ZarinPal connection error (order %s)", order.id)
            return redirect_to_payment_message(
                request, "خطا در ارتباط با درگاه پرداخت. لطفاً دوباره تلاش کنید."
            )


class ZarinPalPaymentVerifyView(LoginRequiredMixin, View):
    """Step 2: the gateway sends the user back here; verify the payment."""

    def get(self, request):
        status = request.GET.get("Status")
        authority = request.GET.get("Authority")

        if status != "OK":
            return redirect_to_payment_message(request, "پرداخت توسط کاربر لغو شد یا ناموفق بود.")

        payment = get_object_or_404(
            Payment, authority=authority, customer__user=request.user
        )

        # callback opened twice (refresh / back button): nothing more to do
        if payment.is_finally:
            return redirect_to_payment_message(
                request, f"این پرداخت قبلاً تأیید شده است. کد رهگیری: {payment.ref_id}"
            )

        try:
            response = gateway.verify_payment(
                # verify with the amount we stored when the payment was created
                amount=payment.amount * 10,
                authority=authority,
            )

            data = response.get("data") if isinstance(response, dict) else None
            if not isinstance(data, dict):
                data = None
            status_code = data.get("code") if data else None

            if status_code is None:
                logger.warning("ZarinPal verify without code (payment %s): %s", payment.id, response)
                return redirect_to_payment_message(
                    request, "خطا در تأیید پرداخت. در صورت کسر وجه با پشتیبانی تماس بگیرید."
                )

            if status_code in (CODE_VERIFIED, CODE_ALREADY_VERIFIED):
                ref_id = data.get("ref_id")
                if not ref_id:
                    return redirect_to_payment_message(
                        request, "کد رهگیری از درگاه دریافت نشد. با پشتیبانی تماس بگیرید."
                    )

                finalize_payment(payment, status_code, ref_id, request.user)
                request.session.pop("shop_cart", None)

                if status_code == CODE_VERIFIED:
                    message = f"پرداخت با موفقیت انجام شد. کد رهگیری: {ref_id}"
                else:
                    message = "این پرداخت قبلاً تأیید شده است."
                return redirect_to_payment_message(request, message)

            payment.status_code = status_code
            payment.save()
            return redirect_to_payment_message(
                request, f"پرداخت ناموفق بود. کد وضعیت: {status_code}"
            )

        except Exception:
            logger.exception("ZarinPal verify error (payment %s)", payment.id)
            return redirect_to_payment_message(
                request, "خطا در تأیید پرداخت. در صورت کسر وجه با پشتیبانی تماس بگیرید."
            )


def show_verify_message(request):
    message = request.session.pop("payment_message", "نتیجه‌ای برای پرداخت وجود ندارد.")
    return render(request, "payments_app/verify_message.html", {"message": message})
