from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import CustomUser

MOBILE = "09123456789"
PASSWORD = "Str0ng-Pass!9"


class AuthBaseTest(TestCase):
    def setUp(self):
        # never send real SMS messages from tests
        patcher = patch("utils.send_sms")
        self.sms = patcher.start()
        self.addCleanup(patcher.stop)

    def create_active_user(self, mobile=MOBILE, password=PASSWORD):
        user = CustomUser.objects.create_user(
            mobile_number=mobile, name="Ali", family="Test", password=password
        )
        user.is_active = True
        user.save()
        return user

    def register(self, mobile=MOBILE, password=PASSWORD, password2=None):
        return self.client.post(reverse("accounts:register"), {
            "mobile_number": mobile,
            "password1": password,
            "password2": password2 or password,
        })


class RegisterTests(AuthBaseTest):
    def test_register_creates_inactive_user_and_sends_sms(self):
        response = self.register()
        self.assertRedirects(response, reverse("accounts:verify"), fetch_redirect_response=False)
        user = CustomUser.objects.get(mobile_number=MOBILE)
        self.assertFalse(user.is_active)
        self.assertTrue(user.check_password(PASSWORD))
        self.sms.assert_called_once()

    def test_register_password_mismatch(self):
        response = self.register(password2="other-password")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CustomUser.objects.filter(mobile_number=MOBILE).exists())

    def test_register_weak_password_is_rejected(self):
        response = self.register(password="12345678")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CustomUser.objects.filter(mobile_number=MOBILE).exists())

    def test_register_invalid_mobile_number(self):
        response = self.register(mobile="12345")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CustomUser.objects.count(), 0)

    def test_register_existing_active_user_is_rejected(self):
        self.create_active_user()
        response = self.register()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CustomUser.objects.count(), 1)

    def test_unverified_number_can_register_again(self):
        self.register()
        response = self.register()
        self.assertRedirects(response, reverse("accounts:verify"), fetch_redirect_response=False)
        self.assertEqual(CustomUser.objects.filter(mobile_number=MOBILE).count(), 1)


class VerifyTests(AuthBaseTest):
    def test_verify_with_correct_code_activates_user(self):
        self.register()
        code = self.client.session["user_session"]["active_code"]
        response = self.client.post(reverse("accounts:verify"), {"active_code": code})
        self.assertRedirects(response, reverse("accounts:login"), fetch_redirect_response=False)
        self.assertTrue(CustomUser.objects.get(mobile_number=MOBILE).is_active)

    def test_verify_with_wrong_code_keeps_user_inactive(self):
        self.register()
        response = self.client.post(reverse("accounts:verify"), {"active_code": "00000"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CustomUser.objects.get(mobile_number=MOBILE).is_active)

    def test_verify_page_without_session_redirects_to_register(self):
        response = self.client.get(reverse("accounts:verify"))
        self.assertRedirects(response, reverse("accounts:register"), fetch_redirect_response=False)


class LoginTests(AuthBaseTest):
    def test_login_success(self):
        user = self.create_active_user()
        response = self.client.post(
            reverse("accounts:login"), {"mobile_number": MOBILE, "password": PASSWORD}
        )
        self.assertRedirects(response, reverse("main:index"), fetch_redirect_response=False)
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.id)

    def test_login_wrong_password(self):
        self.create_active_user()
        response = self.client.post(
            reverse("accounts:login"), {"mobile_number": MOBILE, "password": "wrong"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_inactive_user_cannot_login(self):
        CustomUser.objects.create_user(mobile_number=MOBILE, password=PASSWORD)
        response = self.client.post(
            reverse("accounts:login"), {"mobile_number": MOBILE, "password": PASSWORD}
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_redirects_only_to_local_next_urls(self):
        self.create_active_user()
        response = self.client.post(
            reverse("accounts:login") + "?next=https://evil.example/",
            {"mobile_number": MOBILE, "password": PASSWORD},
        )
        self.assertRedirects(response, reverse("main:index"), fetch_redirect_response=False)

    def test_logout_keeps_shopping_cart(self):
        self.create_active_user()
        self.client.post(reverse("accounts:login"), {"mobile_number": MOBILE, "password": PASSWORD})
        session = self.client.session
        session["shop_cart"] = {"1": {"qty": 1, "price": 10, "final_price": 10}}
        session.save()
        self.client.get(reverse("accounts:logout"))
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertIn("shop_cart", self.client.session)


class ForgotPasswordTests(AuthBaseTest):
    def test_full_flow(self):
        self.create_active_user()
        new_password = "An0ther-Pass!7"

        response = self.client.post(reverse("accounts:remember_password"), {"mobile_number": MOBILE})
        self.assertRedirects(response, reverse("accounts:verify"), fetch_redirect_response=False)

        code = self.client.session["user_session"]["active_code"]
        response = self.client.post(reverse("accounts:verify"), {"active_code": code})
        self.assertRedirects(
            response, reverse("accounts:change_password"), fetch_redirect_response=False
        )

        response = self.client.post(reverse("accounts:change_password"), {
            "password1": new_password, "password2": new_password,
        })
        self.assertRedirects(response, reverse("accounts:login"), fetch_redirect_response=False)

        self.assertTrue(self.client.login(username=MOBILE, password=new_password))

    def test_change_password_requires_verified_mobile(self):
        self.create_active_user()
        response = self.client.get(reverse("accounts:change_password"))
        self.assertRedirects(
            response, reverse("accounts:remember_password"), fetch_redirect_response=False
        )

    def test_unknown_mobile_number(self):
        response = self.client.post(reverse("accounts:remember_password"), {"mobile_number": MOBILE})
        self.assertEqual(response.status_code, 200)
        self.sms.assert_not_called()


class ChangeMyPasswordTests(AuthBaseTest):
    URL = "accounts:change_my_password"

    def test_requires_login(self):
        response = self.client.get(reverse(self.URL))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_logged_in_user_can_change_password(self):
        user = self.create_active_user()
        self.client.force_login(user)
        response = self.client.post(reverse(self.URL), {
            "current_password": PASSWORD, "password1": "An0ther-Pass!7", "password2": "An0ther-Pass!7",
        })
        self.assertRedirects(response, reverse("accounts:userpanel"), fetch_redirect_response=False)
        user.refresh_from_db()
        self.assertTrue(user.check_password("An0ther-Pass!7"))
        # the session survives the change
        self.assertEqual(self.client.get(reverse("accounts:userpanel")).status_code, 200)

    def test_wrong_current_password_is_rejected(self):
        user = self.create_active_user()
        self.client.force_login(user)
        response = self.client.post(reverse(self.URL), {
            "current_password": "wrong", "password1": "An0ther-Pass!7", "password2": "An0ther-Pass!7",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "رمز عبور فعلی نادرست است")
        user.refresh_from_db()
        self.assertTrue(user.check_password(PASSWORD))

    def test_panel_sidebar_links_to_this_form(self):
        self.client.force_login(self.create_active_user())
        response = self.client.get(reverse("accounts:userpanel"))
        self.assertContains(response, reverse(self.URL))

