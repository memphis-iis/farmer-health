from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class AuthenticationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testfarmer",
            email="testfarmer@example.com",
            password="TestPassword123!",
            phone_number="1234567890",
        )

    def test_login_page_loads(self):
        response = self.client.get(reverse("accounts:login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome Back")

    def test_successful_login(self):
        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": "testfarmer",
                "password": "TestPassword123!",
            },
        )

        self.assertRedirects(response, reverse("accounts:home"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_with_incorrect_password(self):
        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": "testfarmer",
                "password": "WrongPassword123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_home_page_requires_login(self):
        response = self.client.get(reverse("accounts:home"))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:home')}",
        )

    def test_logout(self):
        self.client.login(
            username="testfarmer",
            password="TestPassword123!",
        )

        response = self.client.post(reverse("accounts:logout"))

        self.assertRedirects(response, reverse("accounts:login"))
        self.assertNotIn("_auth_user_id", self.client.session)
