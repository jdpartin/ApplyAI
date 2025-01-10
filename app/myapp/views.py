from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from .models import UserInfo, Education, WorkExperience, Skill, Project, Certification
from .forms import UserInfoForm, EducationForm, WorkExperienceForm, SkillForm, ProjectForm, CertificationForm
from django.http import HttpResponse
from django.db import DatabaseError
import logging


from .forms import (
    EducationForm,
    WorkExperienceForm,
    SkillForm,
    ProjectForm,
    CertificationForm
)

from .models import (
    Education,
    WorkExperience,
    Skill,
    Project,
    Certification
)

# ------------------ General Views ------------------

def home(request):
    """Renders the home page."""
    return render(request, 'frontend/index.html')


# ------------------ Authentication Views ------------------

def sign_in(request):
    """Renders the sign-in page."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'frontend/sign-in.html')


def sign_up(request):
    """Renders the sign-up page."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'frontend/sign-up.html')


@csrf_exempt
def signinform(request):
    """Handles user sign-in."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return JsonResponse({'error': 'Email and password are required.'}, status=400)

            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                return JsonResponse({'success': 'User signed in successfully.', 'redirect': reverse('dashboard')}, status=200)

            return JsonResponse({'error': 'Invalid email or password.'}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)

    return JsonResponse({'error': 'Invalid request method. Use POST.'}, status=405)


@csrf_exempt
def signupform(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            confirm_password = data.get('confirmPassword')

            if not email or not password or not confirm_password:
                return JsonResponse({'error': 'All fields are required.'}, status=400)

            if password != confirm_password:
                return JsonResponse({'error': 'Passwords do not match.'}, status=400)

            try:
                validate_password(password)
            except ValidationError as e:
                return JsonResponse({'error': list(e)}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email is already registered.'}, status=400)

            # Create user
            user = User.objects.create_user(username=email, email=email, password=password)

            # Create default UserInfo
            UserInfo.objects.create(user=user)

            return JsonResponse({'success': 'User created successfully.', 'redirect': reverse('sign_in')}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)

    return JsonResponse({'error': 'Invalid request method. Use POST.'}, status=405)



@login_required
def dashboard(request):
    """
    Renders the dashboard with user information, education, work experience,
    skills, projects, and certifications.
    """
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


# Form Views

logger = logging.getLogger(__name__)

@login_required
def user_info_modal(request):
    if request.method == 'POST':
        user_info, created = UserInfo.objects.get_or_create(user=request.user)
        form = UserInfoForm(request.POST, instance=user_info)
        if form.is_valid():
            try:
                user_info = form.save()
                if not user_info.pk:  # Check if the primary key exists
                    raise ValueError("Failed to save user info; primary key is missing.")
                
                # Return the saved data back in the response
                return JsonResponse({
                    "message": "User info saved successfully!",
                    "status": "success",
                    "data": form.cleaned_data,  # Include the submitted form data
                }, status=200)
            except DatabaseError as e:
                logger.error(f"Database error during save: {e}")
                return JsonResponse({
                    "message": "An error occurred while saving user info.",
                    "status": "error"
                }, status=500)
            except Exception as e:
                logger.error(f"General error during save: {e}")
                return JsonResponse({
                    "message": "An unexpected error occurred.",
                    "status": "error"
                }, status=500)
        else:
            return JsonResponse({
                "errors": form.errors,  # Return form validation errors
                "status": "error"
            }, status=400)
    else:  # GET request
        return render(request, 'frontend/modals/user_info_modal.html')




@login_required
def education_modal(request):
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.user = request.user
            education.save()
            return JsonResponse({"message": "Education saved successfully!", "status": "success"}, status=200)
        else:
            return JsonResponse({"errors": form.errors, "status": "error"}, status=400)
    else:  # GET request
        return render(request, 'frontend/modals/education_modal.html')


@login_required
def work_experience_modal(request):
    if request.method == 'POST':
        form = WorkExperienceForm(request.POST)
        if form.is_valid():
            work_experience = form.save(commit=False)
            work_experience.user = request.user
            work_experience.save()
            return JsonResponse({"message": "Work experience saved successfully!", "status": "success"}, status=200)
        else:
            return JsonResponse({"errors": form.errors, "status": "error"}, status=400)
    else:  # GET request
        return render(request, 'frontend/modals/work_experience_modal.html')


@login_required
def skill_modal(request):
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.user = request.user
            skill.save()
            return JsonResponse({"message": "Skill saved successfully!", "status": "success"}, status=200)
        else:
            return JsonResponse({"errors": form.errors, "status": "error"}, status=400)
    else:  # GET request
        return render(request, 'frontend/modals/skill_modal.html')


@login_required
def project_modal(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            return JsonResponse({"message": "Project saved successfully!", "status": "success"}, status=200)
        else:
            return JsonResponse({"errors": form.errors, "status": "error"}, status=400)
    else:  # GET request
        return render(request, 'frontend/modals/project_modal.html')


@login_required
def certification_modal(request):
    if request.method == 'POST':
        form = CertificationForm(request.POST)
        if form.is_valid():
            certification = form.save(commit=False)
            certification.user = request.user
            certification.save()
            return JsonResponse({"message": "Certification saved successfully!", "status": "success"}, status=200)
        else:
            return JsonResponse({"errors": form.errors, "status": "error"}, status=400)
    else:  # GET request
        return render(request, 'frontend/modals/certification_modal.html')