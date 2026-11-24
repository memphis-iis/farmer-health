from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
 
from assessments.models import Survey, Tier, TierMethod, TierRule
from itertools import count

_survey_counter = count(1)

 
def make_survey(**kwargs):
    """Create a Survey with a unique title so (title, version) never collides."""
    n = next(_survey_counter)
    defaults = {
        "title": f"Test Survey {n}",
        "version": 1,
        "scale_min": 1,
        "scale_max": 5,
        # add any other required Survey fields here
    }
    defaults.update(kwargs)
    return Survey.objects.create(**defaults)
 
 
class TierRuleTestBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.survey = make_survey()
        cls.tiers = [value for value, _ in Tier.choices]
 
    def build_rule(self, **overrides):
        data = {
            "survey": self.survey,
            "method": TierMethod.AVERAGE_CUTPOINT,
            "tier": self.tiers[0],
            "min_value": 1,
            "max_value": 3,
            "color_hex": "#00FF00",
            "label": "Low",
        }
        data.update(overrides)
        return TierRule(**data)
 
    def create_rule(self, **overrides):
        rule = self.build_rule(**overrides)
        rule.save()
        return rule
 
 
class TierRuleCleanTests(TierRuleTestBase):
    def test_str(self):
        rule = self.build_rule(label="Low", min_value=1, max_value=3)
        self.assertEqual(str(rule), f"Low ({self.tiers[0]}: 1-3)")
 
    def test_valid_rule_passes(self):
        self.build_rule().full_clean()
 
    def test_min_greater_than_max_raises(self):
        rule = self.build_rule(min_value=4, max_value=2)
        with self.assertRaisesMessage(
            ValidationError, "min_value must be less than or equal to max_value."
        ):
            rule.clean()
 
    def test_min_equal_to_max_is_valid(self):
        self.build_rule(min_value=3, max_value=3).clean()
 
    def test_out_of_scale_raises(self):
        for min_v, max_v in [(0, 3), (3, 6)]:  # below min, above max
            with self.subTest(min_value=min_v, max_value=max_v):
                rule = self.build_rule(min_value=min_v, max_value=max_v)
                with self.assertRaisesMessage(
                    ValidationError, "Range must fall within the survey scale (1-5)."
                ):
                    rule.clean()
 
    def test_uses_survey_specific_scale(self):
        survey = make_survey(scale_min=0, scale_max=10)
        self.build_rule(survey=survey, min_value=0, max_value=10).clean()
        with self.assertRaisesMessage(ValidationError, "(0-10)"):
            self.build_rule(survey=survey, min_value=0, max_value=11).clean()
 
    def test_clean_skips_scale_check_without_survey(self):
        TierRule(min_value=0, max_value=100).clean()
 
 
class TierRuleColorTests(TierRuleTestBase):
    def test_valid_colors(self):
        for color in ["#000000", "#FFFFFF", "#abcdef"]:
            with self.subTest(color=color):
                self.build_rule(color_hex=color).full_clean()
 
    def test_invalid_colors(self):
        for color in ["", "000000", "#00000", "#GGGGGG", "red"]:
            with self.subTest(color=color):
                with self.assertRaises(ValidationError) as ctx:
                    self.build_rule(color_hex=color).full_clean()
                self.assertIn("color_hex", ctx.exception.error_dict)
 
    def test_invalid_color_message(self):
        with self.assertRaises(ValidationError) as ctx:
            self.build_rule(color_hex="blue").full_clean()
        self.assertIn(
            "Enter a color in #RRGGBB format.", ctx.exception.message_dict["color_hex"]
        )
 
 
class TierRuleConstraintTests(TierRuleTestBase):
    def test_unique_survey_method_tier(self):
        self.create_rule()
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.create_rule(min_value=2, max_value=4, label="Dupe")
 
    def test_unique_scoped_to_survey_and_method(self):
        self.create_rule()
        self.create_rule(method=TierMethod.MAJORITY)  # different method
        self.create_rule(survey=make_survey())  # different survey
 
    def test_check_constraint_min_lte_max_db_level(self):
        # save() skips clean(), so this hits the DB constraint directly.
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.create_rule(min_value=5, max_value=1)
 
 
class TierRuleOrderingTests(TierRuleTestBase):
    def test_ordering_by_min_value(self):
        if len(self.tiers) < 3:
            self.skipTest("Need at least three tiers defined.")
        high = self.create_rule(tier=self.tiers[2], min_value=4, max_value=5, label="High")
        low = self.create_rule(tier=self.tiers[0], min_value=1, max_value=2, label="Low")
        mid = self.create_rule(tier=self.tiers[1], min_value=3, max_value=3, label="Mid")
        self.assertEqual(list(self.survey.tier_rules.all()), [low, mid, high])
 