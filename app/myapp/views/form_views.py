from django.contrib.auth.decorators import login_required
from myapp.forms import UserInfoForm, EducationForm, WorkExperienceForm, SkillForm, ProjectForm, CertificationForm
from myapp.models import UserInfo, Education, WorkExperience, Skill, Project, Certification
from django.http import JsonResponse # For returning error messages
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
import json
from myapp.library.resume import add_or_update_resume
from myapp.library.cover_letter import add_or_update_cover_letter
from myapp.library.aiworkflows import ai_add_resume_workflow, ai_add_cover_letter_workflow
from myapp.models import Resume, ResumeWorkExperience, ResumeProject



# This file is for models that handle form rendering and submissions


# User Info

@login_required
def user_info_modal(request):
    if request.method == 'POST':
        user_info, created = UserInfo.objects.get_or_create(user=request.user)
        form = UserInfoForm(request.POST, instance=user_info)

        if form.is_valid():
            # Save User Info and update User model
            user_info = form.save()
            request.user.email = request.POST.get('email', request.user.email)
            request.user.first_name = request.POST.get('first_name', request.user.first_name)
            request.user.last_name = request.POST.get('last_name', request.user.last_name)
            request.user.save()

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

        return JsonResponse({"errors": form.errors, "status": "error"}, status=400)

    return render(request, 'frontend/modals/user_info_modal.html')


# Education

@login_required
def education_modal(request):
    """Handles Education modal form submission and rendering."""
    education_id = request.GET.get('id') if request.method == 'GET' else request.POST.get('id')
    education = get_object_or_404(Education, id=education_id, user=request.user) if education_id else None

    if request.method == 'POST':
        form = EducationForm(request.POST, instance=education)
        if form.is_valid():
            education = form.save(commit=False)
            education.user = request.user
            education.save()
            return JsonResponse({"message": "Education saved successfully!", "status": "success"}, status=200)

        return JsonResponse({"errors": form.errors, "status": "error"}, status=400)

    return render(request, 'frontend/modals/education_modal.html', {'education': education})


# Work Experience

@login_required
def work_experience_modal(request):
    """Handles Work Experience modal form submission and rendering."""
    work_experience_id = request.GET.get('id') if request.method == 'GET' else request.POST.get('id')
    work_experience = get_object_or_404(WorkExperience, id=work_experience_id, user=request.user) if work_experience_id else None

    if request.method == 'POST':
        form = WorkExperienceForm(request.POST, instance=work_experience)
        if form.is_valid():
            work_experience = form.save(commit=False)
            work_experience.user = request.user
            work_experience.save()
            return JsonResponse({"message": "Work experience saved successfully!", "status": "success"}, status=200)

        return JsonResponse({"errors": form.errors, "status": "error"}, status=400)

    return render(request, 'frontend/modals/work_experience_modal.html', {'work_experience': work_experience})


# Skill

@login_required
def skill_modal(request):
    """Handles Skill modal form submission and rendering."""
    skill_id = request.GET.get('id') if request.method == 'GET' else request.POST.get('id')
    skill = get_object_or_404(Skill, id=skill_id, user=request.user) if skill_id else None

    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.user = request.user
            skill.save()
            return JsonResponse({"message": "Skill saved successfully!", "status": "success"}, status=200)

        return JsonResponse({"errors": form.errors, "status": "error"}, status=400)

    return render(request, 'frontend/modals/skill_modal.html', {'skill': skill})


# Project

@login_required
def project_modal(request):
    """Handles Project modal form submission and rendering."""
    project_id = request.GET.get('id') if request.method == 'GET' else request.POST.get('id')
    project = get_object_or_404(Project, id=project_id, user=request.user) if project_id else None

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            return JsonResponse({"message": "Project saved successfully!", "status": "success"}, status=200)

        return JsonResponse({"errors": form.errors, "status": "error"}, status=400)

    return render(request, 'frontend/modals/project_modal.html', {'project': project})


# Certification

@login_required
def certification_modal(request):
    """Handles Certification modal form submission and rendering."""
    certification_id = request.GET.get('id') if request.method == 'GET' else request.POST.get('id')
    certification = get_object_or_404(Certification, id=certification_id, user=request.user) if certification_id else None

    if request.method == 'POST':
        form = CertificationForm(request.POST, instance=certification)
        if form.is_valid():
            certification = form.save(commit=False)
            certification.user = request.user
            certification.save()
            return JsonResponse({"message": "Certification saved successfully!", "status": "success"}, status=200)

        return JsonResponse({"errors": form.errors, "status": "error"}, status=400)

    return render(request, 'frontend/modals/certification_modal.html', {'certification': certification})


# Resume
@login_required
def resume_modal(request):
    print("Resume modal called")
    try:
        if request.method == 'POST':
            print("Processing POST request")
            return add_or_update_resume(request, request.POST.dict())

        resume = None
        work_experience_data = {}
        project_data = {}

        resume_id = request.GET.get('id')
        print(f"Resume ID from GET: {resume_id}")

        if resume_id and resume_id != 'undefined':
            try:
                resume_id = int(resume_id)
                print(f"Validated Resume ID: {resume_id}")

                resume = get_object_or_404(request.user.resumes, id=resume_id)
                print(f"Fetched Resume: {resume}")

                # Prepare tailored work experience data
                work_experience_data = {
                    rwe.workExperience.id: rwe.tailoredDescription  # Use the ID of the related WorkExperience
                    for rwe in ResumeWorkExperience.objects.filter(resume=resume)
                }
                print(f"Work Experience Data: {work_experience_data}")

                # Prepare tailored project data (if applicable)
                project_data = {
                    rp.project.id: rp.tailoredDescription  # Use the ID of the related Project
                    for rp in ResumeProject.objects.filter(resume=resume)
                }
                print(f"Project Data: {project_data}")
            except ValueError:
                print("Invalid Resume ID format in GET request.")
                return JsonResponse({'status': 'error', 'message': 'Invalid Resume ID.'}, status=400)
            except Exception as e:
                print(f"Error fetching resume or related data: {e}")
                return JsonResponse({'status': 'error', 'message': f"Error: {e}"}, status=500)
        else:
            print("No valid Resume ID provided, fetching non-tailored descriptions.")
            # Fetch non-tailored descriptions for work experiences and projects
            work_experience_data = {
                we.id: we.job_description
                for we in request.user.work_experiences.all()
            }
            print(f"Non-Tailored Work Experience Data: {work_experience_data}")

            project_data = {
                p.id: p.description
                for p in request.user.projects.all()
            }
            print(f"Non-Tailored Project Data: {project_data}")

        context = {
            'user': request.user,
            'resume': resume,
            'work_experience_data': work_experience_data,  # Pass tailored or non-tailored descriptions for work experiences
            'project_data': project_data,  # Pass tailored or non-tailored descriptions for projects
        }
        print(f"Context prepared: {context}")
        return render(request, 'frontend/modals/resume_modal.html', context)

    except Exception as e:
        print(f"Unhandled exception in resume_modal: {e}")
        return JsonResponse({'status': 'error', 'message': f"An error occurred: {e}"}, status=500)


@login_required
def ai_resume_modal(request):
    if request.method == 'POST':
        return add_or_update_resume(request, ai_add_resume_workflow(request))

    return render(request, 'frontend/modals/ai_add_resume_modal.html')


# Cover Letter

@login_required
def cover_letter_modal(request):
    if request.method == 'POST':
        return add_or_update_cover_letter(request, request.POST.dict())

    cover_letter = None

    cover_letter_id = request.GET.get('id')
    if cover_letter_id:
        cover_letter = get_object_or_404(request.user.cover_letters, id=cover_letter_id)

    context = {
        'coverletter': cover_letter
    }

    return render(request, 'frontend/modals/cover_letter_modal.html', context)


@login_required
def ai_cover_letter_modal(request):
    if request.method == 'POST':
        return add_or_update_cover_letter(request, ai_add_cover_letter_workflow(request))

    return render(request, 'frontend/modals/ai_add_cover_letter_modal.html')



# Form Submission Handling Only

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
    """Handles user sign-up."""
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
