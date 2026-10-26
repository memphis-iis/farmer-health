from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from progress.models import SeasonalProfile


class SeasonalProfileModelTests(TestCase):
    def test_valid_profile_saves(self):
        profile = SeasonalProfile.objects.create(
            month=10, expected_baseline=3.8, season_label="Harvest"
        )
        self.assertEqual(str(profile), "10: Harvest")

    def test_month_out_of_range_rejected(self):
        for bad in [0, 13]:
            profile = SeasonalProfile(
                month=bad, expected_baseline=3.0, season_label="Test"
            )
            with self.assertRaises(ValidationError):
                profile.full_clean()

    def test_baseline_out_of_range_rejected(self):
        for bad in [0.5, 5.5]:
            profile = SeasonalProfile(
                month=1, expected_baseline=bad, season_label="Test"
            )
            with self.assertRaises(ValidationError):
                profile.full_clean()

    def test_duplicate_month_rejected(self):
        SeasonalProfile.objects.create(
            month=4, expected_baseline=3.2, season_label="Planting"
        )
        with self.assertRaises(IntegrityError):
            SeasonalProfile.objects.create(
                month=4, expected_baseline=2.0, season_label="Duplicate"
            )

    def test_profiles_ordered_by_month(self):
        for month in [11, 2, 7]:
            SeasonalProfile.objects.create(
                month=month, expected_baseline=3.0, season_label="Test"
            )
        months = list(SeasonalProfile.objects.values_list("month", flat=True))
        self.assertEqual(months, [2, 7, 11])