from django.contrib.auth import get_user_model
from django.db.models import ProtectedError
from django.test import TestCase

from assessments.models import Assessment, Question, Response, Survey


class AssessmentModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="farmer1", email="f1@example.com",
            password="x", phone_number="9015550100",
        )
        self.survey = Survey.objects.create(title="Farmer Stress Survey")

    def make_question(self, order):
        return Question.objects.create(
            survey=self.survey, text=f"Question {order}", order=order
        )

    def test_assessment_saves_with_empty_results(self):
        assessment = Assessment.objects.create(user=self.user, survey=self.survey)
        self.assertIsNotNone(assessment.started_at)
        self.assertIsNone(assessment.completed_at)
        self.assertIsNone(assessment.average_score)
        self.assertEqual(assessment.tier, "")
        self.assertEqual(assessment.trend_direction, "")

    def test_calculate_average(self):
        assessment = Assessment.objects.create(user=self.user, survey=self.survey)
        for order, value in enumerate([1, 2, 3], start=1):
            Response.objects.create(
                assessment=assessment, question=self.make_question(order), value=value
            )
        self.assertEqual(assessment.calculate_average(), 2.0)

    def test_calculate_average_with_no_responses_is_none(self):
        assessment = Assessment.objects.create(user=self.user, survey=self.survey)
        self.assertIsNone(assessment.calculate_average())

    def test_survey_with_assessments_cannot_be_deleted(self):
        Assessment.objects.create(user=self.user, survey=self.survey)
        with self.assertRaises(ProtectedError):
            self.survey.delete()

    def test_deleting_user_deletes_assessments(self):
        Assessment.objects.create(user=self.user, survey=self.survey)
        self.user.delete()
        self.assertEqual(Assessment.objects.count(), 0)