"""Data access for users and assessments. Every access is written to the audit log."""
from abc import ABC, abstractmethod

from django.db import transaction

from assessments.models import Assessment
from core.models import AuditLog


class DataRepository(ABC):
    """Interface for saving and reading user and assessment data.

    `actor` is who is doing the action (a User), or None for a system job.
    """

    @abstractmethod
    def save_user(self, user, actor, ip_address=None):
        """Save a user and record it in the audit log."""

    @abstractmethod
    def save_assessment(self, assessment, actor, ip_address=None):
        """Save an assessment and record it in the audit log."""

    @abstractmethod
    def get_history(self, user, actor, ip_address=None):
        """Return the user's completed assessments, oldest first."""


class LocalRepository(DataRepository):
    """Stores data in the Django database and logs every access."""

    def _log(self, actor, action, record_type, record_id, ip_address):
        AuditLog.objects.create(
            actor=actor,
            action=action,
            record_type=record_type,
            record_id=str(record_id),
            ip_address=ip_address,
        )

    def save_user(self, user, actor, ip_address=None):
        action = "UPDATE" if user.pk else "CREATE"
        with transaction.atomic():
            user.save()
            self._log(actor, action, "User", user.pk, ip_address)
        return user

    def save_assessment(self, assessment, actor, ip_address=None):
        action = "UPDATE" if assessment.pk else "CREATE"
        with transaction.atomic():
            assessment.save()
            self._log(actor, action, "Assessment", assessment.pk, ip_address)
        return assessment

    def get_history(self, user, actor, ip_address=None):
        with transaction.atomic():
            history = list(
                Assessment.objects.filter(user=user, completed_at__isnull=False)
                .order_by("completed_at", "id")
            )
            self._log(actor, "READ", "AssessmentHistory", user.pk, ip_address)
        return history
