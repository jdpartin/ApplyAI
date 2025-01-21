import re
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpRequest
from myapp.models import *
from enum import Enum
import google.generativeai as genai
from typing import List, Dict
import json
from .json_views import *


GEMINI_API_KEY = "AIzaSyB2TP2FCbiYgH-wSJcjvRuoiV8GwVWkFiM"
GEMINI_MODEL = "gemini-1.5-flash-8b"
CURRENT_REQUEST = None

RESUME_INFO = {
    "name": "",
    "purpose": "",
    "includePersonalInfo": {
        "summary": "",
        "phone": True,
        "email": True,
        "address": True
    },
    "educations": [],
    "workExperiences": [],
    "skills": [],
    "projects": [],
    "certifications": []
}


@login_required
def ai_add_resume_modal(request):
    if request.method != 'POST':
        return render(request, 'frontend/modals/ai_add_resume_modal.html')

    global CURRENT_REQUEST

    CURRENT_REQUEST = request

    resume_description = request.POST.get("resume_description")

    print(f"Received request to add resume. Description: {resume_description}")

    if not resume_description:
        return JsonResponse({ "error": "A resume_description must be provided" })

    # Define the AI's functions
    ai_tools = [
        set_resume_name_and_purpose,
        set_resume_summary,
        set_resume_certifications,
        set_resume_skills,
        set_resume_education,
        add_resume_work_experience,
        add_resume_project
    ]

    print("AI tools defined")

    # Initalize the AI chat
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(model_name=GEMINI_MODEL, tools=ai_tools)
    chat = model.start_chat(enable_automatic_function_calling=True)

    print("AI chat initialized")

    # Purpose and Name
    next_command = f"""
        This is an automated process to walk you through creating a resume. 
        Follow resume best practices. 
        Do not hallucinate information. 
        Do not call a function you are not explicitly asked to call. 

        This is a description of the purpose of the resume. It could also be a job description, 
        in that case you should assume the resume's purpose is to be tailored to that job:

        {resume_description} 

        Call the 'set_resume_name_and_purpose' function to define the name and purpose of this resume.
    """
    response = chat.send_message(next_command)

    print("Resume name and purpose set")

    # Get user info
    user_info = get_data(EntityType.USER)
    user_education = get_data(EntityType.EDUCATION)
    user_work_experience = get_data(EntityType.WORK_EXPERIENCE)
    user_skills = get_data(EntityType.SKILLS)
    user_projects = get_data(EntityType.PROJECTS)
    user_certifications = get_data(EntityType.CERTIFICATIONS)

    print("User information gathered")

    # Summary
    next_command = f"""
        Here is all the information you need to know about the person you are completing this resume for. 

        Personal Information: 
        {user_info} 

        Education: 
        {user_education} 

        Work Experience: 
        {user_work_experience}

        Skills: 
        {user_skills}

        Projects: 
        {user_projects} 

        Certifications: 
        {user_certifications} 

        Call the 'set_resume_summary' function to create a professional summary for this resume, keeping in mind the purpose they described earlier.
    """
    response = chat.send_message(next_command)

    print("Resume summary set")

    # Skills, Certifications, and Education
    next_command = "Call the 'set_resume_skills' function to choose the skills for this resume, keeping in mind the purpose they described earlier."
    response = chat.send_message(next_command)

    print("Resume skills set")

    next_command = "Call the 'set_resume_certifications' function to choose the certifications for this resume, keeping in mind the purpose they described earlier."
    response = chat.send_message(next_command)

    print("Resume certifications set")

    next_command = "Call the 'set_resume_education' function to choose the education entries for this resume, keeping in mind the purpose they described earlier."
    response = chat.send_message(next_command)

    print("Resume education set")

    # Work Experience and Projects

    next_command = "Make a list of work experience ids that you believe should be included in this resume, keeping in mind the purpose they described earlier. Do not call a function."
    response = chat.send_message(next_command)

    print("Resume work experiences selected")

    next_command = "If you did not choose any work experiences just reply 'OK'. If you did choose any work experiences, for each of the work experience ids you just listed, call the 'add_resume_work_experience' function one at a time to add it to this resume and give it a description, keeping in mind the purpose they described earlier."
    response = chat.send_message(next_command)

    print("Resume work experiences set")

    next_command = "Make a list of project ids that you believe should be included in this resume, keeping in mind the purpose they described earlier. Do not call a function."
    response = chat.send_message(next_command)

    print("Resume projects selected")

    next_command = "If you did not choose any projects just reply 'OK'. If you did choose any projects, for each of the project ids you just listed, call the 'add_resume_project' function one at a time to add it to this resume and give it a description, keeping in mind the purpose they described earlier."
    response = chat.send_message(next_command)

    print("Resume projects set")

    return ai_add_resume_modal_create_resume(request)


# User Info Gathering Functions 

class EntityType(Enum):
    USER = "user"
    EDUCATION = "education"
    WORK_EXPERIENCE = "work_experience"
    SKILLS = "skills"
    PROJECTS = "projects"
    CERTIFICATIONS = "certifications"
    
def get_data(entity_type: EntityType):
    """
    Get data for a specific entity type.
    Args:
        entity_type (EntityType): The type of entity to fetch.
    Returns:
        dict: Data corresponding to the specified entity type.
    """
    global CURRENT_REQUEST

    if entity_type == EntityType.USER:
        data = user_info_data(CURRENT_REQUEST)
    elif entity_type == EntityType.EDUCATION:
        data = education_data(CURRENT_REQUEST)
    elif entity_type == EntityType.WORK_EXPERIENCE:
        data = work_experience_data(CURRENT_REQUEST)
    elif entity_type == EntityType.SKILLS:
        data = skill_data(CURRENT_REQUEST)
    elif entity_type == EntityType.PROJECTS:
        data = project_data(CURRENT_REQUEST)
    elif entity_type == EntityType.CERTIFICATIONS:
        data = certification_data(CURRENT_REQUEST)
    else:
        raise ValueError(f"Unknown entity type: '{entity_type}'")

    return json.loads(data.content.decode('utf-8'))

# AI Functions

def add_resume_project(id: int, description: str):
    """
    Adds a single project entry to the resume being created.
    Args: 
        id: The ID of the project.
        description: The tailored description for the project.
    """
    global RESUME_INFO
    # Add the project entry to the list of projects
    RESUME_INFO.setdefault('projects', []).append({"id": id, "description": description})


def add_resume_work_experience(id: int, description: str):
    """
    Adds a single work experience entry to the resume being created.
    Args: 
        id: The ID of the work experience.
        description: The tailored description for the work experience.
    """
    global RESUME_INFO
    # Add the work experience entry to the list of work experiences
    RESUME_INFO.setdefault('workExperiences', []).append({"id": id, "description": description})


def set_resume_certifications(ids: List[int]):
    """
    Sets which certification entries should be included in the resume you are currently creating.
    Args:
        ids: A list of certification ids that should be included in the current resume.
    """
    global RESUME_INFO
    RESUME_INFO['certifications'] = [{"id": id} for id in ids]

def set_resume_skills(ids: List[int]):
    """
    Sets which skill entries should be included in the resume you are currently creating.
    Args:
        ids: A list of skill ids that should be included in the current resume.
    """
    global RESUME_INFO
    RESUME_INFO['skills'] = [{"id": id} for id in ids]

def set_resume_education(ids: List[int]):
    """
    Sets which education entries should be included in the resume you are currently creating.
    Args:
        ids: A list of education ids that should be included in the current resume.
    """
    global RESUME_INFO
    RESUME_INFO['educations'] = [{"id": id} for id in ids]

def set_resume_summary(summary: str):
    """
    Sets the summary of the resume you are currently creating.
    Args:
        summary: A brief, professional, descriptive summary of the user's skills.
    """
    global RESUME_INFO
    RESUME_INFO['includePersonalInfo']['summary'] = summary

def set_resume_name_and_purpose(name: str, purpose: str):
    """
    Sets the name and purpose of the resume you are currently creating.
    Args:
        name: The name of this resume, basically a title of the document.
        purpose: The purpose this resume is meant to serve, for example: Obtain Senior .NET Role or Tailored Resume for .NET Developer at NVIDIA.
    """
    global RESUME_INFO
    RESUME_INFO['name'] = name
    RESUME_INFO['purpose'] = purpose



# Other views

@login_required
def resume_modal(request):
    resume = None
    work_experience_data = {}
    project_data = {}

    resume_id = request.GET.get('id')
    if resume_id:
        resume = get_object_or_404(request.user.resumes, id=resume_id)

        # Prepare tailored work experience data
        work_experience_data = {
            rwe.workExperience_id: rwe.tailoredDescription
            for rwe in resume.resumeworkexperience_set.all()
        }

        # Prepare tailored project data (if applicable)
        project_data = {
            rp.project_id: rp.tailoredDescription
            for rp in resume.resumeproject_set.all()
        }

    context = {
        'user': request.user,
        'resume': resume,
        'work_experience_data': work_experience_data,  # Pass tailored descriptions for work experiences
        'project_data': project_data,  # Pass tailored descriptions for projects
    }
    return render(request, 'frontend/modals/resume_modal.html', context)


@login_required
def resume_delete(request):
    resume_id = request.GET.get('id')

    if not resume_id:
        return JsonResponse({"error": "Resume ID is required."}, status=400)

    # Ensure the resume belongs to the current user
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    resume.delete()

    return JsonResponse({"message": "Resume deleted successfully!", "status": "success"}, status=200)


@login_required
def add_resume_modal(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

    return add_resume(request)

@login_required
def ai_add_resume_modal_create_resume(request):
    return add_resume(request, RESUME_INFO)

@login_required
def add_resume(request, data=None):
    try:
        # Parse JSON body
        if not data:
            data = json.loads(request.body)

        # Create the Resume object
        resume = Resume.objects.create(
            user=request.user,
            name=data.get('name', 'Untitled Resume'),
            purpose=data.get('purpose', ''),
            tailoredSummary=data['includePersonalInfo'].get('summary', ''),
            showPhone=data['includePersonalInfo'].get('phone', False),
            showEmail=data['includePersonalInfo'].get('email', False),
            showAddress=data['includePersonalInfo'].get('address', False)
        )

        # Add related data (Education, WorkExperience, Skills, etc.)
        # 1. Education
        education_ids = [item['id'] for item in data.get('educations', [])]
        educations = Education.objects.filter(id__in=education_ids)
        resume.educations.add(*educations)

        # 2. Work Experience
        for work_experience_data in data.get('workExperiences', []):
            work_experience = get_object_or_404(WorkExperience, id=work_experience_data['id'])
            resume.workExperiences.add(work_experience, through_defaults={
                'tailoredDescription': work_experience_data.get('tailoredSummary', '')
            })

        # 3. Skills
        skill_ids = [item['id'] for item in data.get('skills', [])]
        skills = Skill.objects.filter(id__in=skill_ids)
        resume.skills.add(*skills)

        # 4. Projects
        for project_data in data.get('projects', []):
            project = get_object_or_404(Project, id=project_data['id'])
            resume.projects.add(project, through_defaults={
                'tailoredDescription': project_data.get('tailoredSummary', '')
            })

        # 5. Certifications
        certification_ids = [item['id'] for item in data.get('certifications', [])]
        certifications = Certification.objects.filter(id__in=certification_ids)
        resume.certifications.add(*certifications)

        # Save and return success
        resume.save()
        return JsonResponse({'status': 'success', 'message': 'Resume created successfully.', 'resume_id': resume.id})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)
    except KeyError as e:
        return JsonResponse({'status': 'error', 'message': f'Missing key: {e}'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=500)
