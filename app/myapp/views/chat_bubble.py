from myapp.models import UserInfo, Education, WorkExperience, Skill, Project, Certification
from myapp.forms import UserInfoForm, EducationForm, WorkExperienceForm, SkillForm, ProjectForm, CertificationForm
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
from enum import Enum
import requests
import logging
import json
from .json_views import *



logger = logging.getLogger(__name__)

# Normally an API key should never be in the code and checked into version control
# This is a free API and the key is here for dev simplicity
GEMINI_API_KEY = "AIzaSyB2TP2FCbiYgH-wSJcjvRuoiV8GwVWkFiM"

CURRENT_REQUEST = None
UI_TABLES_TO_REFRESH = []
CHAT_HISTORY = []
MAX_CHAT_HISTORY_LENGTH = 50

@csrf_exempt
@login_required
def chat_bubble_view(request):
    global CURRENT_REQUEST, GEMINI_API_KEY, UI_TABLES_TO_REFRESH, CHAT_HISTORY

    if request.method == 'POST':
        try:
            CURRENT_REQUEST = request

            body = json.loads(request.body)
            user_message = body.get('message', '')

            ai_tools = [
                get_data,
                update_user_data,
                add_edit_entity
            ]

            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel(model_name='gemini-1.5-flash', tools=ai_tools)

            if 'chat_history' not in request.session:
                request.session['chat_history'] = []

            CHAT_HISTORY = request.session['chat_history']

            chat = model.start_chat(enable_automatic_function_calling=True, history=CHAT_HISTORY)

            add_chat_to_history("user", user_message)
            response = chat.send_message(user_message)
            add_chat_to_history("model", response.text)

            # Trim chat history if it exceeds the maximum length
            if len(CHAT_HISTORY) > MAX_CHAT_HISTORY_LENGTH:
                CHAT_HISTORY = CHAT_HISTORY[-MAX_CHAT_HISTORY_LENGTH:]

            serializable_history = [
                {
                    "role": item["role"].lower(),
                    "parts": [{"text": part["text"]} for part in item["parts"] if part["text"].strip()]
                }
                for item in CHAT_HISTORY
                if item.get("role") and item["role"].strip() and item.get("parts") and any(part["text"].strip() for part in item["parts"])
            ]

            request.session['chat_history'] = serializable_history
            request.session.modified = True

            response_data = {"response": response.text, "tables_to_update": UI_TABLES_TO_REFRESH.copy()}
            UI_TABLES_TO_REFRESH.clear()  # Reset the list for the next request
            return JsonResponse(response_data, status=200)

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({"error": "Failed to get a response from the AI."}, status=500)

    return JsonResponse({"error": "Invalid request method. Use POST."}, status=405)


def add_chat_to_history(role, text):
    global CHAT_HISTORY

    if not role.strip() or not text.strip():
        return

    CHAT_HISTORY.append({
        "role": role.lower(),
        "parts": [{"text": text.strip()}]
    })

    # Trim chat history if it exceeds the maximum length
    if len(CHAT_HISTORY) > MAX_CHAT_HISTORY_LENGTH:
        CHAT_HISTORY = CHAT_HISTORY[-MAX_CHAT_HISTORY_LENGTH:]


class EntityType(Enum):
    USER = "user"
    EDUCATION = "education"
    WORK_EXPERIENCE = "work_experience"
    SKILLS = "skills"
    PROJECTS = "projects"
    CERTIFICATIONS = "certifications"


# AI Functions


def get_data(entity_type: EntityType):
    """
    Get data for a specific entity type.
    Args:
        entity_type (EntityType): The type of entity to fetch (e.g., EntityType.EDUCATION).
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

    text_data = json.loads(data.content.decode('utf-8'))
    add_chat_to_history("model", json.dumps(text_data))
    return text_data


def add_edit_entity(entity_type: EntityType, id: int = None, **kwargs):
    """
    Add or edit data for a specific entity type based on the provided ID.
    Args:
        entity_type (EntityType): The type of entity to modify (e.g., EntityType.EDUCATION).
        id (int, optional): The ID of the entity to edit. If None, a new entity will be added.
        **kwargs: The fields to add or update.
        Note: In order to call this function you must first call the get_data function with the corresponding entity type
    Returns:
        dict: Confirmation of the operation.
    """
    global CURRENT_REQUEST, UI_TABLES_TO_REFRESH

    post_data = kwargs
    if id is not None:
        post_data['id'] = id

    CURRENT_REQUEST.POST = post_data

    if entity_type == EntityType.EDUCATION:
        response = education_data(CURRENT_REQUEST)
        UI_TABLES_TO_REFRESH.append('education_table')
    elif entity_type == EntityType.WORK_EXPERIENCE:
        response = work_experience_data(CURRENT_REQUEST)
        UI_TABLES_TO_REFRESH.append('work_experience_table')
    elif entity_type == EntityType.SKILLS:
        response = skill_data(CURRENT_REQUEST)
        UI_TABLES_TO_REFRESH.append('skills_table')
    elif entity_type == EntityType.PROJECTS:
        response = project_data(CURRENT_REQUEST)
        UI_TABLES_TO_REFRESH.append('projects_table')
    elif entity_type == EntityType.CERTIFICATIONS:
        response = certification_data(CURRENT_REQUEST)
        UI_TABLES_TO_REFRESH.append('certifications_table')
    else:
        raise ValueError(f"Unknown entity type: {entity_type}")

    updated_data = json.loads(response.content.decode('utf-8'))
    action = "updated" if id else "added"
    add_chat_to_history("model", f"{entity_type.value.capitalize()} {action}: {json.dumps(updated_data)}")
    return updated_data


def update_user_data(first_name: str, last_name: str, phone_number: str, address: str, linkedin_url: str, github_url: str, portfolio_url: str, summary: str):
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
    response = user_info_data(CURRENT_REQUEST)
    UI_TABLES_TO_REFRESH.append('user_info_table')
    updated_data = json.loads(response.content.decode('utf-8'))
    add_chat_to_history("model", f"User data updated: {json.dumps(updated_data)}")
    return updated_data
