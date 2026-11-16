from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.shortcuts import render, redirect

from accounts.forms import RegistrationForm


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("accounts:home")
    else:
        form = RegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def home(request):
    return render(request, "accounts/home.html")
