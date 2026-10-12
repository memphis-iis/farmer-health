from django.db import IntegrityError
from django.test import TestCase

from assessments.models import Question, Survey


class QuestionModelTests(TestCase):
    def setUp(self):
        self.survey = Survey.objects.create(title="Farm Stress")

    def test_is_placeholder_defaults_to_false(self):
        question = Question.objects.create(
            survey=self.survey, text="Sample question", order=1
        )
        self.assertFalse(question.is_placeholder)

    def test_order_must_be_unique_within_a_survey(self):
        Question.objects.create(survey=self.survey, text="First", order=1)
        with self.assertRaises(IntegrityError):
            Question.objects.create(survey=self.survey, text="Duplicate", order=1)

    def test_same_order_is_allowed_in_a_different_survey(self):
        other_survey = Survey.objects.create(title="Other", version=1)
        Question.objects.create(survey=self.survey, text="First", order=1)
        Question.objects.create(survey=other_survey, text="First", order=1)
        self.assertEqual(Question.objects.count(), 2)

    def test_get_questions_returns_questions_in_order(self):
        Question.objects.create(survey=self.survey, text="Second", order=2)
        Question.objects.create(survey=self.survey, text="First", order=1)
        texts = [question.text for question in self.survey.get_questions()]
        self.assertEqual(texts, ["First", "Second"])

    def test_deleting_a_survey_deletes_its_questions(self):
        Question.objects.create(survey=self.survey, text="First", order=1)
        self.survey.delete()
        self.assertEqual(Question.objects.count(), 0)
