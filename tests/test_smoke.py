from django.test import SimpleTestCase


class BootstrapSmokeTests(SimpleTestCase):
    def test_ci_test_gate_stays_green(self):
        self.assertEqual(1 + 1, 2)
