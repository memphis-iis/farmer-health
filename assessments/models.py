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

    def __str__(self):
        return f"{self.title} (v{self.version})"
