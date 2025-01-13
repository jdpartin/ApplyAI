from .models import UserInfo, Education, WorkExperience, Skill, Project, Certification
from .forms import UserInfoForm, EducationForm, WorkExperienceForm, SkillForm, ProjectForm, CertificationForm
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.db import DatabaseError
from django.urls import reverse
import logging
import json


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
            # Save the UserInfo model
            user_info = form.save()

            # Update the User model fields
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')

            if email:
                request.user.email = email
            if first_name:
                request.user.first_name = first_name
            if last_name:
                request.user.last_name = last_name
            request.user.save()

            # Return success response
            return JsonResponse({
                "message": "User info saved successfully!",
                "status": "success",
                "data": {
                    **form.cleaned_data,
                    "email": request.user.email,
                    "first_name": request.user.first_name,
                    "last_name": request.user.last_name,
                }
            }, status=200)

        # Return validation errors
        return JsonResponse({
            "errors": form.errors,
            "status": "error"
        }, status=400)

    # Handle GET requests
    return render(request, 'frontend/modals/user_info_modal.html')


@login_required
def education_modal(request):
    # Extract `id` from query parameters
    education_id = request.GET.get('id') if request.method == 'GET' else request.POST.get('id')

    # Fetch the Education instance if `id` is provided
    education = None
    if education_id:
        education = get_object_or_404(Education, id=education_id, user=request.user)

    if request.method == 'POST':
        # Bind the form to the data and the instance (if any)
        form = EducationForm(request.POST, instance=education)
        if form.is_valid():
            education = form.save(commit=False)
            education.user = request.user  # Ensure the user is set
            education.save()
            return JsonResponse({"message": "Education saved successfully!", "status": "success"}, status=200)
        else:
            return JsonResponse({"errors": form.errors, "status": "error"}, status=400)

    else:  # GET request
        # Render the form, prefilled if editing
        return render(request, 'frontend/modals/education_modal.html', {'education': education})



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