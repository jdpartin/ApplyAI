from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from myapp.models import *
from enum import Enum
import google.generativeai as genai
import json
from .json_views import *


GEMINI_API_KEY = "AIzaSyB2TP2FCbiYgH-wSJcjvRuoiV8GwVWkFiM"
GEMINI_MODEL = "gemini-1.5-flash-8b"

CURRENT_REQUEST = None

COVER_LETTER_DATA = {
    "name": "",
    "purpose": "",
    "text": "",
}


@login_required
def ai_add_cover_letter_modal(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

    return add_cover_letter(request)

@login_required
def cover_letter_modal(request):
    cover_letter = None

    cover_letter_id = request.GET.get('id')
    if cover_letter_id:
        cover_letter = get_object_or_404(request.user.resumes, id=cover_letter_id)

    context = {
        'coverletter': cover_letter
    }

    return render(request, 'frontend/modals/cover_letter_modal.html', context)


@login_required
def ai_add_cover_letter_modal(request):
    return render(request, 'frontend/modals/ai_add_cover_letter_modal.html')

@login_required
def add_cover_letter_modal(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

    return add_cover_letter(request)

@login_required
def add_cover_letter(request, data=None):
    if not data:
            data = json.loads(request.body)

    return False