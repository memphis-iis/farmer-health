from django.core.exceptions import ValidationError
from django.db import models
from geopy.distance import geodesic


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

class Tier(models.TextChoices):
    GREEN = "GREEN", "Green"
    YELLOW = "YELLOW", "Yellow"
    RED = "RED", "Red"


class Resource(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    tier = models.CharField(max_length=6, choices=Tier.choices)
    category = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    address = models.CharField(max_length=300, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_national = models.BooleanField(default=False)
    is_crisis = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]

    def clean(self):
        has_lat = self.latitude is not None
        has_lng = self.longitude is not None
        if has_lat != has_lng:
            raise ValidationError("Provide both latitude and longitude, or neither.")
        if has_lat and not (-90 <= self.latitude <= 90):
            raise ValidationError("latitude must be between -90 and 90.")
        if has_lng and not (-180 <= self.longitude <= 180):
            raise ValidationError("longitude must be between -180 and 180.")
        if not self.is_national and not has_lat:
            raise ValidationError("Non-national resources need latitude and longitude.")

    def distance_miles(self, lat, lng):
        if self.latitude is None or self.longitude is None:
            return None
        return geodesic((lat, lng), (self.latitude, self.longitude)).miles
 
    def __str__(self):
        return f"{self.name} ({self.tier})"