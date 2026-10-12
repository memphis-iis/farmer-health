from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.utils import timezone

from accounts.models import RecoveryRequest


class RecoveryRequestTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="farmer1",
            email="farmer1@example.com",
            password="x",
            phone_number="9015550100",
        )

    def make_request(self, code="123456", minutes=15, used=False):
        return RecoveryRequest.objects.create(
            user=self.user,
            method=RecoveryRequest.Method.EMAIL,
            token_hash=make_password(code),
            expires_at=timezone.now() + timedelta(minutes=minutes),
            used=used,
        )

    def test_correct_code_passes(self):
        request = self.make_request()
        self.assertTrue(request.verify("123456"))

    def test_wrong_code_fails(self):
        request = self.make_request()
        self.assertFalse(request.verify("000000"))

    def test_expired_code_fails(self):
        request = self.make_request(minutes=-1)
        self.assertFalse(request.verify("123456"))

    def test_used_code_fails(self):
        request = self.make_request()
        self.assertTrue(request.verify("123456"))
        self.assertFalse(request.verify("123456"))

    def test_raw_code_is_never_stored(self):
        request = self.make_request(code="123456")
        self.assertNotEqual(request.token_hash, "123456")
        self.assertNotIn("123456", request.token_hash)