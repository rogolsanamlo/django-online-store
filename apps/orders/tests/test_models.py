from apps.orders.models import Order, OrderDetails
from apps.products.models import Product

from .base import BaseOrderTest


class OrderModelTests(BaseOrderTest):
    def test_items_total(self):
        self.assertEqual(self.order.get_items_total_price(), 200000)

    def test_total_price_includes_delivery_and_tax(self):
        # 200000 + 2500 delivery + 9% tax of (200000 + 2500)
        self.assertEqual(self.order.get_order_total_price(), 220725)

    def test_total_price_in_rial_is_ten_times_toman(self):
        self.assertEqual(
            self.order.get_order_total_price_rial(),
            self.order.get_order_total_price() * 10,
        )

    def test_delivery_is_free_above_500k(self):
        big_product = Product.objects.create(
            product_name="Big", image_name="x.jpg", price=600000, slug="big"
        )
        order = Order.objects.create(customer=self.customer)
        OrderDetails.objects.create(order=order, product=big_product, qty=1, price=600000)
        # 600000 + 9% tax, no delivery
        self.assertEqual(order.get_order_total_price(), 654000)

    def test_coupon_discount_is_applied_to_total(self):
        self.order.discount = 10
        self.order.save()
        self.assertEqual(self.order.get_order_total_price(), int(220725 - 220725 * 10 / 100))

    def test_price_is_frozen_in_order_details(self):
        self.product.price = 1
        self.product.save()
        self.assertEqual(self.order.get_items_total_price(), 200000)
