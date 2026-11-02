from django.conf import settings
from django.db import models


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
