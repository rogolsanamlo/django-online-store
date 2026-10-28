from unittest.mock import patch

from django.urls import reverse

from apps.accounts.models import CustomUser
from apps.orders.models import OrderState
from apps.orders.tests.base import BaseOrderTest
from apps.payments.models import Payment
from apps.warehouses.models import Warehouse

AUTHORITY = "A0000000000000000000000000000TEST"


class ZarinPalPaymentViewTests(BaseOrderTest):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)
        self.url = reverse("payments:zarinpal_payment", kwargs={"order_id": self.order.id})
        self.message_url = reverse("payments:show_verify_message")

    @patch("apps.payments.views.gateway")
    def test_create_payment(self, gateway):
        gateway.request_payment.return_value = {"data": {"authority": AUTHORITY}, "errors": []}
        gateway.payment_url.return_value = f"https://payment.test/{AUTHORITY}"

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"https://payment.test/{AUTHORITY}")

        payment = Payment.objects.get(order=self.order)
        self.assertEqual(payment.amount, self.order.get_order_total_price())
        self.assertEqual(payment.authority, AUTHORITY)

        # the gateway receives Rial, not Toman
        sent = gateway.request_payment.call_args.kwargs
        self.assertEqual(sent["amount"], self.order.get_order_total_price() * 10)
        self.assertTrue(sent["callback_url"].endswith(reverse("payments:zarinpal_verify")))
        self.assertEqual(sent["mobile"], self.user.mobile_number)

    @patch("apps.payments.views.gateway")
    def test_create_payment_without_data(self, gateway):
        gateway.request_payment.return_value = {"errors": []}
        response = self.client.get(self.url)
        self.assertRedirects(response, self.message_url, fetch_redirect_response=False)
        payment = Payment.objects.get(order=self.order)
        self.assertFalse(payment.is_finally)
        self.assertIsNone(payment.authority)

    @patch("apps.payments.views.gateway")
    def test_create_payment_with_gateway_error_list(self, gateway):
        # ZarinPal answers with "data": [] and an "errors" object when the request is rejected
        gateway.request_payment.return_value = {"data": [], "errors": {"code": -9}}
        response = self.client.get(self.url)
        self.assertRedirects(response, self.message_url, fetch_redirect_response=False)
        self.assertIsNone(Payment.objects.get(order=self.order).authority)

    @patch("apps.payments.views.gateway")
    def test_create_payment_without_authority(self, gateway):
        gateway.request_payment.return_value = {"data": {"code": 100}, "errors": []}
        response = self.client.get(self.url)
        self.assertRedirects(response, self.message_url, fetch_redirect_response=False)
        self.assertIsNone(Payment.objects.get(order=self.order).authority)

    @patch("apps.payments.views.gateway")
    def test_create_payment_gateway_exception(self, gateway):
        gateway.request_payment.side_effect = Exception("ZarinPal connection failed")
        response = self.client.get(self.url)
        self.assertRedirects(response, self.message_url, fetch_redirect_response=False)
        self.assertFalse(Payment.objects.get(order=self.order).is_finally)

    @patch("apps.payments.views.gateway")
    def test_order_without_address_goes_back_to_checkout(self, gateway):
        self.customer.address = ""
        self.customer.save()
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse("orders:checkout_order", kwargs={"order_id": self.order.id}),
            fetch_redirect_response=False,
        )
        gateway.request_payment.assert_not_called()
        self.assertEqual(Payment.objects.count(), 0)

    @patch("apps.payments.views.gateway")
    def test_already_paid_order_is_not_paid_again(self, gateway):
        self.order.is_finally = True
        self.order.save()
        response = self.client.get(self.url)
        self.assertRedirects(response, self.message_url, fetch_redirect_response=False)
        gateway.request_payment.assert_not_called()
        self.assertEqual(Payment.objects.count(), 0)

    @patch("apps.payments.views.gateway")
    def test_cannot_pay_another_users_order(self, gateway):
        other = CustomUser.objects.create_user(
            mobile_number="09121111111", password="12345678", name="O", family="U"
        )
        other.is_active = True
        other.save()
        self.client.force_login(other)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
        gateway.request_payment.assert_not_called()

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)


class ZarinPalVerifyViewTests(BaseOrderTest):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)
        self.verify_url = reverse("payments:zarinpal_verify")
        self.message_url = reverse("payments:show_verify_message")
        self.payment = Payment.objects.create(
            order=self.order,
            customer=self.customer,
            amount=self.order.get_order_total_price(),
            description="Test payment",
            authority=AUTHORITY,
        )

    def verify(self, **params):
        params.setdefault("Status", "OK")
        params.setdefault("Authority", AUTHORITY)
        return self.client.get(self.verify_url, params)

    @patch("apps.payments.views.gateway")
    def test_verify_success(self, gateway):
        gateway.verify_payment.return_value = {"data": {"code": 100, "ref_id": 123456789}, "errors": []}
        response = self.verify()
        self.assertRedirects(response, self.message_url, fetch_redirect_response=False)

        self.payment.refresh_from_db()
        self.order.refresh_from_db()
        self.assertTrue(self.payment.is_finally)
        self.assertEqual(self.payment.status_code, 100)
        self.assertEqual(self.payment.ref_id, "123456789")
        self.assertTrue(self.order.is_finally)
        self.assertEqual(self.order.order_state_id, OrderState.PAID_ID)

        # verified with the stored amount, converted to Rial
        gateway.verify_payment.assert_called_once_with(
            amount=self.payment.amount * 10, authority=AUTHORITY
        )

    @patch("apps.payments.views.gateway")
    def test_success_takes_goods_out_of_warehouse_once(self, gateway):
        gateway.verify_payment.return_value = {"data": {"code": 100, "ref_id": 1}, "errors": []}
        self.verify()
        self.assertEqual(Warehouse.objects.count(), 1)
        row = Warehouse.objects.get()
        self.assertEqual(row.product, self.product)
        self.assertEqual(row.qty, 2)
        self.assertEqual(row.warehouse_type_id, 2)  # output

        # opening the callback again must not deduct stock twice
        self.verify()
        self.assertEqual(Warehouse.objects.count(), 1)
        self.assertEqual(gateway.verify_payment.call_count, 1)

    @patch("apps.payments.views.gateway")
    def test_success_clears_shopping_cart(self, gateway):
        gateway.verify_payment.return_value = {"data": {"code": 100, "ref_id": 1}, "errors": []}
        session = self.client.session
        session["shop_cart"] = {"1": {"qty": 1, "price": 1, "final_price": 1}}
        session.save()
        self.verify()
        self.assertNotIn("shop_cart", self.client.session)

    @patch("apps.payments.views.gateway")
    def test_verify_already_verified_code_101(self, gateway):
        gateway.verify_payment.return_value = {"data": {"code": 101, "ref_id": 987654321}, "errors": []}
        response = self.verify()
        self.assertEqual(response.status_code, 302)
        self.payment.refresh_from_db()
        self.order.refresh_from_db()
        self.assertTrue(self.payment.is_finally)
        self.assertEqual(self.payment.status_code, 101)
        self.assertEqual(self.payment.ref_id, "987654321")
        self.assertTrue(self.order.is_finally)

    @patch("apps.payments.views.gateway")
    def test_verify_failed_code(self, gateway):
        gateway.verify_payment.return_value = {"data": {"code": -1}, "errors": []}
        self.verify()
        self.payment.refresh_from_db()
        self.order.refresh_from_db()
        self.assertFalse(self.payment.is_finally)
        self.assertEqual(self.payment.status_code, -1)
        self.assertIsNone(self.payment.ref_id)
        self.assertFalse(self.order.is_finally)
        self.assertEqual(Warehouse.objects.count(), 0)

    @patch("apps.payments.views.gateway")
    def test_verify_cancelled_by_user(self, gateway):
        response = self.verify(Status="NOK")
        self.assertRedirects(response, self.message_url, fetch_redirect_response=False)
        gateway.verify_payment.assert_not_called()
        self.payment.refresh_from_db()
        self.assertFalse(self.payment.is_finally)
        self.assertIsNone(self.payment.status_code)

    @patch("apps.payments.views.gateway")
    def test_verify_invalid_authority(self, gateway):
        response = self.verify(Authority="INVALID_AUTHORITY")
        self.assertEqual(response.status_code, 404)
        gateway.verify_payment.assert_not_called()

    @patch("apps.payments.views.gateway")
    def test_verify_payment_of_another_user(self, gateway):
        other = CustomUser.objects.create_user(
            mobile_number="09121111111", password="12345678", name="O", family="U"
        )
        other.is_active = True
        other.save()
        self.client.force_login(other)
        response = self.verify()
        self.assertEqual(response.status_code, 404)
        gateway.verify_payment.assert_not_called()

    @patch("apps.payments.views.gateway")
    def test_verify_without_data(self, gateway):
        gateway.verify_payment.return_value = {"errors": []}
        response = self.verify()
        self.assertEqual(response.status_code, 302)
        self.payment.refresh_from_db()
        self.assertFalse(self.payment.is_finally)
        self.assertIsNone(self.payment.ref_id)

    @patch("apps.payments.views.gateway")
    def test_verify_with_gateway_error_list(self, gateway):
        gateway.verify_payment.return_value = {"data": [], "errors": {"code": -50}}
        self.verify()
        self.payment.refresh_from_db()
        self.assertFalse(self.payment.is_finally)

    @patch("apps.payments.views.gateway")
    def test_verify_without_status_code(self, gateway):
        gateway.verify_payment.return_value = {"data": {}, "errors": []}
        self.verify()
        self.payment.refresh_from_db()
        self.assertFalse(self.payment.is_finally)

    @patch("apps.payments.views.gateway")
    def test_verify_without_ref_id(self, gateway):
        gateway.verify_payment.return_value = {"data": {"code": 100}, "errors": []}
        self.verify()
        self.payment.refresh_from_db()
        self.order.refresh_from_db()
        self.assertFalse(self.payment.is_finally)
        self.assertFalse(self.order.is_finally)
        self.assertEqual(Warehouse.objects.count(), 0)

    @patch("apps.payments.views.gateway")
    def test_verify_gateway_exception(self, gateway):
        gateway.verify_payment.side_effect = Exception("boom")
        response = self.verify()
        self.assertEqual(response.status_code, 302)
        self.payment.refresh_from_db()
        self.order.refresh_from_db()
        self.assertFalse(self.payment.is_finally)
        self.assertFalse(self.order.is_finally)


class ShowVerifyMessageTests(BaseOrderTest):
    def test_show_message(self):
        session = self.client.session
        session["payment_message"] = "پرداخت موفق بود"
        session.save()
        response = self.client.get(reverse("payments:show_verify_message"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "پرداخت موفق بود")

    def test_message_is_shown_only_once(self):
        session = self.client.session
        session["payment_message"] = "یک بار"
        session.save()
        self.client.get(reverse("payments:show_verify_message"))
        response = self.client.get(reverse("payments:show_verify_message"))
        self.assertContains(response, "نتیجه‌ای برای پرداخت وجود ندارد.")
