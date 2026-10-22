from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import AuditLog


class AuditLogModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="farmer1",
            email="farmer1@example.com",
            password="test-pass-123",
            phone_number="9015550100",
        )

    def make_entry(self, **overrides):
        values = {
            "actor": self.user,
            "action": "READ",
            "record_type": "Assessment",
            "record_id": "42",
            "ip_address": "203.0.113.5",
        }
        values.update(overrides)
        return AuditLog.objects.create(**values)

    def test_timestamp_is_set_automatically(self):
        entry = self.make_entry()
        self.assertIsNotNone(entry.timestamp)

    def test_ip_address_is_optional(self):
        entry = self.make_entry(ip_address=None)
        self.assertIsNone(entry.ip_address)

    def test_entry_is_kept_with_no_actor_when_user_is_deleted(self):
        entry = self.make_entry()
        self.user.delete()
        entry.refresh_from_db()
        self.assertIsNone(entry.actor)
        self.assertEqual(entry.action, "READ")

    def test_existing_entry_cannot_be_edited(self):
        entry = self.make_entry()
        entry.action = "DELETE"
        with self.assertRaises(ValueError):
            entry.save()

    def test_newest_entries_come_first(self):
        first = self.make_entry(record_id="1")
        second = self.make_entry(record_id="2")
        self.assertEqual(list(AuditLog.objects.all()), [second, first])
