from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("questionnaire/", include("assessments.urls")),
    path("progress/", include("progress.urls")),
]