from django.db import models
from django.utils import timezone


class LandingMessage(models.Model):
    text = models.TextField()
    active = models.BooleanField(default=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.text

    @classmethod
    def get_current_message(cls):
        """Return the most recent currently active landing message."""
        now = timezone.now()

        return cls.objects.filter(
            active=True,
            start_date__lte=now
        ).filter(
            models.Q(end_date__isnull=True) |
            models.Q(end_date__gte=now)
        ).order_by("-start_date").first()