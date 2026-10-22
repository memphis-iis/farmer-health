from django.contrib import admin
from .models import Question, Survey

admin.site.register(Survey)
admin.site.register(Question)
