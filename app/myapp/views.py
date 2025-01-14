from .models import UserInfo, Education, WorkExperience, Skill, Project, Certification
from .forms import UserInfoForm, EducationForm, WorkExperienceForm, SkillForm, ProjectForm, CertificationForm
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from myapp.classes.gemini_manager import GeminiManager
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.urls import reverse
import logging
import json


logger = logging.getLogger(__name__)

GEMINI_API_KEY = "AIzaSyB2TP2FCbiYgH-wSJcjvRuoiV8GwVWkFiM"
BACKEND_BASE_URL = "http://localhost:8000"


@csrf_exempt
@login_required
def chat_bubble_view(request):
    """
    Handle requests for the chat bubble.
    Maintain chat history in the session and use it to interact with GeminiManager.
    """
    if request.method == 'POST':
        logger.info("Received POST request to chat-bubble endpoint.")

        # Get chat history from session or initialize it
        chat_history = request.session.get('chat_history', [])

        # Parse user input
        try:
            body = json.loads(request.body)
            user_message = body.get('message', '')
            logger.debug(f"User message received: {user_message}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON payload: {e}")
            return JsonResponse({"error": "Invalid JSON payload."}, status=400)

        if not user_message:
            logger.warning("Empty user message received.")
            return JsonResponse({"error": "Message content is required."}, status=400)

        # Initialize GeminiManager
        gemini_manager = GeminiManager(api_key=GEMINI_API_KEY, backend_base_url=BACKEND_BASE_URL)

        # Process user message
        try:
            ai_responses = gemini_manager.send_message(user_message)  # Updated to handle a list of responses
            logger.debug(f"AI responses from GeminiManager: {ai_responses}")

            # Update chat history
            chat_history.append({"role": "user", "content": user_message})
            for response in ai_responses:
                chat_history.append({"role": "assistant", "content": response})
            
            request.session['chat_history'] = chat_history
            logger.debug(f"Updated chat history: {chat_history}")
        except Exception as e:
            logger.error(f"Error while communicating with GeminiManager: {e}")
            return JsonResponse({"error": "Failed to get a response from the AI."}, status=500)

        # Return the updated chat history
        return JsonResponse({"chat_history": chat_history})

    logger.warning("Invalid request method received.")
    return JsonResponse({"error": "Invalid request method. Use POST."}, status=405)



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
    """Returns user info data in JSON format."""
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
