from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from assessments.models import Assessment, Question, Response, Survey


class QuestionnaireViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="farmer1", email="f1@example.com",
            password="test-pass-123", phone_number="9015550100",
        )
        self.other = User.objects.create_user(
            username="farmer2", email="f2@example.com",
            password="test-pass-123", phone_number="9015550101",
        )
        self.survey = Survey.objects.create(title="Demo Survey")
        self.questions = [
            Question.objects.create(survey=self.survey, text=f"Question {n}", order=n)
            for n in range(1, 11)
        ]

    def login(self):
        self.client.login(username="farmer1", password="test-pass-123")

    def answer_all(self, assessment, value=3):
        for question in self.questions:
            Response.objects.create(assessment=assessment, question=question, value=value)

    def test_pages_require_login(self):
        for name in ["start", "finish", "done"]:
            response = self.client.get(reverse(f"assessments:{name}"))
            self.assertEqual(response.status_code, 302)
            self.assertIn("login", response["Location"])
        response = self.client.get(reverse("assessments:page", kwargs={"page": 1}))
        self.assertEqual(response.status_code, 302)

    def test_start_page_shows_for_logged_in_user(self):
        self.login()
        response = self.client.get(reverse("assessments:start"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "988")

    def test_starting_creates_one_assessment_and_goes_to_page_one(self):
        self.login()
        response = self.client.post(reverse("assessments:start"))
        self.assertRedirects(response, reverse("assessments:page", kwargs={"page": 1}))
        self.assertEqual(Assessment.objects.filter(user=self.user).count(), 1)

    def test_starting_again_resumes_instead_of_creating_another(self):
        self.login()
        self.client.post(reverse("assessments:start"))
        self.client.post(reverse("assessments:start"))
        self.assertEqual(Assessment.objects.filter(user=self.user).count(), 1)

    def test_resume_goes_to_first_unanswered_page(self):
        self.login()
        self.client.post(reverse("assessments:start"))
        assessment = Assessment.objects.get(user=self.user)
        for question in self.questions[:8]:
            Response.objects.create(assessment=assessment, question=question, value=2)
        response = self.client.post(reverse("assessments:start"))
        self.assertRedirects(response, reverse("assessments:page", kwargs={"page": 2}))

    def test_start_without_a_survey_gives_404(self):
        Survey.objects.all().delete()
        self.login()
        response = self.client.post(reverse("assessments:start"))
        self.assertEqual(response.status_code, 404)

    def test_question_page_shows_first_eight_questions_in_order(self):
        self.login()
        self.client.post(reverse("assessments:start"))
        response = self.client.get(reverse("assessments:page", kwargs={"page": 1}))
        self.assertContains(response, "Question 1")
        self.assertContains(response, "Question 8")
        self.assertNotContains(response, "Question 9")

    def test_page_out_of_range_gives_404(self):
        self.login()
        self.client.post(reverse("assessments:start"))
        response = self.client.get(reverse("assessments:page", kwargs={"page": 99}))
        self.assertEqual(response.status_code, 404)

    def test_answers_are_saved_and_next_goes_to_the_next_page(self):
        self.login()
        self.client.post(reverse("assessments:start"))
        data = {f"q{q.id}": "4" for q in self.questions[:8]}
        data["nav"] = "next"
        response = self.client.post(reverse("assessments:page", kwargs={"page": 1}), data)
        self.assertRedirects(response, reverse("assessments:page", kwargs={"page": 2}))
        self.assertEqual(Response.objects.count(), 8)

    def test_changing_an_answer_updates_instead_of_adding(self):
        self.login()
        self.client.post(reverse("assessments:start"))
        url = reverse("assessments:page", kwargs={"page": 1})
        key = f"q{self.questions[0].id}"
        self.client.post(url, {key: "2", "nav": "save"})
        self.client.post(url, {key: "5", "nav": "save"})
        self.assertEqual(Response.objects.count(), 1)
        self.assertEqual(Response.objects.get().value, 5)

    def test_value_outside_the_scale_is_rejected(self):
        self.login()
        self.client.post(reverse("assessments:start"))
        url = reverse("assessments:page", kwargs={"page": 1})
        response = self.client.post(url, {f"q{self.questions[0].id}": "9", "nav": "next"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please choose one of the answers.")
        self.assertEqual(Response.objects.count(), 0)

    def test_a_question_from_another_page_is_ignored(self):
        self.login()
        self.client.post(reverse("assessments:start"))
        url = reverse("assessments:page", kwargs={"page": 1})
        self.client.post(url, {f"q{self.questions[9].id}": "3", "nav": "save"})
        self.assertEqual(Response.objects.count(), 0)

    def test_finishing_early_goes_back_to_the_first_unanswered_page(self):
        self.login()
        self.client.post(reverse("assessments:start"))
        assessment = Assessment.objects.get(user=self.user)
        for question in self.questions[:8]:
            Response.objects.create(assessment=assessment, question=question, value=3)
        response = self.client.get(reverse("assessments:finish"))
        self.assertRedirects(
            response, reverse("assessments:page", kwargs={"page": 2}) + "?missing=1"
        )

    def test_finishing_sets_the_totals_and_completes_the_assessment(self):
        self.login()
        self.client.post(reverse("assessments:start"))
        assessment = Assessment.objects.get(user=self.user)
        values = [1, 2, 3, 3, 4, 5, 5, 2, 1, 4]
        for question, value in zip(self.questions, values):
            Response.objects.create(assessment=assessment, question=question, value=value)
        response = self.client.post(reverse("assessments:finish"))
        self.assertRedirects(response, reverse("assessments:done"))
        assessment.refresh_from_db()
        self.assertIsNotNone(assessment.completed_at)
        self.assertEqual(assessment.raw_total, sum(values))
        self.assertAlmostEqual(assessment.average_score, sum(values) / 10)
        self.assertEqual(assessment.count_low_1_2, 4)
        self.assertEqual(assessment.count_mid_3, 2)
        self.assertEqual(assessment.count_high_4_5, 4)
        self.assertEqual(assessment.tier, "")

    def test_a_finished_assessment_is_not_resumed(self):
        self.login()
        self.client.post(reverse("assessments:start"))
        assessment = Assessment.objects.get(user=self.user)
        self.answer_all(assessment)
        self.client.post(reverse("assessments:finish"))
        self.client.post(reverse("assessments:start"))
        self.assertEqual(Assessment.objects.filter(user=self.user).count(), 2)

    def test_another_users_assessment_is_never_used(self):
        theirs = Assessment.objects.create(
            user=self.other, survey=self.survey, trend_direction="STABLE"
        )
        self.login()
        response = self.client.get(reverse("assessments:page", kwargs={"page": 1}))
        self.assertRedirects(response, reverse("assessments:start"))
        self.assertEqual(theirs.responses.count(), 0)

    def test_finishing_early_explains_what_is_missing(self):
        self.login()
        self.client.post(reverse("assessments:start"))
        response = self.client.get(reverse("assessments:finish"), follow=True)
        self.assertContains(response, "still need an answer")
        self.assertContains(response, "This question still needs an answer.")
