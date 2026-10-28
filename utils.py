import os
import random
from uuid import uuid4

from django.conf import settings
from django.utils.deconstruct import deconstructible


def create_random_code(count):
    """Return a random integer with exactly ``count`` digits."""
    count -= 1
    return random.randint(10**count, 10 ** (count + 1) - 1)


def send_sms(mobile_number, message):
    """Send an SMS through Kavenegar.

    With no API key configured (local development) nothing is sent. The activation
    code is still saved in the database (``accounts_customuser.active_code``), so it
    can be read from there to test registration.
    """
    api_key = getattr(settings, "KAVENEGAR_API_KEY", "")
    if not api_key:
        return None

    from kavenegar import APIException, HTTPException, KavenegarAPI

    try:
        api = KavenegarAPI(api_key)
        params = {
            "sender": getattr(settings, "KAVENEGAR_SENDER", ""),
            "receptor": mobile_number,
            "message": message,
        }
        return api.sms_send(params)
    except (APIException, HTTPException) as error:
        print(f"SMS error: {error}")
        return None


@deconstructible
class FileUploud:
    """Builds unique upload paths: ``<dir>/<prefix>/<uuid><ext>``.

    Used directly as ``upload_to=FileUploud('images', 'brand')``. It is
    ``@deconstructible`` so migrations can serialize it and compare it
    reliably (otherwise ``makemigrations`` keeps generating new migrations).
    """

    def __init__(self, dir, prefix):
        self.dir = dir
        self.prefix = prefix

    def __call__(self, instance, filename):
        _, ext = os.path.splitext(filename)
        return f"{self.dir}/{self.prefix}/{uuid4()}{ext}"

    # kept for backward compatibility
    def upload_to(self, instance, filename):
        return self(instance, filename)


def price_by_delivery_tax(price, discount=0):
    """Return ``(final_price, delivery, tax)`` in Toman.

    * delivery is free for baskets above 500,000 Toman
    * tax is 9% of (price + delivery)
    * ``discount`` is a percentage applied to the grand total
    """
    delivery = 2500
    if price > 500000:
        delivery = 0

    tax = (price + delivery) * 0.09
    total = price + delivery + tax
    total = total - (total * (discount or 0) / 100)
    return int(total), delivery, int(tax)
