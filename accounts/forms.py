from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import User


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "placeholder": "Enter your email address",
        }),
    )

    phone_number = forms.CharField(
        max_length=10,
        min_length=10,
        widget=forms.TextInput(attrs={
            "placeholder": "Enter your 10-digit phone number",
        }),
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "phone_number",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data["email"].lower()

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email
