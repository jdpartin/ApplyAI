from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from myapp.models import *
import google.generativeai as genai
from .common import get_data, EntityType
from django.conf import settings
from enum import Enum


class GeminiModel(Enum):
    Gemini_1_5_flash_8b = "gemini-1.5-flash-8b"


GEMINI_API_KEY = settings.GEMINI_API_KEY


class GeminiApiManager:

    def __init__(self, model=GeminiModel.Gemini_1_5_flash_8b, tools=[], autoFunctionCalling=True):
        global GEMINI_API_KEY

        genai.configure(api_key=GEMINI_API_KEY)

        self.model = genai.GenerativeModel(model_name=model, tools=tools)

        self.chat = self.model.start_chat(enable_automatic_function_calling=autoFunctionCalling)


    def send_message(self, message, mandatory_function_calls=[]):
        response = None

        try:
            response = self.chat.send_message(message)

        except Exception as e:
            print(f"Error during message processing: {e}")
            response = self.chat.send_message(f"An error occurred: {e}. Please ensure your response meets the requirements and retry.")

        return response