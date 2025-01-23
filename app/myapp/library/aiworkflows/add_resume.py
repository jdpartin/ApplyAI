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


    # Initalize the AI chat
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(model_name=GEMINI_MODEL, tools=ai_tools)
    chat = model.start_chat(enable_automatic_function_calling=True)


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


    # Get user info
    user_info = get_data(EntityType.USER)
    user_education = get_data(EntityType.EDUCATION)
    user_work_experience = get_data(EntityType.WORK_EXPERIENCE)
    user_skills = get_data(EntityType.SKILLS)
    user_projects = get_data(EntityType.PROJECTS)
    user_certifications = get_data(EntityType.CERTIFICATIONS)


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


    # Skills, Certifications, and Education

    next_command = "Call the 'set_resume_skills' function to choose the skills for this resume, keeping in mind the purpose they described earlier."
    response = chat.send_message(next_command)

    next_command = "Call the 'set_resume_certifications' function to choose the certifications for this resume, keeping in mind the purpose they described earlier."
    response = chat.send_message(next_command)

    next_command = "Call the 'set_resume_education' function to choose the education entries for this resume, keeping in mind the purpose they described earlier."
    response = chat.send_message(next_command)


    # Work Experience and Projects

    next_command = "Make a list of work experience ids that you believe should be included in this resume, keeping in mind the purpose they described earlier. Do not call a function."
    response = chat.send_message(next_command)

    next_command = "If you did not choose any work experiences just reply 'OK'. If you did choose any work experiences, for each of the work experience ids you just listed, call the 'add_resume_work_experience' function one at a time to add it to this resume and give it a description, keeping in mind the purpose they described earlier."
    response = chat.send_message(next_command)

    next_command = "Make a list of project ids that you believe should be included in this resume, keeping in mind the purpose they described earlier. Do not call a function."
    response = chat.send_message(next_command)

    next_command = "If you did not choose any projects just reply 'OK'. If you did choose any projects, for each of the project ids you just listed, call the 'add_resume_project' function one at a time to add it to this resume and give it a description, keeping in mind the purpose they described earlier."
    response = chat.send_message(next_command)


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

