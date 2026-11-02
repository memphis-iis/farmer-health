from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.shortcuts import render

from assessments.models import Assessment
from progress.services import ProgressService


@login_required
def dashboard(request):
    # Retrieve only this user's completed assessments.
    assessments = Assessment.objects.filter(
        user=request.user,
        completed_at__isnull=False,
    ).order_by("-completed_at")

    latest_assessment = assessments.first()

    # Calculate the average of saved assessment averages.
    average_score = assessments.aggregate(
        average=Avg("average_score")
    )["average"]

    # Reuse the existing ProgressService.
    service = ProgressService()
    current_weighted_score = service.current_weighted_score(request.user)
    trend_direction = service.trend_direction(request.user)

    trend_labels = {
        "IMPROVING": "Improving",
        "STABLE": "Stable",
        "DECLINED": "Worsening",
        "WORSENING": "Worsening",
    }

    # Prepare the 10 most recent assessments for the chart.
    chart_assessments = list(assessments[:10])
    chart_assessments.reverse()

    chart_data = []

    for assessment in chart_assessments:
        score = assessment.average_score

        if score is not None:
            chart_data.append({
                "score": score,
                "label": assessment.completed_at.strftime("%b %d"),
                "height": max(5, min(160, score * 32)),
            })

    context = {
        "assessments": assessments,
        "latest_assessment": latest_assessment,
        "average_score": average_score,
        "current_weighted_score": current_weighted_score,
        "wellbeing_tier": (
            latest_assessment.get_tier_display()
            if latest_assessment else None
        ),
        "trend_direction": trend_labels.get(
            trend_direction, "Not available"
        ),
        "has_assessments": assessments.exists(),
        "chart_data": chart_data,
    }

    return render(request, "progress/dashboard.html", context)
