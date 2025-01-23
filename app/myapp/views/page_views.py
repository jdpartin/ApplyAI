from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from myapp.models import UserInfo, Education, WorkExperience, Skill, Project, Certification


# This file is for views that render a frontend page


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