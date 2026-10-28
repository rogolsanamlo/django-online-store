from django.urls import reverse

from apps.orders.models import Order

from .base import BaseOrderTest


class ShopCartTests(BaseOrderTest):
    def test_add_to_cart(self):
        response = self.client.get(
            reverse("orders:add_to_shop_cart"),
            {"product_id": self.product.id, "qty": 3},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session["shop_cart"][str(self.product.id)]["qty"], 3)

    def test_status_of_cart(self):
        self.client.get(
            reverse("orders:add_to_shop_cart"),
            {"product_id": self.product.id, "qty": 1},
        )
        response = self.client.get(reverse("orders:status_of_shop_cart"))
        self.assertEqual(response.content, b"1")

    def test_create_order_requires_login(self):
        response = self.client.get(reverse("orders:create_order"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_create_order_with_empty_cart_goes_back_to_cart(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("orders:create_order"))
        self.assertRedirects(response, reverse("orders:shop_cart"), fetch_redirect_response=False)

    def test_create_order_from_cart(self):
        self.client.force_login(self.user)
        self.client.get(
            reverse("orders:add_to_shop_cart"),
            {"product_id": self.product.id, "qty": 2},
        )
        before = Order.objects.count()
        response = self.client.get(reverse("orders:create_order"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.count(), before + 1)
        new_order = Order.objects.latest("id")
        self.assertEqual(new_order.get_items_total_price(), 200000)

    def test_checkout_of_another_users_order_is_404(self):
        from apps.accounts.models import CustomUser

        other = CustomUser.objects.create_user(
            mobile_number="09121111111", password="12345678", name="O", family="U"
        )
        other.is_active = True
        other.save()
        self.client.force_login(other)
        response = self.client.get(
            reverse("orders:checkout_order", kwargs={"order_id": self.order.id})
        )
        self.assertEqual(response.status_code, 404)
