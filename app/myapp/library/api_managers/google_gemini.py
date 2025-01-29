from myapp.models import *
import google.generativeai as genai
from django.conf import settings
from enum import Enum


class GeminiModel(Enum):
    Gemini_1_5_flash_8b = "gemini-1.5-flash-8b"


GEMINI_API_KEY = settings.GEMINI_API_KEY


class GeminiApiManager:

    def __init__(self, model=GeminiModel.Gemini_1_5_flash_8b, chat_history=[], tools=[], autoFunctionCalling=True):
        global GEMINI_API_KEY

        genai.configure(api_key=GEMINI_API_KEY)

        self.model = genai.GenerativeModel(model_name=model.value, tools=tools)

        if chat_history:
            self.chat = self.model.start_chat(enable_automatic_function_calling=autoFunctionCalling, history=chat_history)
        else:
            self.chat = self.model.start_chat(enable_automatic_function_calling=autoFunctionCalling)


    def send_message(self, message):
        return self.chat.send_message(message)
