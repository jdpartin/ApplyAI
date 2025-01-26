from django.shortcuts import render
from django.http import JsonResponse
from myapp.models import *
import google.generativeai as genai
from typing import List
from .common import get_data, EntityType
from django.conf import settings

GEMINI_API_KEY = settings.GEMINI_API_KEY
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

def ai_add_resume_workflow(request):
    if request.method != 'POST':
        return render(request, 'frontend/modals/ai_add_resume_modal.html')

    global CURRENT_REQUEST
    CURRENT_REQUEST = request

    resume_description = request.POST.get("resume_description")
    if not resume_description:
        return JsonResponse({"error": "A resume_description must be provided"})

    # Configure AI Model
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(model_name=GEMINI_MODEL, tools=[
        set_resume_name_and_purpose,
        set_resume_summary,
        set_resume_certifications,
        set_resume_skills,
        set_resume_education,
        add_resume_work_experience,
        add_resume_project,
    ])
    chat = model.start_chat(enable_automatic_function_calling=True)

    # Step 1: Set Resume Name and Purpose
    response = chat.send_message(f"""
        This is an automated process to create a resume tailored to the following description:
        {resume_description}

        Follow resume best practices. Do not hallucinate information or call unnecessary functions. 
        Start by calling the 'set_resume_name_and_purpose' function to set the resume's name and purpose.
    """)

    # Step 2: Generate Summary
    user_info = get_data(CURRENT_REQUEST, EntityType.USER)
    user_skills = get_data(CURRENT_REQUEST, EntityType.SKILLS)
    user_work_experience = get_data(CURRENT_REQUEST, EntityType.WORK_EXPERIENCE)
    user_education = get_data(CURRENT_REQUEST, EntityType.EDUCATION)
    user_certifications = get_data(CURRENT_REQUEST, EntityType.CERTIFICATIONS)

    response = chat.send_message(f"""
        Here is the user's comprehensive information to write a tailored professional summary:

        Personal Information:
        {user_info}

        Relevant Skills:
        {user_skills}

        Work Experience:
        {user_work_experience}

        Education:
        {user_education}

        Certifications:
        {user_certifications}

        The resume's purpose is: "{resume_description}". Use this data to call the 'set_resume_summary' function and write a concise, impactful summary tailored to the resume's purpose.
    """)

    # Step 3: Choose Skills, Certifications, and Education
    response = chat.send_message(f"""
        Based on the resume's purpose and the user's details, select the most relevant entries:

        Skills:
        {user_skills}

        Certifications:
        {user_certifications}

        Education:
        {user_education}

        Follow these steps:
        1. Call 'set_resume_skills' to set the skills most relevant to the resume's purpose.
        2. Call 'set_resume_certifications' to include certifications.
        3. Call 'set_resume_education' to select education entries.
    """)

    # Step 4: Tailor Work Experience
    response = chat.send_message(f"""
        Here is the user's work experience:
        {user_work_experience}

        Tailor the work experience for the resume's purpose:
        1. Identify IDs of relevant work experiences.
        2. For each selected ID, write a concise, tailored description in bullet points.
        3. Call 'add_resume_work_experience' for each entry with its ID and tailored description.
    """)

    # Step 5: Tailor Projects
    user_projects = get_data(CURRENT_REQUEST, EntityType.PROJECTS)
    response = chat.send_message(f"""
        Here are the user's projects:
        {user_projects}

        Tailor the projects for the resume's purpose:
        1. Identify IDs of relevant projects.
        2. For each selected ID, write a concise, tailored description in bullet points.
        3. Call 'add_resume_project' for each entry with its ID and tailored description.
    """)

    # Return Final RESUME_INFO
    return RESUME_INFO

# AI Functions
def add_resume_project(id: int, description: str):
    """
    Adds a single project entry to the resume being created.
    Args: 
        id: The ID of the project.
        description: The tailored description for the project.
    """
    global RESUME_INFO
    RESUME_INFO.setdefault('projects', []).append({"id": id, "description": description})

def add_resume_work_experience(id: int, description: str):
    """
    Adds a single work experience entry to the resume being created.
    Args: 
        id: The ID of the work experience.
        description: The tailored description for the work experience.
    """
    global RESUME_INFO
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
