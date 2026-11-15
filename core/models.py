from django.conf import settings
from django.db import models
from django.db.models import Q, F
from django.core.exceptions import ValidationError
from django.utils import timezone


class AuditLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=50)
    record_type = models.CharField(max_length=100)
    record_id = models.CharField(max_length=64)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp", "-id"]
        indexes = [models.Index(fields=["record_type", "record_id"])]

    def save(self, *args, **kwargs):
        """Audit entries are append-only: existing rows cannot be changed."""
        if not self._state.adding:
            raise ValueError("Audit log entries cannot be modified.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.action} {self.record_type} {self.record_id}"

class LandingMessage(models.Model):
    text = models.TextField()
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-start_date"]
        constraints = [
            models.CheckConstraint(
                condition=Q(end_date__isnull=True) | Q(end_date__gte=F("start_date")),
                name="landing_message_end_after_start",
            )
        ]

    def __str__(self):
        return self.text

    def clean(self):
        super().clean()
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError({
                "end_date": "End date cannot be earlier than start date."
            })

    @classmethod
    def get_current_message(cls):
        now = timezone.now()

        return cls.objects.filter(
            is_active=True,
            start_date__lte=now,
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=now)
        ).order_by("-start_date").first()
