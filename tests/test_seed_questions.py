from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from assessments.management.commands.seed_questions import (
    DRAFT_QUESTIONS,
    SURVEY_TITLE,
    SURVEY_VERSION,
)
from assessments.models import Question, Survey


class SeedQuestionsTests(TestCase):
    def run_seed(self):
        call_command("seed_questions", stdout=StringIO())

    def get_survey(self):
        return Survey.objects.get(title=SURVEY_TITLE, version=SURVEY_VERSION)

    def test_creates_survey_with_ten_questions(self):
        self.run_seed()
        survey = self.get_survey()
        self.assertEqual(survey.questions.count(), 10)
        self.assertEqual(survey.question_count, 10)

    def test_questions_are_in_order(self):
        self.run_seed()
        texts = list(
            self.get_survey().questions.order_by("order").values_list("text", flat=True)
        )
        self.assertEqual(texts, DRAFT_QUESTIONS)

    def test_questions_are_marked_as_drafts(self):
        self.run_seed()
        survey = self.get_survey()
        self.assertFalse(survey.is_validated)
        self.assertFalse(survey.questions.filter(is_placeholder=False).exists())

    def test_running_twice_does_not_duplicate(self):
        self.run_seed()
        self.run_seed()
        self.assertEqual(
            Survey.objects.filter(title=SURVEY_TITLE, version=SURVEY_VERSION).count(), 1
        )
        self.assertEqual(Question.objects.count(), 10)

    def test_running_again_restores_edited_text(self):
        self.run_seed()
        question = Question.objects.get(survey=self.get_survey(), order=1)
        question.text = "Edited by hand"
        question.save()
        self.run_seed()
        question.refresh_from_db()
        self.assertEqual(question.text, DRAFT_QUESTIONS[0])