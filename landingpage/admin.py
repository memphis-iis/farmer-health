from django.contrib import admin
from .models import Landingpage


@admin.register(Landingpage)
class LandingpageAdmin(admin.ModelAdmin):
    list_display = ("text", "active", "start_date", "end_date")
    list_filter = ("active",)
    search_fields = ("text",)