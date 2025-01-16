from .models import UserInfo, Education, WorkExperience, Skill, Project, Certification
from .forms import UserInfoForm, EducationForm, WorkExperienceForm, SkillForm, ProjectForm, CertificationForm
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.http import JsonResponse
import google.generativeai as genai
from django.urls import reverse
from telnetlib import DO
import requests
import logging
import inspect
import json


logger = logging.getLogger(__name__)

# Normally an API key should never be in the code and checked into version control
# This is a free API and the key is here for dev simplicity
GEMINI_API_KEY = "AIzaSyB2TP2FCbiYgH-wSJcjvRuoiV8GwVWkFiM"

CURRENT_REQUEST = None
UI_TABLES_TO_REFRESH = []

# AI Chat Bubble View

@csrf_exempt
@login_required
def chat_bubble_view(request):
    global CURRENT_REQUEST, GEMINI_API_KEY, UI_TABLES_TO_REFRESH

    if request.method == 'POST':
        try:
            CURRENT_REQUEST = request

            request.session['chat_history'] = [] # Use to fix chat history issues when debugging locally

            chat_history = request.session.get('chat_history', [])

            body = json.loads(request.body)
            user_message = body.get('message', '')

            ai_tools = [
                get_user_data,
                update_user_data,
                get_user_education,
                add_user_education,
                edit_user_education,
                delete_user_education,
                get_user_work_experience,
                add_user_work_experience,
                edit_user_work_experience,
                delete_user_work_experience,
                get_user_skills,
                add_user_skill,
                edit_user_skill,
                delete_user_skill,
                get_user_projects,
                add_user_project,
                edit_user_project,
                delete_user_project,
                get_user_certifications,
                add_user_certification,
                edit_user_certification,
                delete_user_certification
            ]

            
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel(model_name='gemini-1.5-flash', tools=ai_tools)
            
            if not chat_history:
                chat = model.start_chat(enable_automatic_function_calling=True)
            else:
                chat = model.start_chat(enable_automatic_function_calling=True, history=chat_history)
            
            response = chat.send_message(user_message)
            
            serializable_history = [
                {"role": item.role, "parts": [{"text": part.text} for part in item.parts]}
                for item in chat.history
            ]

            request.session['chat_history'] = serializable_history
            
            # request.session['chat_history'] = [] # Use to clear chat history when running locally
            
            response_data = {"response": response.text, "tables_to_update": UI_TABLES_TO_REFRESH.copy()}
            UI_TABLES_TO_REFRESH.clear()  # Reset the list for the next request
            return JsonResponse(response_data, status=200)

        except Exception as e:
            print(f"Error: {e}")
            request.session['chat_history'] = [] # clear chat history to prevent malformed messages from breaking chat
            return JsonResponse({"error": "Failed to get a response from the AI."}, status=500)

    request.session['chat_history'] = [] # clear chat history to prevent malformed messages from breaking chat
    return JsonResponse({"error": "Invalid request method. Use POST."}, status=405)
    

# AI Functions

def get_user_data():
    """
    Get information about the user in JSON format
    Args: None
    Returns: Name, Email, Phone, Address, LinkedIn URL, GitHub URL, PortfolioURL, and Summary
    """
    global CURRENT_REQUEST
    data = user_info_data(CURRENT_REQUEST)
    return json.loads(data.content.decode('utf-8'))


def update_user_data(first_name: str, last_name: str, phone_number: str, address: str, linkedin_url: str, github_url: str, portfolio_url: str, summary: str):
    """
    Update user information except email.
    You MUST complete ALL fields.
    Args:
        first_name (str): User's first name.
        last_name (str): User's last name.
        phone_number (str): User's phone number.
        address (str): User's address.
        linkedin_url (str): User's LinkedIn URL.
        github_url (str): User's GitHub URL.
        portfolio_url (str): User's portfolio URL.
        summary (str): User's summary.
    Returns:
        dict: Confirmation of the operation.
    """
    global CURRENT_REQUEST, UI_TABLES_TO_REFRESH
    CURRENT_REQUEST.POST = {
        'email': CURRENT_REQUEST.user.email,
        'first_name': first_name,
        'last_name': last_name,
        'phone_number': phone_number,
        'address': address,
        'linkedin_url': linkedin_url,
        'github_url': github_url,
        'portfolio_url': portfolio_url,
        'summary': summary
    }
    response = user_info_modal(CURRENT_REQUEST)
    UI_TABLES_TO_REFRESH.append('user_info_table')
    return json.loads(response.content.decode('utf-8'))


def get_user_education():
    """
    Get a list of all known education information for the user in JSON format
    Args: None
    """
    global CURRENT_REQUEST
    data = education_data(CURRENT_REQUEST)
    return json.loads(data.content.decode('utf-8'))


def add_user_education(degree: str, institution: str, start_date: str, end_date: str, description: str):
    """
    Add new education information for the user.
    Args:
        degree (str): Degree obtained.
        institution (str): Institution name.
        start_date (str): Start date of the education.
        end_date (str): End date of the education.
        description (str): Description of the education.
    Returns:
        dict: Confirmation of the operation.
    """
    global CURRENT_REQUEST, UI_TABLES_TO_REFRESH
    CURRENT_REQUEST.POST = {
        'degree': degree,
        'institution': institution,
        'start_date': start_date,
        'end_date': end_date,
        'description': description
    }
    response = education_modal(CURRENT_REQUEST)
    UI_TABLES_TO_REFRESH.append('education_table')
    return json.loads(response.content.decode('utf-8'))


def edit_user_education(education_id: int, degree: str, institution: str, start_date: str, end_date: str, description: str):
    """
    Edit an existing education record for the user.
    Args:
        education_id (int): ID of the education record to edit.
        degree (str): Degree obtained.
        institution (str): Institution name.
        start_date (str): Start date of the education.
        end_date (str): End date of the education.
        description (str): Description of the education.
    Returns:
        dict: Confirmation of the operation.
    """
    global CURRENT_REQUEST, UI_TABLES_TO_REFRESH
    CURRENT_REQUEST.POST = {
        'id': education_id,
        'degree': degree,
        'institution': institution,
        'start_date': start_date,
        'end_date': end_date,
        'description': description
    }
    response = education_modal(CURRENT_REQUEST)
    UI_TABLES_TO_REFRESH.append('education_table')
    return json.loads(response.content.decode('utf-8'))


def delete_user_education(education_id: int):
    """
    Delete an existing education record for the user.
    Args:
        education_id (int): ID of the education record to delete.
    Returns:
        dict: Confirmation of the operation.
    """
    global CURRENT_REQUEST, UI_TABLES_TO_REFRESH
    CURRENT_REQUEST.GET = {'id': education_id}
    response = education_delete(CURRENT_REQUEST)
    UI_TABLES_TO_REFRESH.append('education_table')
    return json.loads(response.content.decode('utf-8'))


def get_user_work_experience():
    """
    Get a list of all known work experience information for the user in JSON format
    Args: None
    """
    global CURRENT_REQUEST
    data = work_experience_data(CURRENT_REQUEST)
    return json.loads(data.content.decode('utf-8'))


def add_user_work_experience(job_title: str, company: str, start_date: str, end_date: str, responsibilities: str):
    """
    Add new work experience information for the user.
    Args:
        job_title (str): Job title.
        company (str): Company name.
        start_date (str): Start date of the job.
        end_date (str): End date of the job.
        responsibilities (str): Job responsibilities.
    Returns:
        dict: Confirmation of the operation.
    """
    global CURRENT_REQUEST, UI_TABLES_TO_REFRESH
    CURRENT_REQUEST.POST = {
        'job_title': job_title,
        'company': company,
        'start_date': start_date,
        'end_date': end_date,
        'responsibilities': responsibilities
    }
    response = work_experience_modal(CURRENT_REQUEST)
    UI_TABLES_TO_REFRESH.append('work_experience_table')
    return json.loads(response.content.decode('utf-8'))


def edit_user_work_experience(work_id: int, job_title: str, company: str, start_date: str, end_date: str, responsibilities: str):
    """
    Edit an existing work experience record for the user.
    Args:
        work_id (int): ID of the work experience record to edit.
        job_title (str): Job title.
        company (str): Company name.
        start_date (str): Start date of the job.
        end_date (str): End date of the job.
        responsibilities (str): Job responsibilities.
    Returns:
        dict: Confirmation of the operation.
    """
    global CURRENT_REQUEST, UI_TABLES_TO_REFRESH
    CURRENT_REQUEST.POST = {
        'id': work_id,
        'job_title': job_title,
        'company': company,
        'start_date': start_date,
        'end_date': end_date,
        'responsibilities': responsibilities
    }
    response = work_experience_modal(CURRENT_REQUEST)
    UI_TABLES_TO_REFRESH.append('work_experience_table')
    return json.loads(response.content.decode('utf-8'))


def delete_user_work_experience(work_id: int):
    """
    Delete an existing work experience record for the user.
    Args:
        work_id (int): ID of the work experience record to delete.
    Returns:
        dict: Confirmation of the operation.
    """
    global CURRENT_REQUEST, UI_TABLES_TO_REFRESH
    CURRENT_REQUEST.GET = {'id': work_id}
    response = work_experience_delete(CURRENT_REQUEST)
    UI_TABLES_TO_REFRESH.append('work_experience_table')
    return json.loads(response.content.decode('utf-8'))


def get_user_skills():
    """
    Get a list of all known skills for the user in JSON format
    Args: None
    """
    global CURRENT_REQUEST
    data = skill_data(CURRENT_REQUEST)
    return json.loads(data.content.decode('utf-8'))


def add_user_skill(skill_name: str, proficiency_level: str):
    """
    Add a new skill for the user.
    Args:
        skill_name (str): Name of the skill.
        proficiency_level (str): Proficiency level of the skill.
    Returns:
        dict: Confirmation of the operation.
    """
    global CURRENT_REQUEST, UI_TABLES_TO_REFRESH
    CURRENT_REQUEST.POST = {
        'skill_name': skill_name,
        'proficiency_level': proficiency_level
    }
    response = skill_modal(CURRENT_REQUEST)
    UI_TABLES_TO_REFRESH.append('skills_table')
    return json.loads(response.content.decode('utf-8'))


def edit_user_skill(skill_id: int, skill_name: str, proficiency_level: str):
    """
    Edit an existing skill for the user.
    Args:
        skill_id (int): ID of the skill to edit.
        skill_name (str): Name of the skill.
        proficiency_level (str): Proficiency level of the skill.
    Returns:
        dict: Confirmation of the operation.
    """
    global CURRENT_REQUEST, UI_TABLES_TO_REFRESH
    CURRENT_REQUEST.POST = {
        'id': skill_id,
        'skill_name': skill_name,
        'proficiency_level': proficiency_level
    }
    response = skill_modal(CURRENT_REQUEST)
    UI_TABLES_TO_REFRESH.append('skills_table')
    return json.loads(response.content.decode('utf-8'))


def delete_user_skill(skill_id: int):
    """
    Delete an existing skill for the user.
    Args:
        skill_id (int): ID of the skill to delete.
    Returns:
        dict: Confirmation of the operation.
    """
    global CURRENT_REQUEST, UI_TABLES_TO_REFRESH
    CURRENT_REQUEST.GET = {'id': skill_id}
    response = skill_delete(CURRENT_REQUEST)
    UI_TABLES_TO_REFRESH.append('skills_table')
    return json.loads(response.content.decode('utf-8'))


def get_user_projects():
    """
    Get a list of all known projects for the user in JSON format
    Args: None
    """
    global CURRENT_REQUEST
    data = project_data(CURRENT_REQUEST)
    return json.loads(data.content.decode('utf-8'))


def add_user_project(project_name: str, description: str, technologies_used: str, start_date: str, end_date: str):
    """
    Add a new project for the user.
    Args:
        project_name (str): Name of the project.
        description (str): Description of the project.
        technologies_used (str): Technologies used in the project.
        start_date (str): Start date of the project.
        end_date (str): End date of the project.
    Returns:
        dict: Confirmation of the operation.
    """
    global CURRENT_REQUEST, UI_TABLES_TO_REFRESH
    CURRENT_REQUEST.POST = {
        'project_name': project_name,
        'description': description,
        'technologies_used': technologies_used,
        'start_date': start_date,
        'end_date': end_date
    }
    response = project_modal(CURRENT_REQUEST)
    UI_TABLES_TO_REFRESH.append('projects_table')
    return json.loads(response.content.decode('utf-8'))


def edit_user_project(project_id: int, project_name: str, description: str, technologies_used: str, start_date: str, end_date: str):
    """
    Edit an existing project for the user.
    Args:
        project_id (int): ID of the project to edit.
        project_name (str): Name of the project.
        description (str): Description of the project.
        technologies_used (str): Technologies used in the project.
        start_date (str): Start date of the project.
        end_date (str): End date of the project.
    Returns:
        dict: Confirmation of the operation.
    """
    global CURRENT_REQUEST, UI_TABLES_TO_REFRESH
    CURRENT_REQUEST.POST = {
        'id': project_id,
        'project_name': project_name,
        'description': description,
        'technologies_used': technologies_used,
        'start_date': start_date,
        'end_date': end_date
    }
    response = project_modal(CURRENT_REQUEST)
    UI_TABLES_TO_REFRESH.append('projects_table')
    return json.loads(response.content.decode('utf-8'))


def delete_user_project(project_id: int):
    """
    Delete an existing project for the user.
    Args:
        project_id (int): ID of the project to delete.
    Returns:
        dict: Confirmation of the operation.
    """
    global CURRENT_REQUEST, UI_TABLES_TO_REFRESH
    CURRENT_REQUEST.GET = {'id': project_id}
    response = project_delete(CURRENT_REQUEST)
    UI_TABLES_TO_REFRESH.append('projects_table')
    return json.loads(response.content.decode('utf-8'))


def get_user_certifications():
    """
    Get a list of all known certifications for the user in JSON format
    Args: None
    """
    global CURRENT_REQUEST
    data = certification_data(CURRENT_REQUEST)
    return json.loads(data.content.decode('utf-8'))


def add_user_certification(certification_name: str, issuing_organization: str, issue_date: str, expiration_date: str, credential_id: str):
    """
    Add a new certification for the user.
    Args:
        certification_name (str): Name of the certification.
        issuing_organization (str): Issuing organization of the certification.
        issue_date (str): Date the certification was issued.
        expiration_date (str): Expiration date of the certification.
        credential_id (str): Credential ID of the certification.
    Returns:
        dict: Confirmation of the operation.
    """
    global CURRENT_REQUEST, UI_TABLES_TO_REFRESH
    CURRENT_REQUEST.POST = {
        'certification_name': certification_name,
        'issuing_organization': issuing_organization,
        'issue_date': issue_date,
        'expiration_date': expiration_date,
        'credential_id': credential_id
    }
    response = certification_modal(CURRENT_REQUEST)
    UI_TABLES_TO_REFRESH.append('certifications_table')
    return json.loads(response.content.decode('utf-8'))


def edit_user_certification(certification_id: int, certification_name: str, issuing_organization: str, issue_date: str, expiration_date: str, credential_id: str):
    """
    Edit an existing certification for the user.
    Args:
        certification_id (int): ID of the certification to edit.
        certification_name (str): Name of the certification.
        issuing_organization (str): Issuing organization of the certification.
        issue_date (str): Date the certification was issued.
        expiration_date (str): Expiration date of the certification.
        credential_id (str): Credential ID of the certification.
    Returns:
        dict: Confirmation of the operation.
    """
    global CURRENT_REQUEST, UI_TABLES_TO_REFRESH
    CURRENT_REQUEST.POST = {
        'id': certification_id,
        'certification_name': certification_name,
        'issuing_organization': issuing_organization,
        'issue_date': issue_date,
        'expiration_date': expiration_date,
        'credential_id': credential_id
    }
    response = certification_modal(CURRENT_REQUEST)
    UI_TABLES_TO_REFRESH.append('certifications_table')
    return json.loads(response.content.decode('utf-8'))


def delete_user_certification(certification_id: int):
    """
    Delete an existing certification for the user.
    Args:
        certification_id (int): ID of the certification to delete.
    Returns:
        dict: Confirmation of the operation.
    """
    global CURRENT_REQUEST, UI_TABLES_TO_REFRESH
    CURRENT_REQUEST.GET = {'id': certification_id}
    response = certification_delete(CURRENT_REQUEST)
    UI_TABLES_TO_REFRESH.append('certifications_table')
    return json.loads(response.content.decode('utf-8'))


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

# ------------------ Dashboard and Logout Views ------------------

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

# ------------------ JSON Data Views ------------------

@login_required
def user_info_data(request):
    """
    Get information about the user
    Args: None
    Returns Name, Email, Phone, Address, LinkedIn URL, GitHub URL, PortfolioURL, and Summary in JSON format
    """
    user_info = UserInfo.objects.filter(user=request.user).first()
    if user_info:
        data = {
            "email": request.user.email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "phone_number": user_info.phone_number,
            "address": user_info.address,
            "linkedin_url": user_info.linkedin_url,
            "github_url": user_info.github_url,
            "portfolio_url": user_info.portfolio_url,
            "summary": user_info.summary,
        }
    else:
        data = {}
    return JsonResponse(data, safe=False)

@login_required
def education_data(request):
    """Returns education data in JSON format."""
    educations = Education.objects.filter(user=request.user).values()
    return JsonResponse(list(educations), safe=False)

@login_required
def work_experience_data(request):
    """Returns work experience data in JSON format."""
    work_experiences = WorkExperience.objects.filter(user=request.user).values()
    return JsonResponse(list(work_experiences), safe=False)

@login_required
def skill_data(request):
    """Returns skill data in JSON format."""
    skills = Skill.objects.filter(user=request.user).values()
    return JsonResponse(list(skills), safe=False)

@login_required
def project_data(request):
    """Returns project data in JSON format."""
    projects = Project.objects.filter(user=request.user).values()
    return JsonResponse(list(projects), safe=False)

@login_required
def certification_data(request):
    """Returns certification data in JSON format."""
    certifications = Certification.objects.filter(user=request.user).values()
    return JsonResponse(list(certifications), safe=False)

# ------------------ Modal Views ------------------

@login_required
def user_info_modal(request):
    """Handles User Info modal form submission and rendering."""
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

@login_required
def education_delete(request):
    """Handles deletion of an Education record."""
    education_id = request.GET.get('id')
    education = get_object_or_404(Education, id=education_id, user=request.user)

    if request.method == 'GET':
        education.delete()
        return JsonResponse({"message": "Education deleted successfully!", "status": "success"}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)

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

@login_required
def work_experience_delete(request):
    """Handles deletion of a Work Experience record."""
    work_experience_id = request.GET.get('id')
    work_experience = get_object_or_404(WorkExperience, id=work_experience_id, user=request.user)

    if request.method == 'GET':
        work_experience.delete()
        return JsonResponse({"message": "Work experience deleted successfully!", "status": "success"}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)

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

@login_required
def skill_delete(request):
    """Handles deletion of a Skill record."""
    skill_id = request.GET.get('id')
    skill = get_object_or_404(Skill, id=skill_id, user=request.user)

    if request.method == 'GET':
        skill.delete()
        return JsonResponse({"message": "Skill deleted successfully!", "status": "success"}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)

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

@login_required
def project_delete(request):
    """Handles deletion of a Project record."""
    project_id = request.GET.get('id')
    project = get_object_or_404(Project, id=project_id, user=request.user)

    if request.method == 'GET':
        project.delete()
        return JsonResponse({"message": "Project deleted successfully!", "status": "success"}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)

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

@login_required
def certification_delete(request):
    """Handles deletion of a Certification record."""
    certification_id = request.GET.get('id')
    certification = get_object_or_404(Certification, id=certification_id, user=request.user)

    if request.method == 'GET':
        certification.delete()
        return JsonResponse({"message": "Certification deleted successfully!", "status": "success"}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)
