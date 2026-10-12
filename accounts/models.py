from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

# Create your models here.
class User(AbstractUser):
    class NotifyChannel(models.TextChoices):
        EMAIL = "EMAIL", "EMAIL"
        SMS = "SMS", "SMS"
    
    email = models.EmailField(unique=True)

    phone_number = models.CharField(
    max_length=10,
    unique=True,
    validators=[RegexValidator(r"^\d{10}$", "Enter a 10-digit phone number.")],
    )

    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=64, blank=True)
    notifications_enabled = models.BooleanField(default=True)
    preferred_channel = models.CharField(
        max_length=5,
        choices=NotifyChannel.choices,
        default=NotifyChannel.EMAIL,

    )

    last_assessment_at = models.DateTimeField(null=True, blank=True)
    redcap_record_id = models.CharField(max_length=64, blank=True)

    REQUIRED_FIELDS = ["email", "phone_number"]

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)

