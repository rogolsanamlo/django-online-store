from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import CustomUser
from apps.comment_scoring_favorites.models import Comment, Favorite, Scoring
from apps.products.models import Product


class CsfBaseTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            mobile_number="09120000000", name="Ali", family="Test", password="Str0ng-Pass!9"
        )
        self.user.is_active = True
        self.user.save()
        self.product = Product.objects.create(
            product_name="Phone one", image_name="p.jpg", price=1000, slug="phone-one"
        )


class FavoriteTests(CsfBaseTest):
    def toggle(self):
        return self.client.post(reverse("csf:toggle_favorite"), {"productId": self.product.id})

    def test_first_click_adds_second_click_removes(self):
        self.client.force_login(self.user)
        first = self.toggle()
        self.assertEqual(first.status_code, 200)
        self.assertTrue(first.json()["favorite"])
        self.assertEqual(Favorite.objects.filter(favorite_user=self.user).count(), 1)

        second = self.toggle()
        self.assertFalse(second.json()["favorite"])
        self.assertEqual(Favorite.objects.count(), 0)

    def test_anonymous_gets_401_not_a_login_page(self):
        response = self.toggle()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(Favorite.objects.count(), 0)

    def test_toggle_requires_post(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("csf:toggle_favorite"), {"productId": self.product.id})
        self.assertEqual(response.status_code, 405)

    def test_unknown_product_is_404(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("csf:toggle_favorite"), {"productId": 99999})
        self.assertEqual(response.status_code, 404)

    def test_favorites_page_and_removal(self):
        self.client.force_login(self.user)
        self.toggle()
        page = self.client.get(reverse("csf:user_favorite"))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Phone one")
        self.client.post(reverse("csf:remove_from_favorite"), {"productId": self.product.id})
        self.assertEqual(Favorite.objects.count(), 0)


class ScoreTests(CsfBaseTest):
    def test_score_is_created_then_updated(self):
        self.client.force_login(self.user)
        url = reverse("csf:add_score")
        self.client.get(url, {"productId": self.product.id, "score": 3})
        self.client.get(url, {"productId": self.product.id, "score": 5})
        self.assertEqual(Scoring.objects.count(), 1)
        self.assertEqual(Scoring.objects.get().score, 5)

    def test_invalid_scores_are_rejected(self):
        self.client.force_login(self.user)
        url = reverse("csf:add_score")
        for bad in ("abc", "9", "-1"):
            with self.subTest(score=bad):
                response = self.client.get(url, {"productId": self.product.id, "score": bad})
                self.assertEqual(response.status_code, 400)
        self.assertEqual(Scoring.objects.count(), 0)

    def test_anonymous_cannot_score(self):
        response = self.client.get(reverse("csf:add_score"), {"productId": self.product.id, "score": 4})
        self.assertEqual(response.status_code, 401)


class CommentTests(CsfBaseTest):
    def test_comment_form_is_shown_to_logged_in_users(self):
        self.client.force_login(self.user)
        response = self.client.get(self.product.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="comment_text"')

    def test_comment_form_is_not_shown_to_anonymous_users(self):
        response = self.client.get(self.product.get_absolute_url())
        self.assertNotContains(response, 'name="comment_text"')

    def test_new_comment_waits_for_approval(self):
        self.client.force_login(self.user)
        url = reverse("csf:create_comment", kwargs={"slug": self.product.slug})
        response = self.client.post(url, {"comment_text": "عالی بود", "comment_id": ""})
        self.assertEqual(response.status_code, 302)
        comment = Comment.objects.get()
        self.assertEqual(comment.commenting_user, self.user)
        self.assertFalse(comment.is_active)
        self.assertNotContains(self.client.get(self.product.get_absolute_url()), "عالی بود")

        comment.is_active = True
        comment.save()
        self.assertContains(self.client.get(self.product.get_absolute_url()), "عالی بود")

    def test_anonymous_cannot_comment(self):
        url = reverse("csf:create_comment", kwargs={"slug": self.product.slug})
        response = self.client.post(url, {"comment_text": "x"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 0)
