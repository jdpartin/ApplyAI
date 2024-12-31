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


# ------------------ API Views ------------------

@csrf_exempt
@login_required
def update_user_info(request):
    """Updates personal user information."""
    if request.method == 'POST':
        form = UserInfoForm(json.loads(request.body), instance=request.user.user_info)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': 'User info updated successfully.'})
        return JsonResponse({'error': form.errors}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


# ------------------ Education CRUD Views ------------------

@csrf_exempt
@login_required
def add_education(request):
    """Adds a new education record."""
    if request.method == 'POST':
        form = EducationForm(json.loads(request.body))
        if form.is_valid():
            education = form.save(commit=False)
            education.user = request.user
            education.save()
            return JsonResponse({'success': 'Education added successfully.'})
        return JsonResponse({'error': form.errors}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt
@login_required
def edit_education(request, id):
    """Edits an existing education record."""
    education = get_object_or_404(Education, id=id, user=request.user)
    if request.method == 'POST':
        form = EducationForm(json.loads(request.body), instance=education)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': 'Education updated successfully.'})
        return JsonResponse({'error': form.errors}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt
@login_required
def delete_education(request, id):
    """Deletes an education record."""
    education = get_object_or_404(Education, id=id, user=request.user)
    if request.method == 'DELETE':
        education.delete()
        return JsonResponse({'success': 'Education deleted successfully.'})
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


# ------------------ WorkExperience CRUD Views ------------------

@csrf_exempt
@login_required
def add_work_experience(request):
    """Adds a new work experience record."""
    if request.method == 'POST':
        form = WorkExperienceForm(json.loads(request.body))
        if form.is_valid():
            work_experience = form.save(commit=False)
            work_experience.user = request.user
            work_experience.save()
            return JsonResponse({'success': 'Work experience added successfully.'})
        return JsonResponse({'error': form.errors}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt
@login_required
def edit_work_experience(request, id):
    """Edits an existing work experience record."""
    work_experience = get_object_or_404(WorkExperience, id=id, user=request.user)
    if request.method == 'POST':
        form = WorkExperienceForm(json.loads(request.body), instance=work_experience)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': 'Work experience updated successfully.'})
        return JsonResponse({'error': form.errors}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt
@login_required
def delete_work_experience(request, id):
    """Deletes a work experience record."""
    work_experience = get_object_or_404(WorkExperience, id=id, user=request.user)
    if request.method == 'DELETE':
        work_experience.delete()
        return JsonResponse({'success': 'Work experience deleted successfully.'})
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


# ------------------ Skill CRUD Views ------------------

@csrf_exempt
@login_required
def add_skill(request):
    """Adds a new skill record."""
    if request.method == 'POST':
        form = SkillForm(json.loads(request.body))
        if form.is_valid():
            skill = form.save(commit=False)
            skill.user = request.user
            skill.save()
            return JsonResponse({'success': 'Skill added successfully.'})
        return JsonResponse({'error': form.errors}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt
@login_required
def edit_skill(request, id):
    """Edits an existing skill record."""
    skill = get_object_or_404(Skill, id=id, user=request.user)
    if request.method == 'POST':
        form = SkillForm(json.loads(request.body), instance=skill)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': 'Skill updated successfully.'})
        return JsonResponse({'error': form.errors}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt
@login_required
def delete_skill(request, id):
    """Deletes a skill record."""
    skill = get_object_or_404(Skill, id=id, user=request.user)
    if request.method == 'DELETE':
        skill.delete()
        return JsonResponse({'success': 'Skill deleted successfully.'})
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


# ------------------ Project CRUD Views ------------------

@csrf_exempt
@login_required
def add_project(request):
    """Adds a new project record."""
    if request.method == 'POST':
        form = ProjectForm(json.loads(request.body))
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            return JsonResponse({'success': 'Project added successfully.'})
        return JsonResponse({'error': form.errors}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt
@login_required
def edit_project(request, id):
    """Edits an existing project record."""
    project = get_object_or_404(Project, id=id, user=request.user)
    if request.method == 'POST':
        form = ProjectForm(json.loads(request.body), instance=project)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': 'Project updated successfully.'})
        return JsonResponse({'error': form.errors}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt
@login_required
def delete_project(request, id):
    """Deletes a project record."""
    project = get_object_or_404(Project, id=id, user=request.user)
    if request.method == 'DELETE':
        project.delete()
        return JsonResponse({'success': 'Project deleted successfully.'})
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


# ------------------ Certification CRUD Views ------------------

@csrf_exempt
@login_required
def add_certification(request):
    """Adds a new certification record."""
    if request.method == 'POST':
        form = CertificationForm(json.loads(request.body))
        if form.is_valid():
            certification = form.save(commit=False)
            certification.user = request.user
            certification.save()
            return JsonResponse({'success': 'Certification added successfully.'})
        return JsonResponse({'error': form.errors}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt
@login_required
def edit_certification(request, id):
    """Edits an existing certification record."""
    certification = get_object_or_404(Certification, id=id, user=request.user)
    if request.method == 'POST':
        form = CertificationForm(json.loads(request.body), instance=certification)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': 'Certification updated successfully.'})
        return JsonResponse({'error': form.errors}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt
@login_required
def delete_certification(request, id):
    """Deletes a certification record."""
    certification = get_object_or_404(Certification, id=id, user=request.user)
    if request.method == 'DELETE':
        certification.delete()
        return JsonResponse({'success': 'Certification deleted successfully.'})
    return JsonResponse({'error': 'Invalid request method.'}, status=405)
