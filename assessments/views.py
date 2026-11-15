from math import ceil

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from .models import Assessment, Response, Survey, TrendDirection

QUESTIONS_PER_PAGE = 8


def _active_survey():
    return Survey.objects.filter(is_active=True).order_by("-version", "-id").first()


def _current_assessment(user):
    """The user's unfinished assessment, or None. Never looks at anyone else's."""
    return user.assessments.filter(completed_at__isnull=True).order_by("-started_at").first()


def _page_count(questions):
    return max(1, ceil(len(questions) / QUESTIONS_PER_PAGE))


def _first_unanswered_page(assessment, questions):
    answered = set(assessment.responses.values_list("question_id", flat=True))
    for index, question in enumerate(questions):
        if question.id not in answered:
            return index // QUESTIONS_PER_PAGE + 1
    return _page_count(questions)


@login_required
def start(request):
    assessment = _current_assessment(request.user)
    if request.method == "POST":
        if assessment is None:
            survey = _active_survey()
            if survey is None or not survey.questions.exists():
                raise Http404("No survey is available.")
            assessment = Assessment.objects.create(
                user=request.user,
                survey=survey,
                trend_direction=TrendDirection.STABLE,
            )
        questions = assessment.survey.get_questions()
        return redirect("assessments:page", page=_first_unanswered_page(assessment, questions))
    return render(request, "assessments/start.html", {"resuming": assessment is not None})


@login_required
def question_page(request, page):
    assessment = _current_assessment(request.user)
    if assessment is None:
        return redirect("assessments:start")

    survey = assessment.survey
    questions = survey.get_questions()
    pages = _page_count(questions)
    if page < 1 or page > pages:
        raise Http404("No such page.")

    first = (page - 1) * QUESTIONS_PER_PAGE
    page_questions = questions[first:first + QUESTIONS_PER_PAGE]
    errors = {}

    if request.method == "POST":
        for question in page_questions:
            raw = request.POST.get(f"q{question.id}")
            if raw in (None, ""):
                continue
            try:
                value = int(raw)
            except ValueError:
                value = None
            if value is None or not survey.scale_min <= value <= survey.scale_max:
                errors[question.id] = "Please choose one of the answers."
                continue
            Response.objects.update_or_create(
                assessment=assessment, question=question, defaults={"value": value}
            )
        if not errors:
            nav = request.POST.get("nav")
            if nav == "back" and page > 1:
                return redirect("assessments:page", page=page - 1)
            if nav == "next":
                if page < pages:
                    return redirect("assessments:page", page=page + 1)
                return redirect("assessments:finish")
            return redirect("assessments:page", page=page)

    answers = dict(assessment.responses.values_list("question_id", "value"))
    show_missing = request.GET.get("missing") == "1"
    rows = []
    for q in page_questions:
        error = errors.get(q.id)
        if error is None and show_missing and q.id not in answers:
            error = "This question still needs an answer."
        rows.append({"question": q, "answer": answers.get(q.id), "error": error})
    return render(request, "assessments/page.html", {
        "rows": rows,
        "choices": range(survey.scale_min, survey.scale_max + 1),
        "page": page,
        "pages": pages,
        "is_first": page == 1,
        "is_last": page == pages,
        "answered": len(answers),
        "total": len(questions),
    })


@login_required
def finish(request):
    assessment = _current_assessment(request.user)
    if assessment is None:
        return redirect("assessments:start")

    questions = assessment.survey.get_questions()
    if not questions:
        raise Http404("This survey has no questions.")
    answered = assessment.responses.count()
    if answered < len(questions):
        missing = len(questions) - answered
        messages.warning(
            request,
            f"{missing} question{'s' if missing != 1 else ''} still need an answer "
            "before you can finish. They are marked below.",
        )
        page = _first_unanswered_page(assessment, questions)
        return redirect(reverse("assessments:page", kwargs={"page": page}) + "?missing=1")

    if request.method == "POST":
        with transaction.atomic():
            values = list(assessment.responses.values_list("value", flat=True))
            assessment.raw_total = sum(values)
            assessment.average_score = sum(values) / len(values)
            assessment.count_low_1_2 = sum(1 for v in values if v <= 2)
            assessment.count_mid_3 = sum(1 for v in values if v == 3)
            assessment.count_high_4_5 = sum(1 for v in values if v >= 4)
            assessment.completed_at = timezone.now()
            assessment.save()
        return redirect("assessments:done")
    return render(request, "assessments/finish.html", {"answered": answered})


@login_required
def done(request):
    return render(request, "assessments/done.html")
