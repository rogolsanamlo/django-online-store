"""Minimal client for the ZarinPal REST API (v4).

Docs: https://docs.zarinpal.com/paymentGateway/
Amounts are in Rial. In sandbox mode any UUID works as the merchant id.
"""
import requests
from django.conf import settings

REQUEST_PATH = '/pg/v4/payment/request.json'
VERIFY_PATH = '/pg/v4/payment/verify.json'
START_PAY_PATH = '/pg/StartPay/'
TIMEOUT_SECONDS = 20


def _host():
    return 'https://sandbox.zarinpal.com' if settings.ZARINPAL_SANDBOX else 'https://payment.zarinpal.com'


def _post(path, payload):
    response = requests.post(
        _host() + path,
        json={'merchant_id': settings.ZARINPAL_MERCHANT_ID, **payload},
        headers={'accept': 'application/json', 'content-type': 'application/json'},
        timeout=TIMEOUT_SECONDS,
    )
    return response.json()


def request_payment(amount, callback_url, description, mobile='', email=''):
    """Ask ZarinPal for a payment ``authority``. Returns the decoded JSON response."""
    metadata = {key: value for key, value in (('mobile', mobile), ('email', email)) if value}
    payload = {
        'amount': amount,
        'currency': 'IRR',
        'callback_url': callback_url,
        'description': description,
    }
    if metadata:
        payload['metadata'] = metadata
    return _post(REQUEST_PATH, payload)


def payment_url(authority):
    """The gateway page the customer is redirected to."""
    return f'{_host()}{START_PAY_PATH}{authority}'


def verify_payment(amount, authority):
    """Verify a finished payment. Returns the decoded JSON response."""
    return _post(VERIFY_PATH, {'amount': amount, 'authority': authority})
