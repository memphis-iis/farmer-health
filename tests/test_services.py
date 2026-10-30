from datetime import datetime
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from progress.services import ProgressService
from assessments.models import Survey, Assessment


class ProgressServiceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="tester", email="a@example.com", password="x"  
        )
        self.survey = Survey.objects.create(title="S")
        self.service = ProgressService()

    def _make(self, y, m, d, avg, weighted):
        return Assessment.objects.create(
            user=self.user, survey=self.survey,
            completed_at=timezone.make_aware(datetime(y, m, d, 12)),
            average_score=avg, weighted_score=weighted,
            tier="GREEN", trend_direction="STABLE",
        )

    def test_empty_history(self):
        self.assertEqual(self.service.weighted_trend(self.user), [])
        self.assertIsNone(self.service.current_weighted_score(self.user))

    def test_trend_is_oldest_first(self):
        self._make(2026, 10, 5, 3.0, 3.1)
        self._make(2026, 9, 5, 2.0, 2.1)
        scores = [p.weighted_score for p in self.service.weighted_trend(self.user)]
        self.assertEqual(scores, [2.1, 3.1])

    def test_monthly_average(self):
        self._make(2026, 10, 1, 2.0, 2.0)
        self._make(2026, 10, 20, 4.0, 4.0)
        self._make(2026, 9, 1, 1.0, 1.0)
        self.assertEqual(self.service.monthly_average(self.user, 2026, 10), 3.0)