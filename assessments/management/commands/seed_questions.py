from django.core.management.base import BaseCommand
from django.db import transaction

from assessments.models import Question, Survey

SURVEY_TITLE = "Demo Survey"
SURVEY_VERSION = 1

# Draft questions for development only. They will be replaced by the
# validated set from the sponsor's independent study.
# Scale: 1 = not at all, 5 = very much. A higher number always means
# more difficulty, so a lower average is better.
DRAFT_QUESTIONS = [
    "How stressed or under pressure have you felt this week?",
    "How worried have you been about money or the farm's finances?",
    "How much trouble have you had sleeping?",
    "How tired or low on energy have you felt?",
    "How worried have you been about things outside your control, like weather, prices, or equipment?",
    "How overwhelmed have you felt by your workload?",
    "How down or discouraged have you felt?",
    "How anxious or on edge have you felt?",
    "How alone or cut off from other people have you felt?",
    "How hard has it been to focus or make decisions?",
]


class Command(BaseCommand):
    help = (
        "Load the ten draft questionnaire questions into the Demo Survey. "
        "Safe to run more than once: it updates in place and never duplicates."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        survey, created = Survey.objects.get_or_create(
            title=SURVEY_TITLE,
            version=SURVEY_VERSION,
            defaults={
                "source_citation": "These are drafted questions for development.",
                "is_validated": False,
                "scale_min": 1,
                "scale_max": 5,
                "is_active": True,
            },
        )
        survey.question_count = len(DRAFT_QUESTIONS)
        survey.save(update_fields=["question_count"])

        for order, text in enumerate(DRAFT_QUESTIONS, start=1):
            Question.objects.update_or_create(
                survey=survey,
                order=order,
                defaults={"text": text, "is_placeholder": True},
            )

        action = "Created" if created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f"{action} {survey} with {len(DRAFT_QUESTIONS)} draft questions."
            )
        )