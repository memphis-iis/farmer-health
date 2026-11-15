from django.test import TestCase

# Create your tests here.
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from assessments.models import Assessment, Survey


class ProgressDashboardTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username="dashboarduser",
            email="dashboard@example.com",
            password="testpassword123",
            phone_number="9015550101",
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="testpassword123",
            phone_number="9015550102",
        )

        self.survey = Survey.objects.create(
            title="Dashboard Test Survey"
        )

        self.url = reverse("progress:dashboard")

    def test_logged_out_user_is_redirected(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)

    def test_empty_state_for_user_without_assessments(self):
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["has_assessments"])
        self.assertContains(
            response,
            "You haven't completed any assessments yet."
        )

    def test_user_only_sees_their_own_assessments(self):
        Assessment.objects.create(
            user=self.user,
            survey=self.survey,
            completed_at=timezone.now(),
            average_score=4.0,
            weighted_score=3.8,
            tier="GREEN",
            trend_direction="STABLE",
        )

        Assessment.objects.create(
            user=self.other_user,
            survey=self.survey,
            completed_at=timezone.now(),
            average_score=2.0,
            weighted_score=2.2,
            tier="RED",
            trend_direction="DECLINED",
        )

        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["assessments"].count(),
            1
        )
        self.assertEqual(
            response.context["average_score"],
            4.0
        )
        self.assertEqual(
            len(response.context["chart_data"]),
            1
        )
