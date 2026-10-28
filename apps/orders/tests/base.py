from django.test import TestCase

from apps.accounts.models import Customer, CustomUser
from apps.orders.models import Order, OrderDetails, OrderState, PaymentType
from apps.products.models import Product


class BaseOrderTest(TestCase):
    """Shared fixtures: an active user (with address), a product and an unpaid order."""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            mobile_number="09120000000",
            email="user@example.com",
            name="Test",
            family="User",
            password="12345678",
        )
        self.user.is_active = True
        self.user.save()

        self.customer = Customer.objects.create(
            user=self.user,
            phone_number="02100000000",
            address="Tehran, Test street",
        )

        self.payment_type = PaymentType.objects.create(id=10, payment_title="Online")
        # ids chosen so they never collide with the well-known default rows
        self.order_state = OrderState.objects.create(id=10, order_state_title="Pending")

        self.product = Product.objects.create(
            product_name="Test product",
            image_name="images/product_group/test.jpg",
            price=100000,
            slug="test-product",
        )

        self.order = Order.objects.create(
            customer=self.customer,
            payment_type=self.payment_type,
            order_state=self.order_state,
        )
        OrderDetails.objects.create(
            order=self.order, product=self.product, qty=2, price=self.product.price
        )
