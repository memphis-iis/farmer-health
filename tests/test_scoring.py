from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from assessments.models import Assessment, Survey, TrendDirection
from progress.scoring import ScoringModel, SimpleAverageModel
from resources.models import Tier


class ScoringModelInterfaceTests(SimpleTestCase):
    def test_interface_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            ScoringModel()

    def test_subclass_missing_a_method_fails(self):
        class Incomplete(ScoringModel):  # has score, but no weighted_history
            def score(self, user, assessment):
                return None

        with self.assertRaises(TypeError):
            Incomplete()


class SimpleAverageMathTests(SimpleTestCase):
    def setUp(self):
        self.model = SimpleAverageModel()

    def test_mean(self):
        self.assertAlmostEqual(self.model._mean([2.0, 3.0, 4.0]), 3.0)
        self.assertEqual(self.model._mean([]), 0.0)

    def test_single_assessment_is_stable(self):
        self.assertEqual(self.model._trend([3.0]), TrendDirection.STABLE)

    def test_rising_score_is_declined(self):
        self.assertEqual(self.model._trend([2.0, 3.0]), TrendDirection.WORSENING)

    def test_falling_score_is_improving(self):
        self.assertEqual(self.model._trend([3.0, 2.0]), TrendDirection.IMPROVING)

    def test_small_change_is_stable(self):
        self.assertEqual(self.model._trend([2.0, 2.05]), TrendDirection.STABLE)


class SimpleAverageModelTests(TestCase):
    def setUp(self):
        User = get_user_model()
        # Copy how tests/test_assessment_model.py creates users if this differs
        self.user = User.objects.create_user(
            username="farmer",
            email="farmer@example.com",
            phone_number="9015550100",
            password="test-pass-123",
        )
        self.other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            phone_number="9015550101",
            password="test-pass-123",
        )
        self.survey = Survey.objects.create(title="Test survey")
        self.model = SimpleAverageModel()

    def make_assessment(self, user, days_ago, average, tier=Tier.GREEN):
        return Assessment.objects.create(
            user=user,
            survey=self.survey,
            completed_at=timezone.now() - timedelta(days=days_ago),
            average_score=average,
            tier=tier,
            trend_direction=TrendDirection.STABLE,
        )

    def test_score_with_history(self):
        self.make_assessment(self.user, days_ago=20, average=2.0)
        self.make_assessment(self.user, days_ago=10, average=3.0)
        today = self.make_assessment(self.user, days_ago=0, average=4.0, tier=Tier.RED)

        result = self.model.score(self.user, today)

        self.assertEqual(result.average_score, 4.0)
        self.assertEqual(result.tier, Tier.RED)
        self.assertAlmostEqual(result.weighted_score, 3.0)  # mean of 2, 3, 4
        self.assertEqual(result.trend_direction, TrendDirection.WORSENING)  # 4.0 vs 2.5

    def test_first_assessment(self):
        only = self.make_assessment(self.user, days_ago=0, average=2.5)
        result = self.model.score(self.user, only)
        self.assertAlmostEqual(result.weighted_score, 2.5)
        self.assertEqual(result.trend_direction, TrendDirection.STABLE)

    def test_other_users_history_is_ignored(self):
        self.make_assessment(self.other_user, days_ago=10, average=5.0)
        mine = self.make_assessment(self.user, days_ago=0, average=2.0)
        result = self.model.score(self.user, mine)
        self.assertAlmostEqual(result.weighted_score, 2.0)

    def test_wrong_user_raises(self):
        theirs = self.make_assessment(self.other_user, days_ago=0, average=3.0)
        with self.assertRaises(ValueError):
            self.model.score(self.user, theirs)

    def test_history_is_oldest_first_with_running_mean(self):
        self.make_assessment(self.user, days_ago=5, average=3.0)   # created first,
        self.make_assessment(self.user, days_ago=15, average=2.0)  # but older

        points = self.model.weighted_history(self.user)

        self.assertEqual([p.average_score for p in points], [2.0, 3.0])
        self.assertEqual([p.weighted_score for p in points], [2.0, 2.5])

    def test_no_assessments(self):
        self.assertEqual(self.model.weighted_history(self.user), [])

    def test_assessment_with_no_responses_raises(self):
        empty = self.make_assessment(self.user, days_ago=0, average=None)
        with self.assertRaises(ValueError):
            self.model.score(self.user, empty)