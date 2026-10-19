from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from geopy.distance import geodesic


class Tier(models.TextChoices):
    GREEN = "GREEN", "Green"
    YELLOW = "YELLOW", "Yellow"
    RED = "RED", "Red"


class Resource(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    tier = models.CharField(max_length=10, choices=Tier.choices, default=Tier.GREEN)
    category = models.CharField(max_length=100, db_index=True)
    phone = models.CharField(max_length=32, blank=True)
    website = models.URLField(blank=True)
    address = models.CharField(max_length=500, blank=True)
    latitude = models.FloatField(null=True, blank=True, validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.FloatField(null=True, blank=True,validators=[MinValueValidator(-180), MaxValueValidator(180)])
    is_national = models.BooleanField(default=False)
    is_crisis = models.BooleanField(default=False)
 
    class Meta:
        ordering = ["tier", "name"]
        indexes = [
            models.Index(fields=["latitude", "longitude"]),
            models.Index(fields=["is_crisis", "is_national"]),
            models.Index(fields=["is_crisis", "tier"]),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        has_lat = self.latitude is not None
        has_lng = self.longitude is not None

        if has_lat != has_lng:
            raise ValidationError("Both latitude and longitude must be provided.")

        if not self.is_national and not (has_lat and has_lng):
            raise ValidationError("Provide coordinates for non-national resources.")
    
    def distance_miles(self, lat, lng):
        if self.latitude is None or self.longitude is None:
            return None
 
        return geodesic((lat, lng), (self.latitude, self.longitude)).miles
 
