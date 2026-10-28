from django.contrib.humanize.templatetags.humanize import intcomma
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import CustomUser
from apps.products.models import Product, ProductGroup
from apps.warehouses.models import Warehouse, WarehouseType


class PageSmokeTests(TestCase):
    """Render the public pages with real templates to catch broken queries/templates."""

    def setUp(self):
        self.group = ProductGroup.objects.create(
            group_title="Phones", image_name="g.jpg", slug="phones"
        )
        self.product = Product.objects.create(
            product_name="Phone one", image_name="p.jpg", price=1000, slug="phone-one"
        )
        self.product.product_group.add(self.group)
        self.hidden = Product.objects.create(
            product_name="Hidden", image_name="h.jpg", price=5, slug="hidden", is_active=False
        )

    def test_home_page(self):
        response = self.client.get(reverse("main:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Phone one")
        # the scripts behind cart / favourites / rating / comments must be loaded
        for script in ("js/number.js", "js/main.js", "js/myscript.js", "js/shop-actions.js"):
            self.assertContains(response, script)
        # the footer / slider must not be duplicated
        self.assertEqual(response.content.decode().count("<footer"), 1)
        self.assertEqual(response.content.decode().count("<header"), 1)

    def test_product_groups_page(self):
        response = self.client.get(reverse("products:product_groups"))
        self.assertEqual(response.status_code, 200)

    def test_products_of_group_page(self):
        response = self.client.get(reverse("products:products_of_group", kwargs={"slug": "phones"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Phone one")
        self.assertNotContains(response, "Hidden")

    def test_sorting_options(self):
        url = reverse("products:products_of_group", kwargs={"slug": "phones"})
        for sort_type in ("0", "1", "2"):
            with self.subTest(sort_type=sort_type):
                self.assertEqual(self.client.get(url, {"sort_type": sort_type}).status_code, 200)

    def test_invalid_filter_values_do_not_crash(self):
        url = reverse("products:products_of_group", kwargs={"slug": "phones"})
        response = self.client.get(url, {"brand": "abc", "feature": "x", "price": "abc", "page": "zzz"})
        self.assertEqual(response.status_code, 200)

    def test_price_filter(self):
        url = reverse("products:products_of_group", kwargs={"slug": "phones"})
        response = self.client.get(url, {"price": 10})
        self.assertNotContains(response, "Phone one")

    def test_unknown_group_is_404(self):
        response = self.client.get(reverse("products:products_of_group", kwargs={"slug": "nope"}))
        self.assertEqual(response.status_code, 404)

    def test_product_detail(self):
        response = self.client.get(self.product.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Phone one")

    def test_product_detail_has_working_widgets(self):
        response = self.client.get(self.product.get_absolute_url())
        self.assertContains(response, "<title>Phone one</title>", html=False)
        self.assertNotContains(response, "darsman")
        self.assertContains(response, 'data-action="add-to-cart"')
        self.assertContains(response, 'id="tab-reviews"')

    def test_inactive_product_detail_is_404(self):
        response = self.client.get(self.hidden.get_absolute_url())
        self.assertEqual(response.status_code, 404)

    def test_search(self):
        response = self.client.get(reverse("search:search_view"), {"q": "Phone"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Phone one")

    def test_empty_search_does_not_crash(self):
        self.assertEqual(self.client.get(reverse("search:search_view")).status_code, 200)

    def test_compare_list(self):
        response = self.client.get(
            reverse("products:add_to_compare_list"), {"productId": self.product.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get(reverse("products:status_of_compare_list")).content, b"1")
        self.assertEqual(self.client.get(reverse("products:compare_list")).status_code, 200)
        self.assertEqual(self.client.get(reverse("products:compare_table")).status_code, 200)

    def test_compare_rejects_invalid_product(self):
        response = self.client.get(reverse("products:add_to_compare_list"), {"productId": "abc"})
        self.assertEqual(response.status_code, 404)

    def test_product_prices_with_no_discount(self):
        self.assertEqual(self.product.get_price_by_discount(), 1000)
        self.assertEqual(self.product.get_number_in_warehouse(), 0)


class ProductCardButtonTests(TestCase):
    """The cart / favourite / compare buttons on product cards must call real JS functions."""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            mobile_number="09120000000", name="Ali", family="Test", password="Str0ng-Pass!9"
        )
        self.user.is_active = True
        self.user.save()
        self.product = Product.objects.create(
            product_name="Milk", image_name="m.jpg", price=15000, slug="milk"
        )
        Warehouse.objects.create(
            warehouse_type=WarehouseType.get_input(), user_registered=self.user,
            product=self.product, qty=5, price=10000,
        )

    def test_logged_in_user_sees_working_buttons(self):
        self.client.force_login(self.user)
        html = self.client.get(reverse("main:index")).content.decode()
        self.assertIn(f'data-action="add-to-cart" data-product-id="{self.product.id}"', html)
        self.assertIn(f'data-action="toggle-favorite" data-product-id="{self.product.id}"', html)
        self.assertIn(f'data-action="add-to-compare" data-product-id="{self.product.id}"', html)

    def test_anonymous_user_is_sent_to_login_for_favourites(self):
        html = self.client.get(reverse("main:index")).content.decode()
        self.assertIn(f'data-action="add-to-cart" data-product-id="{self.product.id}"', html)
        self.assertNotIn('data-action="toggle-favorite"', html)
        self.assertIn(reverse("accounts:login"), html)

    def test_out_of_stock_product_has_no_cart_button(self):
        Warehouse.objects.all().delete()
        html = self.client.get(reverse("main:index")).content.decode()
        self.assertNotIn('data-action="add-to-cart"', html)
        self.assertIn("ناموجود", html)


class NavigationAndHomeTests(TestCase):
    def setUp(self):
        self.parent = ProductGroup.objects.create(group_title="Dairy", image_name="d.jpg", slug="dairy")
        self.child = ProductGroup.objects.create(
            group_title="Cheese", image_name="c.jpg", slug="cheese", group_parent=self.parent
        )
        self.hidden = ProductGroup.objects.create(
            group_title="Hidden group", image_name="h.jpg", slug="hidden-group", is_active=False
        )

    def home(self):
        return self.client.get(reverse("main:index")).content.decode()

    def test_category_menu_is_built_from_the_database(self):
        html = self.home()
        self.assertIn("Dairy", html)
        self.assertIn("Cheese", html)
        self.assertIn(reverse("products:products_of_group", kwargs={"slug": "cheese"}), html)
        self.assertNotIn("Hidden group", html)

    def test_no_hard_coded_demo_categories_are_left(self):
        html = self.home()
        for demo_label in ("پوشاک", "لوازم جانبی", "لپ تاپ"):
            self.assertNotIn(demo_label, html)

    def test_menu_with_no_groups_says_so(self):
        ProductGroup.objects.all().delete()
        self.assertIn("هنوز دسته‌بندی‌ای ثبت نشده است", self.home())

    def test_there_is_no_dead_blog_link(self):
        self.assertNotIn("fa-newspaper", self.home())

    def test_compare_page_is_linked_from_the_header(self):
        html = self.home()
        self.assertIn(reverse("products:compare_list"), html)
        self.assertIn('id="compare_count"', html)

    def test_favourites_indicator_has_no_counter(self):
        html = self.home()
        start = html.index(reverse("csf:user_favorite"))
        end = html.index("</a>", start)
        self.assertNotIn("indicator__value", html[start:end])

    def test_slider_shows_a_default_banner_when_no_slides_exist(self):
        self.assertIn("hero-slider__slide", self.home())

    def test_products_page_sidebar_lists_the_categories(self):
        response = self.client.get(reverse("products:products_of_group", kwargs={"slug": "dairy"}))
        self.assertContains(response, "Cheese")

    def test_group_with_sub_groups_is_a_link_too(self):
        parent_url = reverse("products:products_of_group", kwargs={"slug": "dairy"})
        html = self.home()
        menu = html[html.index('class="megamenu"'):html.index("site__body")]
        self.assertIn(f'<a class="megamenu__heading" href="{parent_url}">Dairy</a>', menu)
        page = self.client.get(reverse("products:products_of_group", kwargs={"slug": "cheese"}))
        self.assertContains(page, f'href="{parent_url}"')

    def test_group_page_lists_products_of_its_sub_groups(self):
        product = Product.objects.create(product_name="Gouda", image_name="g.jpg", price=100, slug="gouda")
        product.product_group.add(self.child)
        parent_page = self.client.get(reverse("products:products_of_group", kwargs={"slug": "dairy"}))
        self.assertContains(parent_page, "Gouda")
        self.assertEqual(parent_page.context["product_count"], 1)
        child_page = self.client.get(reverse("products:products_of_group", kwargs={"slug": "cheese"}))
        self.assertContains(child_page, "Gouda")

    def test_product_in_parent_and_child_is_listed_once(self):
        product = Product.objects.create(product_name="Feta", image_name="f.jpg", price=100, slug="feta")
        product.product_group.add(self.parent, self.child)
        page = self.client.get(reverse("products:products_of_group", kwargs={"slug": "dairy"}))
        self.assertEqual(page.context["product_count"], 1)

    def test_groups_page_counts_products_of_sub_groups(self):
        product = Product.objects.create(product_name="Brie", image_name="b.jpg", price=100, slug="brie")
        product.product_group.add(self.child)
        page = self.client.get(reverse("products:product_groups"))
        counts = {g.slug: g.total_products for g in page.context["product_groups"]}
        self.assertEqual(counts["dairy"], 1)
        self.assertEqual(counts["cheese"], 1)

    def test_group_without_sub_groups_is_still_a_link(self):
        leaf_url = reverse("products:products_of_group", kwargs={"slug": "cheese"})
        self.assertIn(f'href="{leaf_url}"', self.home())


class ProductListPaginationTests(TestCase):
    def setUp(self):
        self.group = ProductGroup.objects.create(group_title="Spices", image_name="s.jpg", slug="spices")
        for i in range(25):
            product = Product.objects.create(
                product_name=f"Item {i:02d}", image_name="i.jpg", price=100 + i, slug=f"item-{i}"
            )
            product.product_group.add(self.group)
        self.url = reverse("products:products_of_group", kwargs={"slug": "spices"})

    def test_page_is_rendered_once(self):
        html = self.client.get(self.url).content.decode()
        self.assertEqual(html.count("page-header__title"), 1)
        self.assertEqual(html.count("products-list__item"), 10)

    def test_first_page_is_active_by_default(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context["page_obj"].number, 1)
        self.assertContains(response, "در حال نمایش 1 تا 10 از 25 محصول")

    def test_each_page_has_its_own_products(self):
        pages = [self.client.get(self.url, {"page": n}).context["page_obj"] for n in (1, 2, 3)]
        names = [[product.product_name for product in p.object_list] for p in pages]
        self.assertEqual([len(n) for n in names], [10, 10, 5])
        self.assertEqual(len(set().union(*[set(n) for n in names])), 25)

    def test_page_links_are_real_and_keep_filters(self):
        response = self.client.get(self.url, {"page": 2, "sort_type": "1"})
        self.assertContains(response, "sort_type=1&page=1")
        self.assertContains(response, "sort_type=1&page=3")
        self.assertNotContains(response, 'href="">')

    def test_per_page_changes_the_number_of_products(self):
        for per_page, expected in ((10, [10, 10, 5]), (20, [20, 5]), (40, [25])):
            with self.subTest(per_page=per_page):
                response = self.client.get(self.url, {"per_page": per_page})
                self.assertEqual(response.context["page_obj"].paginator.num_pages, len(expected))
                last = len(expected)
                lengths = [
                    len(self.client.get(self.url, {"per_page": per_page, "page": n}).context["page_obj"])
                    for n in range(1, last + 1)
                ]
                self.assertEqual(lengths, expected)

    def test_per_page_renders_that_many_products(self):
        html = self.client.get(self.url, {"per_page": 20}).content.decode()
        self.assertEqual(html.count("products-list__item"), 20)
        self.assertContains(self.client.get(self.url, {"per_page": 20}), "در حال نمایش 1 تا 20 از 25 محصول")

    def test_invalid_per_page_falls_back_to_default(self):
        for value in ("abc", "999", "0", "-5", "", "20.5"):
            with self.subTest(per_page=value):
                response = self.client.get(self.url, {"per_page": value})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.context["page_obj"]), 10)

    def test_per_page_select_marks_the_current_choice(self):
        html = self.client.get(self.url, {"per_page": 20}).content.decode()
        self.assertIn('<option value="20" selected>20</option>', html)
        self.assertNotIn('<option value="10" selected>', html)
        default_html = self.client.get(self.url).content.decode()
        self.assertIn('<option value="10" selected>10</option>', default_html)

    def test_page_links_keep_per_page_and_sort(self):
        response = self.client.get(self.url, {"per_page": 10, "sort_type": "2"})
        self.assertContains(response, "per_page=10&amp;sort_type=2&page=2")

    def test_single_page_has_no_pagination(self):
        Product.objects.filter(slug__startswith="item-").exclude(slug__in=["item-0", "item-1"]).delete()
        self.assertNotContains(self.client.get(self.url), "products-view__pagination")

    def test_group_title_is_separated_from_the_label(self):
        self.assertContains(self.client.get(self.url), "محصولات گروه Spices")


class LayoutTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            mobile_number="09120000000", name="Ali", family="Test", password="Str0ng-Pass!9"
        )
        self.user.is_active = True
        self.user.save()

    def home(self):
        return self.client.get(reverse("main:index")).content.decode()

    def test_there_is_no_top_bar(self):
        html = self.home()
        self.assertNotIn("topbar", html)
        self.assertNotIn("site-header__topbar", html)

    def test_header_has_a_logo(self):
        self.assertIn('class="site-logo"', self.home())

    def test_search_icon_was_removed_from_the_nav_bar(self):
        self.assertNotIn("drop-search", self.home())

    def test_nav_bar_links_to_about_and_contact(self):
        html = self.home()
        self.assertIn(reverse("main:about"), html)
        self.assertIn(reverse("main:contact"), html)

    def test_static_pages_exist(self):
        for name in ("main:about", "main:contact", "main:terms"):
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_account_menu_has_panel_and_logout_for_logged_in_users(self):
        self.client.force_login(self.user)
        html = self.home()
        self.assertIn(reverse("accounts:userpanel"), html)
        self.assertIn(reverse("accounts:logout"), html)

    def test_account_menu_for_visitors_has_login_and_register(self):
        html = self.home()
        self.assertIn(reverse("accounts:login"), html)
        self.assertIn(reverse("accounts:register"), html)

    def test_home_slider_is_visible_even_without_javascript(self):
        html = self.home()
        self.assertIn("data-hero-slider", html)
        self.assertIn("hero-slider__slide is-active", html)
        self.assertIn("js/hero-slider.js", html)


class DuplicateSlugTests(TestCase):
    def test_two_products_cannot_share_a_slug(self):
        from django.db import IntegrityError, transaction

        Product.objects.create(product_name="A", image_name="a.jpg", price=1, slug="same")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Product.objects.create(product_name="B", image_name="b.jpg", price=1, slug="same")

    def test_many_products_without_slug_are_allowed(self):
        Product.objects.create(product_name="A", image_name="a.jpg", price=1)
        Product.objects.create(product_name="B", image_name="b.jpg", price=1)
        self.assertEqual(Product.objects.count(), 2)


class CompareListTests(TestCase):
    def setUp(self):
        self.group = ProductGroup.objects.create(group_title="Dairy", image_name="g.jpg", slug="dairy")
        self.milk = Product.objects.create(product_name="Milk", image_name="m.jpg", price=15000, slug="milk")
        self.butter = Product.objects.create(product_name="Butter", image_name="b.jpg", price=6000, slug="butter")
        for product in (self.milk, self.butter):
            self.client.get(reverse("products:add_to_compare_list"), {"productId": product.id})

    def test_compare_page_shows_names_prices_and_stock(self):
        response = self.client.get(reverse("products:compare_list"))
        self.assertContains(response, "Milk")
        self.assertContains(response, "Butter")
        self.assertContains(response, intcomma(15000))
        self.assertContains(response, "ناموجود")
        self.assertContains(response, 'data-action="remove-from-compare"')

    def test_removing_a_product_updates_the_table(self):
        response = self.client.get(reverse("products:delete_from_compare_list"), {"productId": self.milk.id}, follow=True)
        self.assertNotContains(response, "Milk")
        self.assertContains(response, "Butter")

    def test_empty_compare_page_has_a_message(self):
        self.client.get(reverse("products:delete_from_compare_list"), {"productId": self.milk.id})
        self.client.get(reverse("products:delete_from_compare_list"), {"productId": self.butter.id})
        self.assertContains(self.client.get(reverse("products:compare_list")), "هنوز کالایی برای مقایسه")

