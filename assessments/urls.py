from django.urls import path

from . import views

app_name = "assessments"

urlpatterns = [
    path("", views.start, name="start"),
    path("page/<int:page>/", views.question_page, name="page"),
    path("finish/", views.finish, name="finish"),
    path("done/", views.done, name="done"),
]
