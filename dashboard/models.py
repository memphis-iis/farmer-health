
from django.conf import settings
from django.db import models


class AssessmentResult(models.Model):
    TIER_CHOICES = [
        ("Tier 1", "Tier 1"),
        ("Tier 2", "Tier 2"),
        ("Tier 3", "Tier 3"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assessment_results"
    )

    score = models.PositiveIntegerField()
    tier = models.CharField(
        max_length=10,
        choices=TIER_CHOICES
    )
    assessment_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-assessment_date"]

    def __str__(self):
        return f"{self.user} - {self.score} - {self.tier}"
