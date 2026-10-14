from django.core.exceptions import ValidationError
from django.test import TestCase

from assessments.models import Resource, Tier


class ResourceModelTests(TestCase):
    def test_national_resource_without_coordinates_is_valid(self):
        Resource(name="988", tier=Tier.RED, is_national=True, is_crisis=True).full_clean()

    def test_local_resource_requires_coordinates(self):
        with self.assertRaises(ValidationError):
            Resource(name="Clinic", tier=Tier.YELLOW).full_clean()

    def test_lat_and_lng_must_come_together(self):
        with self.assertRaises(ValidationError):
            Resource(name="X", tier=Tier.GREEN, latitude=32.3).full_clean()

    def test_coordinate_bounds(self):
        with self.assertRaises(ValidationError):
            Resource(name="X", tier=Tier.GREEN, latitude=95, longitude=0).full_clean()

    def test_distance_miles(self):
        r = Resource(name="Jackson", tier=Tier.GREEN, latitude=32.2988, longitude=-90.1848)
        self.assertAlmostEqual(r.distance_miles(32.2988, -90.1848), 0, places=3)
        
        self.assertAlmostEqual(r.distance_miles(29.9511, -90.0715), 162, delta=8)

    def test_distance_none_without_coordinates(self):
        r = Resource(name="988", tier=Tier.RED, is_national=True)
        self.assertIsNone(r.distance_miles(0, 0))