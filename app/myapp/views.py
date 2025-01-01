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

# ------------------ General Views ------------------

def home(request):
    """Renders the home page."""
    return render(request, 'frontend/index.html')


# ------------------ Authentication Views ------------------

def sign_in(request):
    """Renders the sign-in page."""
    return render(request, 'frontend/sign-in.html')


def sign_up(request):
    """Renders the sign-up page."""
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

# User Info Modal
@login_required
def user_info_modal(request):
    # Fetch the UserInfo instance for the signed-in user or create one
    user_info, created = UserInfo.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserInfoForm(request.POST, instance=user_info)
        if form.is_valid():
            # Save the form but explicitly set the user
            user_info = form.save(commit=False)
            user_info.user = request.user  # Ensure the user is the logged-in user
            user_info.save()
            return HttpResponse(status=200)  # HTTP 200 OK
    else:
        form = UserInfoForm(instance=user_info)

    return render(request, 'frontend/modals/user_info_modal.html', {'form': form})

# Education Modal
def education_modal(request):
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_url')
    else:
        form = EducationForm()

    return render(request, 'frontend/modals/education_modal.html', {'form': form})

# Work Experience Modal
def work_experience_modal(request):
    if request.method == 'POST':
        form = WorkExperienceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_url')
    else:
        form = WorkExperienceForm()

    return render(request, 'frontend/modals/work_experience_modal.html', {'form': form})

# Skill Modal
def skill_modal(request):
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_url')
    else:
        form = SkillForm()

    return render(request, 'frontend/modals/skill_modal.html', {'form': form})

# Project Modal
def project_modal(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_url')
    else:
        form = ProjectForm()

    return render(request, 'frontend/modals/project_modal.html', {'form': form})

# Certification Modal
def certification_modal(request):
    if request.method == 'POST':
        form = CertificationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_url')
    else:
        form = CertificationForm()

    return render(request, 'frontend/modals/certification_modal.html', {'form': form})
