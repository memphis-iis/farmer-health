from django.shortcuts import render


def dashboard(request):
    return render(request, "dashboard.html")


def start_assessment(request):
    return render(request, "assessment.html", {
        "title": "Start Assessment",
        "message": "Your wellbeing questionnaire will appear here."
    })


def resources(request):
    return render(request, "resources.html", {
        "title": "Resources",
        "message": "Wellbeing support resources will appear here."
    })


def history(request):
    return render(request, "history.html", {
        "title": "History & Progress",
        "message": "Your previous assessment results and progress chart will appear here."
    })
