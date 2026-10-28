from django.contrib import admin
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import CustomUser


class AdminSmokeTests(TestCase):
    """Every registered admin page must load, and the admin must be in Persian."""

    def setUp(self):
        self.superuser = CustomUser.objects.create_superuser(
            mobile_number='09100000000',
            email='admin@example.com',
            name='مدیر',
            family='سایت',
            password='Str0ng-Pass!9',
        )
        self.client.force_login(self.superuser)

    def test_admin_index_is_persian(self):
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'مدیریت فروشگاه')
        self.assertContains(response, 'کاربران')
        self.assertContains(response, 'سفارش')
        self.assertNotContains(response, 'Custom users')

    def test_changelist_and_add_pages_load(self):
        for model in admin.site._registry:
            opts = model._meta
            for view_name, allowed in (('changelist', (200,)), ('add', (200, 403))):
                url = reverse(f'admin:{opts.app_label}_{opts.model_name}_{view_name}')
                with self.subTest(model=opts.label, view=view_name):
                    self.assertIn(self.client.get(url).status_code, allowed)

    def test_admin_form_errors_are_persian(self):
        response = self.client.post(reverse('admin:products_brand_add'), {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'لطفاً')
        self.assertNotContains(response, 'Please correct')
