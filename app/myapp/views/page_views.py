from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from ..models import UserInfo, Education, WorkExperience, Skill, Project, Certification

# The modules in this file are imported in the __init__.py file (the one in the same folder)
# That is what makes these views available to the Django app
# Currently we are using * to import all modules which simplifies setup, but risks namespace pollution

# This file should contain simple views that render a page the user will navigate to
# Form views should be put in the form_views.py file
# More complex views should be put in their own file, dont forget to add a reference in __init__.py


def home(request):
    return render(request, 'frontend/index.html')

def sign_in(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'frontend/sign-in.html')

def sign_up(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'frontend/sign-up.html')

@login_required
def dashboard(request):
    """Renders the dashboard with user-related data."""
    user = request.user
    context = {
        'user_info': UserInfo.objects.filter(user=user).first(),
        'educations': Education.objects.filter(user=user),
        'work_experiences': WorkExperience.objects.filter(user=user),
        'skills': Skill.objects.filter(user=user),
        'projects': Project.objects.filter(user=user),
        'certifications': Certification.objects.filter(user=user),
    }
    return render(request, 'frontend/dashboard.html', context)

@login_required
def logout_view(request):
    """Logs out the user and redirects to the home page."""
    logout(request)
    return redirect('home')