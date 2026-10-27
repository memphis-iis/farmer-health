from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from django.db.models import Avg
from resources.models import Tier

class Survey(models.Model):
    title = models.CharField(max_length=200)
    source_citation = models.CharField(max_length=500, blank=True)
    version = models.PositiveIntegerField(default=1)
    is_validated = models.BooleanField(default=False)
    question_count = models.PositiveSmallIntegerField(default=59)
    scale_min = models.PositiveSmallIntegerField(default=1)
    scale_max = models.PositiveSmallIntegerField(default=5)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["title", "version"],
                name="unique_survey_title_version",
            )
        ]

    def clean(self):
        if self.scale_min >= self.scale_max:
            raise ValidationError("scale_min must be less than scale_max.")

    def get_questions(self):
        """Return this survey's questions in their fixed order."""
        return list(self.questions.order_by("order"))

    def __str__(self):
        return f"{self.title} (v{self.version})"


class Question(models.Model):
    survey = models.ForeignKey(
        Survey, on_delete=models.CASCADE, related_name="questions"
    )
    text = models.TextField()
    order = models.PositiveSmallIntegerField()
    is_placeholder = models.BooleanField(default=False)

    class Meta:
        ordering = ["survey", "order"]
        constraints = [
            models.UniqueConstraint(
                fields=["survey", "order"],
                name="unique_question_order_per_survey",
            )
        ]

    def __str__(self):
        return f"Q{self.order}: {self.text[:50]}"

class TrendDirection(models.TextChoices):
    IMPROVING = "IMPROVING", "Improving"
    STABLE = "STABLE", "Stable"
    DECLINED = "DECLINED", "Declined"

class Assessment(models.Model):
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assessments")
    survey = models.ForeignKey(Survey, on_delete=models.PROTECT, related_name="assessments")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    raw_total = models.PositiveSmallIntegerField(null=True, blank=True)
    average_score = models.FloatField(null=True, blank=True)
    count_low_1_2 = models.PositiveSmallIntegerField(null=True, blank=True)
    count_mid_3 = models.PositiveSmallIntegerField(null=True, blank=True)
    count_high_4_5 = models.PositiveSmallIntegerField(null=True, blank=True)
    tier = models.CharField(max_length=6, choices=Tier.choices, blank=True)
    weighted_score = models.FloatField(null=True, blank=True)
    trend_direction = models.CharField(max_length=9, choices=TrendDirection.choices)
    model_version = models.CharField(max_length=20, blank=True)
    redcap_record_id = models.CharField(max_length=64, blank=True)

    def calculate_average(self):
        return self.responses.aggregate(Avg("value"))["value__avg"]

    def __str__(self):
        return f"{self.user} – {self.started_at:%Y-%m-%d}"

class Response(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="responses")
    question = models.ForeignKey(Question, on_delete=models.PROTECT, related_name="responses")
    value = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=["assessment", "question"],
            name="one_response_per_question",
        )]