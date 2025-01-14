import google.generativeai as genai
import requests

class GeminiManager:
    """
    A class to manage connections and interactions with Google's Gemini API,
    including function calling support and backend API interactions.
    """

    def __init__(self, api_key, backend_base_url):
        """
        Initialize the GeminiManager with the required API key and backend base URL.
        :param api_key: Your Gemini API key.
        :param backend_base_url: Base URL for your Django backend.
        """
        self.api_key = api_key
        self.backend_base_url = backend_base_url
        self.chat = None
        self.model = None

        # Configure the generative AI library with the API key
        genai.configure(api_key=self.api_key)

        # Define functions for function calling
        self.tools = [
            self.set_light_values,  # Example function
        ]

        # Initialize the model with tools
        self.model = genai.GenerativeModel(model_name='gemini-1.5-flash', tools=self.tools)

    def start_chat(self):
        """
        Start a chat session with the model, enabling function calling.
        """
        self.chat = self.model.start_chat(enable_automatic_function_calling=False)

    # -------------------- Example Function --------------------

    @staticmethod
    def set_light_values(brightness: int, color_temp: str) -> dict:
        """
        Set the brightness and color temperature of a room light. (mock API).
        :param brightness: Light level from 0 to 100. Zero is off and 100 is full brightness.
        :param color_temp: Color temperature, which can be `daylight`, `cool`, or `warm`.
        :return: A dictionary containing the set brightness and color temperature.
        """
        return {
            "brightness": brightness,
            "colorTemperature": color_temp
        }

    # -------------------- Chat Interaction --------------------

    def send_message(self, user_message):
        """
        Send a message to the chat model and handle function calling.
        :param user_message: The user's input message.
        :return: The model's response.
        """
        if not self.chat:
            self.start_chat()

        # Send user message to the model
        response = self.chat.send_message(user_message)

        # Extract AI's response
        ai_responses = []
        for part in response.parts:  # Access 'parts' attribute directly
            if hasattr(part, 'content') and part.content:
                ai_responses.append(part.content)

        return ai_responses  # Return list of AI responses (if any)


    # -------------------- Django View API Methods --------------------

    def get_table_data(self, table_name):
        """
        Retrieve data for a specific table from the Django backend.
        :param table_name: Name of the table (e.g., 'user_info', 'education').
        :return: Data retrieved from the backend API.
        """
        endpoint_mapping = {
            "user_info": "user-info-json/",
            "education": "education-json/",
            "work_experience": "work-experience-json/",
            "skill": "skill-json/",
            "project": "project-json/",
            "certification": "certification-json/",
        }

        endpoint = endpoint_mapping.get(table_name)
        if not endpoint:
            return {"error": f"Table '{table_name}' is not supported."}

        try:
            url = f"{self.backend_base_url}/{endpoint}"
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def add_record(self, table_name, data):
        """
        Add a new record to a specific table in the Django backend.
        :param table_name: Name of the table (e.g., 'education').
        :param data: Dictionary containing the data for the new record.
        :return: Response from the backend API.
        """
        endpoint_mapping = {
            "education": "education-add/",
            "work_experience": "work-experience-add/",
            "skill": "skill-add/",
            "project": "project-add/",
            "certification": "certification-add/",
        }

        endpoint = endpoint_mapping.get(table_name)
        if not endpoint:
            return {"error": f"Table '{table_name}' is not supported for adding records."}

        try:
            url = f"{self.backend_base_url}/{endpoint}"
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def delete_record(self, table_name, record_id):
        """
        Delete a record from a specific table in the Django backend.
        :param table_name: Name of the table (e.g., 'education').
        :param record_id: ID of the record to be deleted.
        :return: Response from the backend API.
        """
        endpoint_mapping = {
            "education": "education-delete/",
            "work_experience": "work-experience-delete/",
            "skill": "skill-delete/",
            "project": "project-delete/",
            "certification": "certification-delete/",
        }

        endpoint = endpoint_mapping.get(table_name)
        if not endpoint:
            return {"error": f"Table '{table_name}' is not supported for deleting records."}

        try:
            url = f"{self.backend_base_url}/{endpoint}?id={record_id}"
            response = requests.delete(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    # Convenience methods for specific tables

    def get_user_info(self):
        return self.get_table_data("user_info")

    def get_education_data(self):
        return self.get_table_data("education")

    def get_work_experience_data(self):
        return self.get_table_data("work_experience")

    def get_skill_data(self):
        return self.get_table_data("skill")

    def get_project_data(self):
        return self.get_table_data("project")

    def get_certification_data(self):
        return self.get_table_data("certification")
