from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase


class UserModelTests(TestCase):
    def setUp(self):
        self.User = get_user_model()

    def test_create_user_with_profile_fields(self):
        user = self.User.objects.create_user(
            username="farmer1",
            email="farmer1@example.com",
            password="test-pass-123",
            phone_number="9015550100",
        )
        self.assertEqual(user.phone_number, "9015550100")
        self.assertFalse(user.mfa_enabled)
        self.assertTrue(user.notifications_enabled)
        self.assertEqual(user.preferred_channel, "EMAIL")
        self.assertIsNone(user.last_assessment_at)
        self.assertEqual(user.redcap_record_id, "")

    def test_email_is_lowercased_on_save(self):
        user = self.User.objects.create_user(
            username="farmer2",
            email="Farmer2@Example.COM",
            password="x",
            phone_number="9015550104",
        )
        user.refresh_from_db()
        self.assertEqual(user.email, "farmer2@example.com")

    def test_email_must_be_unique(self):
        self.User.objects.create_user(
            username="a", email="same@example.com",
            password="x", phone_number="9015550101",
        )
        with self.assertRaises(IntegrityError):
            self.User.objects.create_user(
                username="b", email="same@example.com",
                password="x", phone_number="9015550102",
            )

    def test_email_unique_ignores_case(self):
        self.User.objects.create_user(
            username="a", email="case@example.com",
            password="x", phone_number="9015550105",
        )
        with self.assertRaises(IntegrityError):
            self.User.objects.create_user(
                username="b", email="CASE@example.com",
                password="x", phone_number="9015550106",
            )

    def test_phone_must_be_unique(self):
        self.User.objects.create_user(
            username="a", email="a@example.com",
            password="x", phone_number="9015550103",
        )
        with self.assertRaises(IntegrityError):
            self.User.objects.create_user(
                username="b", email="b@example.com",
                password="x", phone_number="9015550103",
            )

    def test_phone_must_be_ten_digits(self):
        for bad in ["901555010", "901-555-0100", "90155501000"]:
            user = self.User(
                username="c", email="c@example.com", phone_number=bad
            )
            with self.assertRaises(ValidationError):
                user.full_clean()