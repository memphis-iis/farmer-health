from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class SeasonalProfile(models.Model):
    month = models.PositiveSmallIntegerField(unique=True, 
        validators=[MinValueValidator(1), MaxValueValidator(12)],
    )
    expected_baseline = models.FloatField(validators=[MinValueValidator(1.0), MaxValueValidator(5.0)])
    season_label = models.CharField()

    class Meta:
        ordering = ["month"]

    def __str__(self):
            return f"{self.month}: {self.season_label}"