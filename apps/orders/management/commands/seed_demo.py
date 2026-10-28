"""Fill the database with demo categories, brands and products.

    python manage.py seed_demo

Safe to run more than once: rows are matched by slug and updated, and stock is only added the
first time a product is created. Images are the sample images that ship with the repository
(`media/images/...`), so nothing needs to be uploaded.
"""
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import CustomUser
from apps.products.models import (
    Brand, Feature, FeatureValue, Product, ProductFeature, ProductGroup,
)
from apps.warehouses.models import Warehouse, WarehouseType

DEMO_USER_MOBILE = "09000000000"

BRANDS = [
    ("نوا", "nova"),
    ("آریا", "arya"),
    ("پارس", "pars"),
]

# slug, title, image, parent slug
GROUPS = [
    ("digital", "کالای دیجیتال", "images/categories/hardware.jpg", None),
    ("mobile", "موبایل", "images/categories/mobile.jpg", "digital"),
    ("laptop", "لپ‌تاپ", "images/categories/laptop.jpg", "digital"),
    ("camera", "دوربین", "images/categories/camera.png", "digital"),
    ("foodstuffs", "مواد غذایی", "images/categories/Foodstuffs.jpg", None),
    ("clothing", "پوشاک", "images/categories/clothing.png", None),
    ("tools", "ابزار و یراق", "images/categories/hardware.png", None),
]

# feature title -> (group slugs, values)
FEATURES = {
    "حافظه داخلی": (["mobile"], ["64 گیگابایت", "128 گیگابایت", "256 گیگابایت"]),
    "حافظه رم": (["laptop"], ["8 گیگابایت", "16 گیگابایت"]),
}

PRODUCT_IMAGES = [
    "images/products/p1.jpg",
    "images/products/p2.jpg",
    "images/products/p3.jpg",
    "images/products/p11.jpg",
]

# slug, name, price (toman), group slug, brand slug, qty in stock, (feature, value) or None
PRODUCTS = [
    ("mobile-a1", "گوشی موبایل نوا مدل A1", 12_500_000, "mobile", "nova", 15, ("حافظه داخلی", "128 گیگابایت")),
    ("mobile-a2", "گوشی موبایل نوا مدل A2", 18_900_000, "mobile", "nova", 8, ("حافظه داخلی", "256 گیگابایت")),
    ("mobile-b1", "گوشی موبایل آریا مدل B1", 7_800_000, "mobile", "arya", 20, ("حافظه داخلی", "64 گیگابایت")),
    ("laptop-p14", "لپ‌تاپ پارس مدل P14", 32_000_000, "laptop", "pars", 6, ("حافظه رم", "16 گیگابایت")),
    ("laptop-a15", "لپ‌تاپ آریا مدل A15", 24_500_000, "laptop", "arya", 9, ("حافظه رم", "8 گیگابایت")),
    ("camera-x10", "دوربین عکاسی نوا مدل X10", 21_000_000, "camera", "nova", 4, None),
    ("tea-500", "چای سیاه ممتاز ۵۰۰ گرمی", 185_000, "foodstuffs", "pars", 60, None),
    ("rice-5kg", "برنج ایرانی ۵ کیلوگرمی", 620_000, "foodstuffs", "pars", 40, None),
    ("honey-1kg", "عسل طبیعی ۱ کیلوگرمی", 450_000, "foodstuffs", "arya", 25, None),
    ("tshirt-m", "تی‌شرت نخی مردانه", 320_000, "clothing", "arya", 30, None),
    ("jacket-w", "کاپشن زمستانی زنانه", 1_850_000, "clothing", "nova", 12, None),
    ("drill-500", "دریل برقی ۵۰۰ وات", 2_400_000, "tools", "pars", 10, None),
]


class Command(BaseCommand):
    help = "Create demo categories, brands, products and stock so the shop is not empty."

    def handle(self, *args, **options):
        call_command("seed_data")  # payment type / order state / warehouse types

        self._warn_about_missing_images()

        with transaction.atomic():
            brands = self._brands()
            groups = self._groups()
            features = self._features(groups)
            created = self._products(brands, groups, features)

        self.stdout.write(self.style.SUCCESS(
            f"Demo data is ready: {len(groups)} categories, {len(brands)} brands, "
            f"{len(PRODUCTS)} products ({created} new)."
        ))

    # ------------------------------------------------------------------ helpers
    def _warn_about_missing_images(self):
        paths = {g[2] for g in GROUPS} | set(PRODUCT_IMAGES) | {"images/logo.png"}
        for rel in sorted(paths):
            if not (Path(settings.MEDIA_ROOT) / rel).exists():
                self.stdout.write(self.style.WARNING(f"Missing sample image: {rel}"))

    def _brands(self):
        brands = {}
        for title, slug in BRANDS:
            brand = Brand.objects.filter(slug=slug).first() or Brand(slug=slug)
            brand.brand_title = title
            brand.image_name = "images/logo.png"
            brand.save()
            brands[slug] = brand
        return brands

    def _groups(self):
        groups = {}
        for slug, title, image, parent_slug in GROUPS:  # parents are listed before their children
            group, _ = ProductGroup.objects.update_or_create(
                slug=slug,
                defaults={
                    "group_title": title,
                    "image_name": image,
                    "is_active": True,
                    "group_parent": groups.get(parent_slug),
                },
            )
            groups[slug] = group
        return groups

    def _features(self, groups):
        result = {}
        for title, (group_slugs, values) in FEATURES.items():
            feature = Feature.objects.filter(feature_name=title).first() or Feature.objects.create(
                feature_name=title
            )
            feature.product_group.add(*[groups[s] for s in group_slugs])
            result[title] = {
                value: FeatureValue.objects.get_or_create(feature=feature, value_title=value)[0]
                for value in values
            }
            result[title]["__feature__"] = feature
        return result

    def _warehouse_user(self):
        user = CustomUser.objects.filter(is_superuser=True).first()
        if user is None:
            # Inactive, password-less user that only owns the stock records.
            user = CustomUser.objects.filter(mobile_number=DEMO_USER_MOBILE).first()
        if user is None:
            user = CustomUser.objects.create_user(
                mobile_number=DEMO_USER_MOBILE, name="انبار", family="نمونه", password=None
            )
        return user

    def _products(self, brands, groups, features):
        user = self._warehouse_user()
        input_type = WarehouseType.get_input()
        created_count = 0

        for index, (slug, name, price, group_slug, brand_slug, qty, feature_value) in enumerate(PRODUCTS):
            product, created = Product.objects.update_or_create(
                slug=slug,
                defaults={
                    "product_name": name,
                    "price": price,
                    "brand": brands[brand_slug],
                    "image_name": PRODUCT_IMAGES[index % len(PRODUCT_IMAGES)],
                    "is_active": True,
                    "summery_description": f"{name} - کالای نمونه برای نمایش فروشگاه.",
                    "description": f"<p>{name}. این کالا فقط برای نمایش و آزمایش فروشگاه ساخته شده است.</p>",
                },
            )
            product.product_group.set([groups[group_slug]])

            if feature_value:
                title, value = feature_value
                feature = features[title]["__feature__"]
                ProductFeature.objects.update_or_create(
                    product=product,
                    feature=feature,
                    defaults={"value": value, "filter_value": features[title][value]},
                )

            if not product.warehouse_products.exists():  # add stock only once
                Warehouse.objects.create(
                    warehouse_type=input_type, user_registered=user,
                    product=product, qty=qty, price=price,
                )
            created_count += int(created)
        return created_count
