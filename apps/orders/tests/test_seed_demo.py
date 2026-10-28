from django.core.management import call_command
from django.test import TestCase

from apps.products.models import Brand, Product, ProductGroup
from apps.warehouses.models import Warehouse


class SeedDemoTests(TestCase):
    def run_command(self):
        call_command("seed_demo", verbosity=0)

    def test_creates_categories_brands_and_products(self):
        self.run_command()
        self.assertEqual(ProductGroup.objects.filter(slug__in=["digital", "mobile", "laptop"]).count(), 3)
        self.assertEqual(ProductGroup.objects.get(slug="mobile").group_parent.slug, "digital")
        self.assertEqual(Brand.objects.count(), 3)
        self.assertEqual(Product.objects.count(), 12)

    def test_every_product_has_a_group_and_stock(self):
        self.run_command()
        for product in Product.objects.all():
            with self.subTest(product=product.slug):
                self.assertEqual(product.product_group.count(), 1)
                self.assertGreater(product.get_number_in_warehouse(), 0)

    def test_running_twice_does_not_duplicate_anything(self):
        self.run_command()
        stock = {p.slug: p.get_number_in_warehouse() for p in Product.objects.all()}
        self.run_command()
        self.assertEqual(Product.objects.count(), 12)
        self.assertEqual(ProductGroup.objects.count(), 7)
        self.assertEqual(Warehouse.objects.count(), 12)
        self.assertEqual({p.slug: p.get_number_in_warehouse() for p in Product.objects.all()}, stock)

    def test_demo_products_show_up_on_the_site(self):
        self.run_command()
        response = self.client.get("/products/products_of_group/mobile/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "گوشی موبایل نوا مدل A1")
