from django.contrib import admin
from .models import AssessmentResult


@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    list_display = ("user", "score", "tier", "assessment_date")
    list_filter = ("tier", "assessment_date")
    search_fields = ("user__username", "user__email")
