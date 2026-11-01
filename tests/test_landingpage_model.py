
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from core.models import LandingMessage


class LandingMessageModelTest(TestCase):

    def setUp(self):
        self.now = timezone.now()

    def test_create_landing_message(self):
        """Test that a landing message can be created."""
        message = LandingMessage.objects.create(
            text="Welcome to the Farmer Wellbeing Dashboard!",
            is_active=True,
            start_date=self.now,
            end_date=self.now + timedelta(days=7),
        )

        self.assertEqual(
            message.text,
            "Welcome to the Farmer Wellbeing Dashboard!",
        )
        self.assertTrue(message.is_active)
        self.assertIsNotNone(message.start_date)
        self.assertIsNotNone(message.end_date)

    def test_landing_message_can_be_inactive(self):
        """Test that a landing message can be inactive."""
        message = LandingMessage.objects.create(
            text="Maintenance notice",
            is_active=False,
        )

        self.assertFalse(message.is_active)

    def test_end_date_can_be_empty(self):
        """Test that a message can have no expiration date."""
        message = LandingMessage.objects.create(
            text="Permanent welcome message",
            is_active=True,
            end_date=None,
        )

        self.assertIsNone(message.end_date)

    def test_future_message_is_not_returned(self):
        """A message that has not started should not be current."""
        LandingMessage.objects.create(
            text="Future message",
            is_active=True,
            start_date=self.now + timedelta(days=1),
        )

        self.assertIsNone(LandingMessage.get_current_message())

    def test_expired_message_is_not_returned(self):
        """An expired message should not be current."""
        LandingMessage.objects.create(
            text="Expired message",
            is_active=True,
            start_date=self.now - timedelta(days=3),
            end_date=self.now - timedelta(days=1),
        )

        self.assertIsNone(LandingMessage.get_current_message())

    def test_inactive_message_is_not_returned(self):
        """An inactive message should not be current."""
        LandingMessage.objects.create(
            text="Disabled message",
            is_active=False,
            start_date=self.now - timedelta(days=1),
        )

        self.assertIsNone(LandingMessage.get_current_message())

    def test_returns_none_when_no_message_is_active(self):
        """The helper should return None when no message qualifies."""
        self.assertIsNone(LandingMessage.get_current_message())

    def test_end_date_before_start_date_is_invalid(self):
        """An end date cannot be earlier than the start date."""
        message = LandingMessage(
            text="Invalid message",
            is_active=True,
            start_date=self.now,
            end_date=self.now - timedelta(days=1),
        )

        with self.assertRaises(ValidationError):
            message.full_clean()

    def test_helper_returns_current_message(self):
        """The helper should return a currently eligible message."""
        message = LandingMessage.objects.create(
            text="Current welcome message",
            is_active=True,
            start_date=self.now - timedelta(days=1),
            end_date=self.now + timedelta(days=7),
        )

        self.assertEqual(LandingMessage.get_current_message(), message)

    def test_helper_returns_message_with_latest_start_date(self):
        """The newest eligible message should be returned."""
        LandingMessage.objects.create(
            text="Older message",
            is_active=True,
            start_date=self.now - timedelta(days=3),
        )

        newer_message = LandingMessage.objects.create(
            text="Newer message",
            is_active=True,
            start_date=self.now - timedelta(days=1),
        )

        self.assertEqual(
            LandingMessage.get_current_message(),
            newer_message,
        )
