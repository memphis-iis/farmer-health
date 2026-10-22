from django.core.exceptions import ValidationError
from django.test import TestCase

from resources.models import Resource, Tier


class ResourceModelTests(TestCase):
    def test_national_resource_without_coordinates_is_valid(self):
        Resource(name="988", category="Crisis", tier=Tier.RED, is_national=True, is_crisis=True).full_clean()

    def test_local_resource_requires_coordinates(self):
        with self.assertRaises(ValidationError):
            Resource(name="Clinic", category="Crisis", tier=Tier.YELLOW).full_clean()

    def test_lat_and_lng_must_come_together(self):
        with self.assertRaises(ValidationError) as cm:
            Resource(name="X", category="Crisis", tier=Tier.GREEN, latitude=32.3).full_clean()
        self.assertIn("Both latitude and longitude must be provided.", cm.exception.messages)

    def test_coordinate_bounds(self):
        with self.assertRaises(ValidationError) as cm:
            Resource(name="X", category="Crisis", tier=Tier.GREEN, latitude=95, longitude=0).full_clean()
        self.assertIn("latitude", cm.exception.message_dict)

    def test_distance_miles(self):
        r = Resource(name="Memphis", category="Hotline", tier=Tier.GREEN, latitude=35.1495, longitude=-90.0490)
        self.assertAlmostEqual(r.distance_miles(35.1495, -90.0490), 0, places=3)

                # Coordinates input are for Miami, Florida (873 miles from Memphis)
        self.assertAlmostEqual(r.distance_miles(25.761681, -80.191788), 873, delta=8)

    def test_distance_none_without_coordinates(self):
        r = Resource(name="988", category="Crisis", tier=Tier.RED, is_national=True)
        self.assertIsNone(r.distance_miles(0, 0))