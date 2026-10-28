from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, override_settings

from apps.payments import gateway


def fake_response(payload):
    response = MagicMock()
    response.json.return_value = payload
    return response


@override_settings(ZARINPAL_SANDBOX=True, ZARINPAL_MERCHANT_ID="11111111-1111-1111-1111-111111111111")
class GatewayTests(SimpleTestCase):
    @patch("apps.payments.gateway.requests.post")
    def test_request_payment_uses_sandbox_and_sends_expected_payload(self, post):
        post.return_value = fake_response({"data": {"authority": "A1"}, "errors": []})

        result = gateway.request_payment(
            amount=2000, callback_url="http://testserver/verify/", description="Order 1",
            mobile="09120000000", email="a@b.com",
        )

        self.assertEqual(result["data"]["authority"], "A1")
        url = post.call_args.args[0]
        body = post.call_args.kwargs["json"]
        self.assertEqual(url, "https://sandbox.zarinpal.com/pg/v4/payment/request.json")
        self.assertEqual(body["merchant_id"], "11111111-1111-1111-1111-111111111111")
        self.assertEqual(body["amount"], 2000)
        self.assertEqual(body["currency"], "IRR")
        self.assertEqual(body["callback_url"], "http://testserver/verify/")
        self.assertEqual(body["metadata"], {"mobile": "09120000000", "email": "a@b.com"})

    @patch("apps.payments.gateway.requests.post")
    def test_empty_contact_info_is_not_sent(self, post):
        post.return_value = fake_response({"data": {}, "errors": []})
        gateway.request_payment(amount=1, callback_url="http://x/", description="d")
        self.assertNotIn("metadata", post.call_args.kwargs["json"])

    @patch("apps.payments.gateway.requests.post")
    def test_verify_payment(self, post):
        post.return_value = fake_response({"data": {"code": 100, "ref_id": 5}, "errors": []})
        result = gateway.verify_payment(amount=2000, authority="A1")
        self.assertEqual(result["data"]["ref_id"], 5)
        self.assertEqual(post.call_args.args[0], "https://sandbox.zarinpal.com/pg/v4/payment/verify.json")
        self.assertEqual(post.call_args.kwargs["json"]["authority"], "A1")

    def test_payment_url(self):
        self.assertEqual(gateway.payment_url("A1"), "https://sandbox.zarinpal.com/pg/StartPay/A1")

    @override_settings(ZARINPAL_SANDBOX=False)
    def test_live_urls(self):
        self.assertEqual(gateway.payment_url("A1"), "https://payment.zarinpal.com/pg/StartPay/A1")
