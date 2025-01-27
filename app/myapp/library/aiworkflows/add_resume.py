from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from myapp.models import *
import google.generativeai as genai
from typing import List
from .common import get_data, EntityType
from django.conf import settings
from django.contrib.auth.decorators import login_required
import json


GEMINI_API_KEY = settings.GEMINI_API_KEY
GEMINI_MODEL = "gemini-1.5-flash-8b"
CHAT = None
CURRENT_REQUEST = None

RESUME_INFO = {
    "name": "",
    "purpose": "",
    "includePersonalInfo": {
        "tailoredSummary": "",
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

ADDITIONAL_INFO = {
    "resume_description": "",
    "summarized_resume_description": "",
}

FUNCTIONS_CALLED = []


@login_required
def ai_add_resume_workflow(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request type, must be POST"})

    global CHAT, ADDITIONAL_INFO, CURRENT_REQUEST, RESUME_INFO

    resume_description = request.POST.get("resume_description")
    if not resume_description:
        return JsonResponse({"error": "A resume description must be provided"})

    ADDITIONAL_INFO["resume_description"] = resume_description
    CURRENT_REQUEST = request


    # Configure AI Model

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(model_name=GEMINI_MODEL, tools=[
        report_issue,
        set_summarized_resume_description,
        set_resume_name_and_purpose,
        set_skill_relevance,
        set_certification_relevance,
        set_education_relevance,
        set_work_experience_relevance,
        set_project_relevance,
        set_work_experience_description,
        set_project_description,
        set_professional_summary
    ])

    CHAT = model.start_chat(enable_automatic_function_calling=True)


    # Helper Functions

    def send_message(message, mandatory_function_calls=[]):
        global CHAT, FUNCTIONS_CALLED

        response = None

        print("SYSTEM: " + message)

        try:
            response = CHAT.send_message(message)

        except Exception as e:
            print(f"Error during message processing: {e}")
            response = CHAT.send_message(f"An error occurred: {e}. Please ensure your response meets the requirements and retry.")

        print("AI: " + response.text)

        for function_name in mandatory_function_calls:
            if not function_name in FUNCTIONS_CALLED:
                send_message("The requested function is mandatory. Please call the requested function, or call the function 'report_issue' to log why you could not.")

        FUNCTIONS_CALLED = []


    def ensure_section_relevance(section_name: str, model_queryset, add_function, tailored=False):
        global RESUME_INFO

        # Check if there are any existing items in the section
        existing_items = RESUME_INFO.get(section_name, [])
        if not existing_items:
            print(f"No entries found in {section_name}, adding all by default.")

            for item in model_queryset:
                if tailored:
                    # Call the add function with tailored description as None (placeholder)
                    add_function(item.id, tailored_description=None)
                else:
                    # Call the add function without tailored description
                    add_function(item.id)

        else:
            print(f"Entries already exist in {section_name}, no default additions needed.")


    # AI Chat

    # Provide Context
    send_message(f"""
        This is an automated process to create a tailored resume.
        - Follow resume best practices.
        - Do not hallucinate any information that was not given to you in this conversation.
        Simply say 'OK'. Do not call a function.
    """)

    # Summarize The Resume Description
    send_message(f"""
        Below is the user input. It is either a description of the desired resume, or a job description that you should tailor the resume to.

        {resume_description}

        Call the function 'set_summarized_resume_description' and pass a sumarized description of the purpose of this resume, 
        it should retain all relevant details that may be needed later.

        Once you have called the function simply reply 'OK'
    """, 
    mandatory_function_calls=[
        'set_summarized_resume_description'
    ])

    # Resume Name and Purpose
    send_message(f"""
        Based on the sumarized description you just created, please decide on a name, and purpose for the resume. 
        name: A brief and descriptive name for this resume. 
        purpose: A very short note to help the applicant remember what the resume is for, 1-2 sentences. 

        Call the function 'set_resume_name_and_purpose' and pass the name and purpose.

        Once you have called the function simply reply 'OK'
    """,
    mandatory_function_calls=[
        'set_resume_name_and_purpose'
    ])


    # Choose Skills
    if request.user.skills.exists():
        send_message(f"""
            We will now choose which of the applicant's skills are relevant to this resume.

            When making your choices, keep in mind the purpose of this resume: 
        
            {ADDITIONAL_INFO["summarized_resume_description"]}

            Simply reply 'OK'. Do not call a function.
        """)

        for skill in request.user.skills.all():
            send_message(f"""
                Based on the resume's purpose, is the following skill relevant?

                Skill ID: {skill.id} 
                Skill Name: {skill.skill_name} 

                Call the function 'set_skill_relevance' and pass the skill id and is_relevant parameters. 

                Once you have called the function simply reply 'OK'
            """,
            mandatory_function_calls=[
                'set_skill_relevance'
            ])

        send_message(f"""
            Now we will review the skills in this resume. Here are the skill ids that will be included:

            {json.dumps(RESUME_INFO['skills'])}

            Ensure at least a few skills are provided even if they are less relevant.

            If no changes are needed reply 'OK'. If you need to add more skills call the 'set_skill_relevance' to add them one at a time.
        """)


    # Choose Certifications
    if request.user.certifications.exists():
        send_message(f"""
            We will now choose which of the applicant's certifications are relevant to this resume.

            When making your choices, keep in mind the purpose of this resume: 
        
            {ADDITIONAL_INFO["summarized_resume_description"]} 

            Simply reply 'OK'. Do not call a function. 
        """)

        for certification in request.user.certifications.all():
            send_message(f"""
                Based on the resume's purpose, is the following certification relevant? 

                Certification ID: {certification.id} 
                Certification Vendor: {certification.issuing_organization} 
                Certification Name: {certification.certification_name} 

                Call the function 'set_certification_relevance' and pass the certification id and is_relevant parameters. 

                Once you have called the function simply reply 'OK'
            """,
            mandatory_function_calls=[
                'set_certification_relevance'
            ])

        send_message(f"""
            Now we will review the certifications in this resume. Here are the certification ids that will be included:

            {json.dumps(RESUME_INFO['certifications'])}

            Ensure at least a few certifications are provided even if they are less relevant.

            If no changes are needed reply 'OK'. If you need to add more certifications call the 'set_certification_relevance' to add them one at a time.
        """)


    # Choose Education
    if request.user.educations.exists():
        send_message(f"""
            We will now choose which of the applicant's educations are relevant to this resume.

            When making your choices, keep in mind the purpose of this resume: 
        
            {ADDITIONAL_INFO["summarized_resume_description"]} 

            Simply reply 'OK'. Do not call a function. 
        """)

        for education in request.user.educations.all():
            send_message(f"""
                Based on the resume's purpose, is the following education relevant? 

                Education ID: {education.id} 
                Degree: {education.degree} 
                Field of Strudy: {education.field_of_study}

                Call the function 'set_education_relevance' and pass the education id and is_relevant parameters. 

                Once you have called the function simply reply 'OK'
            """,
            mandatory_function_calls=[
                'set_education_relevance'
            ])

        send_message(f"""
            Now we will review the educations in this resume. Here are the education ids that will be included:

            {json.dumps(RESUME_INFO['educations'])}

            Ensure at least a few educations are provided even if they are less relevant.

            If no changes are needed reply 'OK'. If you need to add more educations call the 'set_education_relevance' to add them one at a time.
        """)


    # Choose Work Experience
    if request.user.work_experiences.exists():

        # Choose relevant experience

        send_message(f"""
            We will now choose which of the applicant's work experiences are relevant to this resume.

            When making your choices, keep in mind the purpose of this resume: 
        
            {ADDITIONAL_INFO["summarized_resume_description"]} 

            Simply reply 'OK'. Do not call a function. 
        """)

        for experience in request.user.work_experiences.all():
            send_message(f"""
                Based on the resume's purpose, is the following work experience relevant? 

                Work Experience ID: {experience.id} 
                Job Title: {experience.job_title} 
                Job Description: {experience.job_description}

                Call the function 'set_work_experience_relevance' and pass the work experience id and is_relevant parameters. 

                Once you have called the function simply reply 'OK'
            """,
            mandatory_function_calls=[
                'set_work_experience_relevance'
            ])

        send_message(f"""
            Now we will review the work experiences in this resume. Here are the work experience ids that will be included:

            {json.dumps(RESUME_INFO['workExperiences'])}

            Ensure at least a few work experiences are provided even if they are less relevant.

            If no changes are needed reply 'OK'. If you need to add more work experiences call the 'set_work_experience_relevance' to add them one at a time.
        """)

        # Create tailored descriptions

        send_message(f"""
            We will now create tailored descriptions for each of the work experiences that you chose as relevant to this resume.

            When creating the descriptions, keep in mind the purpose of this resume: 
        
            {ADDITIONAL_INFO["summarized_resume_description"]} 

            Simply reply 'OK'. Do not call a function. 
        """)

        for entry in RESUME_INFO["workExperiences"]:
            experience = get_object_or_404(WorkExperience, id=entry['id'], user=CURRENT_REQUEST.user)

            send_message(f"""
                Based on the resume's purpose, create a tailored description for this work experience. 

                Work Experience ID: {experience.id} 
                Job Title: {experience.job_title} 
                Job Description: {experience.job_description}

                Call the function 'set_work_experience_description' and pass the work experience id and tailored_description parameters. 

                Once you have called the function simply reply 'OK'
            """,
            mandatory_function_calls=[
                'set_work_experience_description'
            ])


    # Choose Projects
    if request.user.projects.exists():
        send_message(f"""
            We will now choose which of the applicant's projects are relevant to this resume.

            When making your choices, keep in mind the purpose of this resume: 
        
            {ADDITIONAL_INFO["summarized_resume_description"]} 

            Simply reply 'OK'. Do not call a function. 
        """)

        for project in request.user.projects.all():
            send_message(f"""
                Based on the resume's purpose, is the following projects relevant? 

                Project ID: {project.id} 
                Project Name: {project.project_title} 
                Project Description: {project.description}

                Call the function 'set_project_relevance' and pass the project id and is_relevant parameters. 

                Once you have called the function simply reply 'OK'
            """,
            mandatory_function_calls=[
                'set_project_relevance'
            ])

        send_message(f"""
            Now we will review the projects in this resume. Here are the project ids that will be included:

            {json.dumps(RESUME_INFO['projects'])}

            Ensure at least a few projects are provided even if they are less relevant.

            If no changes are needed reply 'OK'. If you need to add more projects call the 'set_project_relevance' to add them one at a time.
        """)

        # Create tailored descriptions

        send_message(f"""
            We will now create tailored descriptions for each of the projects that you chose as relevant to this resume.

            When creating the descriptions, keep in mind the purpose of this resume: 
        
            {ADDITIONAL_INFO["summarized_resume_description"]} 

            Simply reply 'OK'. Do not call a function. 
        """)

        for entry in RESUME_INFO["projects"]:
            project = get_object_or_404(Project, id=entry['id'], user=CURRENT_REQUEST.user)

            send_message(f"""
                Based on the resume's purpose, create a tailored description for this project. 

                Project ID: {project.id} 
                Project Name: {project.project_title} 
                Project Description: {project.description}

                Call the function 'set_project_description' and pass the project id and tailored_description parameters. 

                Once you have called the function simply reply 'OK'
            """,
            mandatory_function_calls=[
                'set_project_description'
            ])


    # Summary
    send_message(f"""
            We will now create a professional summary for this resume. 

            - Do not include any placeholders such as [Hiring Manager Name], [Platform where you saw the ad], etc.
            - Use professional but common language. Avoid overly formal or rarely used words.
            - Use only information sourced from the provided data. Do not hallucinate or fabricate any information.
            - Maintain alignment with the purpose described earlier.
            - Include relevant ATS keywords while maintaining natural language.

            Reply with a rough draft of the summary. Do not call a function.
        """)

    send_message(f"""
            Review your summary to ensure it meets the requirements.

            - Do not include any placeholders such as [Hiring Manager Name], [Platform where you saw the ad], etc.
            - Use professional but common language. Avoid overly formal or rarely used words.
            - Use only information sourced from the provided data. Do not hallucinate or fabricate any information.
            - Maintain alignment with the purpose described earlier.
            - Include relevant ATS keywords while maintaining natural language.

            Call the function 'set_professional_summary' and pass the final draft professional summary of the resume.
        """,
        mandatory_function_calls=[
            'set_professional_summary'
        ])


    # Return Final RESUME_INFO
    return RESUME_INFO


# AI Functions

def report_issue(description: str):
    """
    Report a problem that you cannot solve on your own.
    Args:
        description (string): A description of the problem
    """
    print("The AI has reported an issue: " + description)


def set_summarized_resume_description(summarized_description: str):
    """
    Sets the summarized description of the resume being created.
    Args:
        summarized_description (string): A summary of the purpose of this resume
    Returns: Nothing
    """
    global ADDITIONAL_INFO, FUNCTIONS_CALLED

    if not summarized_description or summarized_description == "":
        raise ValueError("The parameter description (string) is a required field")

    ADDITIONAL_INFO["summarized_resume_description"] = summarized_description
    FUNCTIONS_CALLED.append('set_summarized_resume_description')
    

def set_resume_name_and_purpose(name: str, purpose: str):
    """
    Sets the name and purpose of the resume.

    Args:
        name (string): A brief and descriptive name for this resume. 
        purpose (string): A very short note to help the applicant remember what the resume is for, 1-2 sentences. 

    Returns:
        dict: An error message if validation fails, otherwise None.
    """
    global RESUME_INFO, FUNCTIONS_CALLED

    if not name or not purpose:
        raise ValueError("Name and purpose are required.")

    RESUME_INFO['name'] = name
    RESUME_INFO['purpose'] = purpose

    FUNCTIONS_CALLED.append('set_resume_name_and_purpose')


def set_skill_relevance(skill_id: int, is_relevant: bool):
    """
    Sets whether or not a skill is relevant to the resume being created.
    Args:
        skill_id (integer): The id of the skill.
        is_relevant (boolean): Whether the skill is relevant to the resume or not
    """
    global RESUME_INFO, FUNCTIONS_CALLED, CURRENT_REQUEST

    if not skill_id or not is_relevant:
        raise ValueError("Skill id and is relevant parameters are required")

    if is_relevant:
        skill = get_object_or_404(Skill, id=skill_id, user=CURRENT_REQUEST.user)

        RESUME_INFO.setdefault('skills', []).append({
            "id": skill.id,
        })

    FUNCTIONS_CALLED.append('set_skill_relevance')


def set_certification_relevance(certification_id: int, is_relevant: bool):
    """
    Sets whether or not a certification is relevant to the resume being created.
    Args:
        certification_id (integer): The id of the certification.
        is_relevant (boolean): Whether the certification is relevant to the resume or not
    """
    global RESUME_INFO, FUNCTIONS_CALLED, CURRENT_REQUEST

    if not certification_id or not is_relevant:
        raise ValueError("Certification id and is relevant parameters are required")

    if is_relevant:
        certification = get_object_or_404(Certification, id=certification_id, user=CURRENT_REQUEST.user)

        RESUME_INFO.setdefault('certifications', []).append({
            "id": certification.id,
        })

    FUNCTIONS_CALLED.append('set_certification_relevance')


def set_education_relevance(education_id: int, is_relevant: bool):
    """
    Sets whether or not a ceducation is relevant to the resume being created.
    Args:
        education_id (integer): The id of the education.
        is_relevant (boolean): Whether the education is relevant to the resume or not
    """
    global RESUME_INFO, FUNCTIONS_CALLED, CURRENT_REQUEST

    if not education_id or not is_relevant:
        raise ValueError("Education id and is relevant parameters are required")

    if is_relevant:
        education = get_object_or_404(Education, id=education_id, user=CURRENT_REQUEST.user)

        RESUME_INFO.setdefault('educations', []).append({
            "id": education.id,
        })

    FUNCTIONS_CALLED.append('set_education_relevance')


def set_work_experience_description(work_experience_id: int, tailored_description: str):
    """
    Sets the tailored description of the work experience for the resume being created.

    Args:
        work_experience_id (integer): The id of the work experience.
        tailored_description (string): The tailored description for this work experience based on the purpose of this resume.

    Returns:
        None
    """
    global RESUME_INFO, FUNCTIONS_CALLED

    if not work_experience_id or not tailored_description:
        raise ValueError("Work experience id and tailored description are required parameters.")

    for experience in RESUME_INFO["workExperiences"]:
        if experience["id"] == work_experience_id:
            experience["tailoredSummary"] = tailored_description
            break
    else:
        raise ValueError(f"Work experience with id {work_experience_id} was not found in RESUME_INFO.")

    FUNCTIONS_CALLED.append('set_work_experience_description')


def set_project_description(project_id: int, tailored_description: str):
    """
    Sets the tailored description of the project for the resume being created.

    Args:
        project_id (integer): The id of the project.
        tailored_description (string): The tailored description for this project based on the purpose of this resume.

    Returns:
        None
    """
    global RESUME_INFO, FUNCTIONS_CALLED

    if not project_id or not tailored_description:
        raise ValueError("Project id and tailored description are required parameters.")

    for project in RESUME_INFO["projects"]:
        if project["id"] == project_id:
            project["tailoredSummary"] = tailored_description
            break
    else:
        raise ValueError(f"Project with id {project_id} was not found in RESUME_INFO.")

    FUNCTIONS_CALLED.append('set_project_description')


def set_work_experience_relevance(work_experience_id: int, is_relevant: bool):
    """
    Sets whether or not a work experience is relevant to the resume being created.

    Args:
        work_experience_id (integer): The id of the work experience.
        is_relevant (boolean): Whether the work experience is relevant to the resume or not.

    Returns:
        None
    """
    global RESUME_INFO, FUNCTIONS_CALLED, CURRENT_REQUEST

    if work_experience_id is None or is_relevant is None:
        raise ValueError("Work experience id and is_relevant parameters are required.")

    if is_relevant:
        work_experience = get_object_or_404(WorkExperience, id=work_experience_id, user=CURRENT_REQUEST.user)
        RESUME_INFO.setdefault('workExperiences', []).append({
            "id": work_experience.id,
            "tailoredSummary": None
        })

    FUNCTIONS_CALLED.append('set_work_experience_relevance')


def set_project_relevance(project_id: int, is_relevant: bool):
    """
    Sets whether or not a project is relevant to the resume being created.

    Args:
        project_id (integer): The id of the project.
        is_relevant (boolean): Whether the project is relevant to the resume or not.

    Returns:
        None
    """
    global RESUME_INFO, FUNCTIONS_CALLED, CURRENT_REQUEST

    if project_id is None or is_relevant is None:
        raise ValueError("Project id and is_relevant parameters are required.")

    if is_relevant:
        project = get_object_or_404(Project, id=project_id, user=CURRENT_REQUEST.user)
        RESUME_INFO.setdefault('projects', []).append({
            "id": project.id,
            "tailoredSummary": None
        })

    FUNCTIONS_CALLED.append('set_project_relevance')


def set_professional_summary(summary: str):
    """
    Sets the professional summary of the resume being created.
    Args:
        summary (string): The professional summary for the resume.
    """
    global RESUME_INFO, FUNCTIONS_CALLED

    if not summary:
        raise ValueError("Summary is required")

    RESUME_INFO["includePersonalInfo"]["summary"] = summary

    FUNCTIONS_CALLED.append('set_professional_summary')
