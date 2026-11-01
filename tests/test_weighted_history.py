from datetime import date, timedelta

from django.test import SimpleTestCase

from progress.weighted_history import (
    IMPROVING, STABLE, WORSENING, WeightedHistoryModel,
)


class WeightedHistoryModelTests(SimpleTestCase):
    def setUp(self):
        self.model = WeightedHistoryModel(today_weight=0.5, half_life_days=90)
        self.today = date(2026, 10, 27)

    def test_decay_is_full_today_and_halves_each_half_life(self):
        self.assertEqual(self.model.decay_weight(0), 1.0)
        self.assertAlmostEqual(self.model.decay_weight(90), 0.5)

    def test_very_old_results_barely_count(self):
        self.assertLess(self.model.decay_weight(3 * 365), 0.001)

    def test_negative_age_is_rejected(self):
        with self.assertRaises(ValueError):
            self.model.decay_weight(-1)

    def test_recent_results_count_more_than_old_ones(self):
        past = [(self.today - timedelta(days=1), 5),
                (self.today - timedelta(days=365), 1)]
        self.assertGreater(self.model.weighted_history(past, self.today), 4.5)

    def test_empty_history_is_none(self):
        self.assertIsNone(self.model.weighted_history([], self.today))

    def test_blend_uses_only_today_when_there_is_no_history(self):
        self.assertEqual(self.model.blended_score(4, self.today, []), 4.0)

    def test_blend_mixes_today_and_history(self):
        past = [(self.today - timedelta(days=1), 2)]
        self.assertAlmostEqual(self.model.blended_score(4, self.today, past), 3.0)

    def test_seasonal_adjust_removes_the_expected_swing(self):
        model = WeightedHistoryModel(baselines={10: 4.0, 1: 2.0})
        self.assertAlmostEqual(model.seasonal_adjust(4.0, 10), 3.0)
        self.assertAlmostEqual(model.seasonal_adjust(2.0, 1), 3.0)

    def test_seasonal_adjust_without_baselines_changes_nothing(self):
        self.assertEqual(self.model.seasonal_adjust(3.5, 10), 3.5)

    def test_trend_worsening_when_scores_rise(self):
        self.assertEqual(self.model.trend_direction([1, 1, 2, 2, 3, 3, 3]), WORSENING)

    def test_trend_improving_when_scores_fall(self):
        self.assertEqual(self.model.trend_direction([4, 4, 4, 2, 2, 2]), IMPROVING)

    def test_trend_stable_when_scores_hold(self):
        self.assertEqual(self.model.trend_direction([3, 3, 3, 3, 3, 3]), STABLE)

    def test_trend_stable_with_too_little_history(self):
        self.assertEqual(self.model.trend_direction([3, 3, 3]), STABLE)
