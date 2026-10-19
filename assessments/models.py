from django.core.exceptions import ValidationError
from django.db import models


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