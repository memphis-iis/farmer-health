
from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("assessment/", views.start_assessment, name="start_assessment"),
    path("resources/", views.resources, name="resources"),
    path("history/", views.history, name="history"),
]

