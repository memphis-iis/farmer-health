from django.contrib import admin
from .models import LandingMessage


@admin.register(LandingMessage)
class LandingMessageAdmin(admin.ModelAdmin):
    list_display = ("text", "active", "start_date", "end_date")
    list_filter = ("active",)
    search_fields = ("text",)