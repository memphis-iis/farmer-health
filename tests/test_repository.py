from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from assessments.models import Assessment, Survey
from core.models import AuditLog
from core.repository import DataRepository, LocalRepository


class LocalRepositoryTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="farmer1", email="f1@example.com",
            password="x", phone_number="9015550100",
        )
        self.other = User.objects.create_user(
            username="farmer2", email="f2@example.com",
            password="x", phone_number="9015550101",
        )
        self.survey = Survey.objects.create(title="Demo Survey")
        self.repo = LocalRepository()

    def make_assessment(self, user, completed_days_ago=None):
        completed = None
        if completed_days_ago is not None:
            completed = timezone.now() - timedelta(days=completed_days_ago)
        return Assessment.objects.create(
            user=user, survey=self.survey,
            trend_direction="STABLE", completed_at=completed,
        )

    def test_interface_cannot_be_used_directly(self):
        with self.assertRaises(TypeError):
            DataRepository()

    def test_save_assessment_saves_and_logs_a_create(self):
        assessment = Assessment(user=self.user, survey=self.survey, trend_direction="STABLE")
        self.repo.save_assessment(assessment, actor=self.user, ip_address="203.0.113.5")
        entry = AuditLog.objects.get()
        self.assertIsNotNone(assessment.pk)
        self.assertEqual(entry.action, "CREATE")
        self.assertEqual(entry.record_type, "Assessment")
        self.assertEqual(entry.record_id, str(assessment.pk))
        self.assertEqual(entry.actor, self.user)
        self.assertEqual(entry.ip_address, "203.0.113.5")

    def test_saving_an_existing_assessment_logs_an_update(self):
        assessment = self.make_assessment(self.user)
        self.repo.save_assessment(assessment, actor=self.user)
        self.assertEqual(AuditLog.objects.get().action, "UPDATE")

    def test_assessment_is_not_saved_if_logging_fails(self):
        assessment = Assessment(user=self.user, survey=self.survey, trend_direction="STABLE")
        with patch.object(LocalRepository, "_log", side_effect=RuntimeError("boom")):
            with self.assertRaises(RuntimeError):
                self.repo.save_assessment(assessment, actor=self.user)
        self.assertEqual(Assessment.objects.count(), 0)

    def test_save_user_logs_a_create(self):
        User = get_user_model()
        new_user = User(username="farmer3", email="f3@example.com", phone_number="9015550102")
        new_user.set_password("x")
        self.repo.save_user(new_user, actor=new_user)
        entry = AuditLog.objects.get()
        self.assertEqual(entry.action, "CREATE")
        self.assertEqual(entry.record_type, "User")
        self.assertEqual(entry.record_id, str(new_user.pk))

    def test_history_has_only_this_users_completed_assessments_oldest_first(self):
        newer = self.make_assessment(self.user, completed_days_ago=1)
        older = self.make_assessment(self.user, completed_days_ago=5)
        self.make_assessment(self.user)  # not completed
        self.make_assessment(self.other, completed_days_ago=2)  # someone else's
        history = self.repo.get_history(self.user, actor=self.user)
        self.assertEqual(history, [older, newer])

    def test_reading_history_is_logged_once(self):
        self.make_assessment(self.user, completed_days_ago=1)
        self.make_assessment(self.user, completed_days_ago=2)
        self.repo.get_history(self.user, actor=self.other)
        entry = AuditLog.objects.get()
        self.assertEqual(entry.action, "READ")
        self.assertEqual(entry.record_type, "AssessmentHistory")
        self.assertEqual(entry.record_id, str(self.user.pk))
        self.assertEqual(entry.actor, self.other)

    def test_history_is_empty_when_nothing_is_completed(self):
        self.assertEqual(self.repo.get_history(self.user, actor=self.user), [])
