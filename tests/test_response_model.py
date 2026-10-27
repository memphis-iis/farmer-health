from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.test import TestCase

from assessments.models import Assessment, Question, Response, Survey


class ResponseModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="farmer1", email="f1@example.com",
            password="x", phone_number="9015550100",
        )
        self.survey = Survey.objects.create(title="Farmer Stress Survey")
        self.question = Question.objects.create(
            survey=self.survey, text="Question 1", order=1
        )
        self.assessment = Assessment.objects.create(user=self.user, survey=self.survey)

    def test_valid_response_saves(self):
        Response.objects.create(
            assessment=self.assessment, question=self.question, value=3
        )
        self.assertEqual(self.assessment.responses.count(), 1)

    def test_value_out_of_range_rejected(self):
        for bad in [0, 6]:
            response = Response(
                assessment=self.assessment, question=self.question, value=bad
            )
            with self.assertRaises(ValidationError):
                response.full_clean()

    def test_duplicate_answer_rejected(self):
        Response.objects.create(assessment=self.assessment, question=self.question, value=2)
        with self.assertRaises(IntegrityError):
            Response.objects.create(
                assessment=self.assessment, question=self.question, value=4
            )

    def test_deleting_assessment_deletes_responses(self):
        Response.objects.create(assessment=self.assessment, question=self.question, value=1)
        self.assessment.delete()
        self.assertEqual(Response.objects.count(), 0)

    def test_answered_question_cannot_be_deleted(self):
        Response.objects.create(assessment=self.assessment, question=self.question, value=5)
        with self.assertRaises(ProtectedError):
            self.question.delete()