from myapp.library.api_managers.google_gemini import GeminiApiManager
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from myapp.views.view_utils import json_utils
import json


RELEVANCE_SCORE = None


@login_required
def ai_simulate_ats_workflow(request, custom_filters, job_info):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request type, must be POST"})

    global RELEVANCE_SCORE

    ai_tools = [
        set_job_relevance
    ]

    ai_manager = GeminiApiManager(tools=ai_tools)

    # Provide Context and Apply Filters
    user_info = json_utils.consolidated_user_data(request)
    user_info = json.loads(user_info.content.decode('utf-8'))

    # Evaluate the job vs user info
    ai_manager.send_message(f"""
        You are an AI-powered Applicant Tracking System (ATS) designed to evaluate and rank job applications based on custom instructions and career alignment criteria. 

        Here is the information for the applicant you are currently evaluating:

        User Information: {user_info}

        Additional Instructions or Filters: {custom_filters}

        Here is the information for the job you are currently evaluating the applicant's information against:

        Job Information: {job_info}

        You will grade each of the following rubric sections 0 - 3 with 0 being the worst score and 3 being the best score:

        1. Career Goal Alignment
        How well the job aligns with the applicant's stated career aspirations.

        Scores:
        3: The job closely matches the applicant's career goals, with multiple direct alignments in responsibilities, industry, and progression opportunities.
        2: The job aligns moderately well, sharing some similarities with the applicant's goals but lacking a few key elements (e.g., responsibilities or opportunities).
        1: There are noticeable gaps in alignment; only some responsibilities or opportunities match the career goals.
        0: The job does not significantly align with the applicant's stated goals.

        2. Custom Filters
        How well the job meets the applicant's non-negotiable criteria such as location, salary, and required skills.

        Scores:
        3: The job meets all custom filter criteria (e.g., location, salary, skills).
        2: The job meets most custom filter criteria but is slightly off in one or two areas (e.g., lower salary, different location preference).
        1: The job meets only some of the custom filters; critical preferences like location or required skills may be unmet.
        0: The job fails to meet most or all custom filters.

        3. Experience Match
        How well the applicant's skills, qualifications, and experience align with the job requirements.

        Scores:
        3: The applicant has all required skills, qualifications, and significant relevant experience for the role.
        2: The applicant meets most requirements but may lack a few specific skills or qualifications.
        1: The applicant has some relevant experience or qualifications but is missing key elements.
        0: The applicant has little or no relevant experience or qualifications for the role.

        Reply to this message with your scores. Do not call a function.
    """)

    # Evaluate the answer for quality control
    ai_manager.send_message(f"""
        Next, evaluate your answer to ensure it meets the following standards:

        - Do not hallucinate any information, use only information provided in this chat.
        - Follow the provided instructions strictly
        - Ensure your answer meets the rubric criteria and is accurate

        Reply to this message with your final scores. Do not call a function.
    """)

    # Assign a compatibility percentage
    ai_manager.send_message(f"""
        Based on the scores you provided and the applicant vs job information, assign a score from 0-100 using the following criteria.

        0% - 50%: The application is not relevant, it scored poorly in two or more sections or does not meet non-negotiable standards set by the applicant.
        50% - 75%: The application may be partially relevant, it partially aligns with the stated goals and qualifications of the applicant and meets all non-negotiable criteria set by the user.
        75% - 99%: The application is relevant, it scored well in all sections and the applicant would be a moderately strong candidate, it aligns well withe their career goals and meets all non-negotiable criteria.
        100%: This is a dream application that the applicant will be the perfect candidate for. This job was made for them.

        Call the 'set_job_relevance' function to provide your score as a number between 0 and 100.
    """)

    return RELEVANCE_SCORE




# AI Tools
def set_job_relevance(relevance_score: int):
    """
    Sets the relevance score of the job being evaluated.
    Args:
        relevance_score (integer): A score from 0 to 100 indicating how relevant the job is to the applicant
    """
    global RELEVANCE_SCORE

    if not relevance_score or relevance_score > 100 or relevance_score < 0:
        raise ValueError("Relevance score must be an integer between 0 and 100")
    
    RELEVANCE_SCORE = relevance_score