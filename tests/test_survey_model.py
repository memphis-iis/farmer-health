from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from assessments.models import Survey


class SurveyModelTests(TestCase):
    def test_defaults(self):
        survey = Survey.objects.create(title="Farm Stress")
        self.assertEqual(survey.version, 1)
        self.assertEqual(survey.question_count, 59)
        self.assertEqual((survey.scale_min, survey.scale_max), (1, 5))
        self.assertTrue(survey.is_active)
        self.assertFalse(survey.is_validated)

    def test_scale_min_must_be_less_than_scale_max(self):
        survey = Survey(title="Bad", scale_min=5, scale_max=1)
        with self.assertRaises(ValidationError):
            survey.full_clean()

    def test_title_and_version_must_be_unique_together(self):
        Survey.objects.create(title="Farm Stress", version=1)
        with self.assertRaises(IntegrityError):
            Survey.objects.create(title="Farm Stress", version=1)

    def test_str(self):
        survey = Survey(title="Farm Stress", version=2)
        self.assertEqual(str(survey), "Farm Stress (v2)")
