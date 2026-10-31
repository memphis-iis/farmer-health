from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from core.models import LandingMessage


class LandingMessageModelTest(TestCase):

    def test_create_landing_message(self):
        """Test that a landing message can be created."""
        now = timezone.now()

        message = LandingMessage.objects.create(
            text="Welcome to the Farmer Wellbeing Dashboard!",
            active=True,
            start_date=now,
            end_date=now + timedelta(days=7)
        )

        self.assertEqual(
            message.text,
            "Welcome to the Farmer Wellbeing Dashboard!"
        )
        self.assertTrue(message.active)
        self.assertIsNotNone(message.start_date)
        self.assertIsNotNone(message.end_date)

    def test_landing_message_can_be_inactive(self):
        """Test that a landing message can be inactive."""
        message = LandingMessage.objects.create(
            text="Maintenance notice",
            active=False
        )

        self.assertFalse(message.active)

    def test_end_date_can_be_empty(self):
        """Test that a message can have no expiration date."""
        message = LandingMessage.objects.create(
            text="Permanent welcome message",
            active=True,
            end_date=None
        )

        self.assertIsNone(message.end_date)
