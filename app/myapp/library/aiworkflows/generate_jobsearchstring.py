from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from myapp.models import *
from .common import get_data, EntityType
from myapp.library.api_managers.google_gemini import GeminiApiManager
from .common import get_data, EntityType


CURRENT_REQUEST = None
JOB_SEARCH_STRING = None


@login_required
def ai_generate_jobsearchstring_workflow(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request type, must be POST"})

    global CURRENT_REQUEST, JOB_SEARCH_STRING

    CURRENT_REQUEST = request

    ai_tools = [
        set_job_search_string
    ]

    ai_manager = GeminiApiManager(tools=ai_tools)

    consolidated_user_data = get_data(request, EntityType.CONSOLIDATED_DATA)

    prompt = f"""
        You are an expert career advisor. Your task is to generate an optimized job search string that combines job titles and key skills based on the user's resume and career goals. 

        Input:
        Here is the consolidated data for the user. The summary should be seen as a career description/additional info section.

        {consolidated_user_data}

        Output:
        Create a search string optimized for job search APIs like Adzuna. The search string should:
        1. Include job titles that match the user's skills and career goals.
        2. Highlight key skills and technologies mentioned in the resume or relevant to the career goals.
        3. Be concise but comprehensive to maximize relevant job search results.
        4. Use proper formatting to separate job titles and skills logically (e.g., commas or spaces).

        Example Format:
        [Job Title 1] [Job Title 2] [Skill 1] [Skill 2] [Skill 3]

        Now, based on the input, reply with the job search string. Do not call a function.
    """

    response = ai_manager.send_message(prompt)

    prompt = f"""
        Now we will review.

        Please ensure that the search string you created meets the requirements:

        Create a search string optimized for job search APIs like Adzuna. The search string should:
        1. Include job titles that match the user's skills and career goals.
        2. Highlight key skills and technologies mentioned in the resume or relevant to the career goals.
        3. Be concise but comprehensive to maximize relevant job search results.
        4. Use proper formatting to separate job titles and skills logically (e.g., commas or spaces).

        Example Format:
        [Job Title 1] [Job Title 2] [Skill 1] [Skill 2] [Skill 3]

        Call the function 'set_job_search_string' to provide the final draft of your search string.
    """

    response = ai_manager.send_message(prompt)

    return JOB_SEARCH_STRING


# AI Functions

def set_job_search_string(search_string: str):
    """
    Sets the job search string you are creating.
    Args:
        search_string (string): The job search string.
    """
    global JOB_SEARCH_STRING

    if not search_string:
        raise ValueError("search_string is required")

    JOB_SEARCH_STRING = search_string