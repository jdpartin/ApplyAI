from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from myapp.models import UserInfo, Education, WorkExperience, Skill, Project, Certification, Resume, CoverLetter
from django.shortcuts import get_object_or_404
from myapp.library.workflows.find_jobs import jobsearch_workflow
import json


# This file is for views that return JSON data


# Consolidated User Data

@login_required
def consolidated_user_data(request):
    # Fetch user info
    user_info = UserInfo.objects.filter(user=request.user).first()
    user_info_data = {
        "email": request.user.email,
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "phone_number": user_info.phone_number if user_info else None,
        "address": user_info.address if user_info else None,
        "summary": user_info.summary if user_info else None,
    } if user_info else {}

    # Fetch related data
    educations = list(Education.objects.filter(user=request.user).values())
    work_experiences = list(WorkExperience.objects.filter(user=request.user).values())
    skills = list(Skill.objects.filter(user=request.user).values())
    projects = list(Project.objects.filter(user=request.user).values())
    certifications = list(Certification.objects.filter(user=request.user).values())

    # Combine all data into a single JSON object
    consolidated_data = {
        "user_info": user_info_data,
        "educations": educations,
        "work_experiences": work_experiences,
        "skills": skills,
        "projects": projects,
        "certifications": certifications,
    }

    return JsonResponse(consolidated_data, safe=False)


# User Info

@login_required
def user_info_data(request):
    user_info = UserInfo.objects.filter(user=request.user).first()
    if user_info:
        data = {
            "email": request.user.email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "phone_number": user_info.phone_number,
            "address": user_info.address,
            "summary": user_info.summary,
        }
    else:
        data = {}
    return JsonResponse(data, safe=False)


# Education

@login_required
def education_data(request):
    educations = Education.objects.filter(user=request.user).values()
    return JsonResponse(list(educations), safe=False)


# Work Experience

@login_required
def work_experience_data(request):
    work_experiences = WorkExperience.objects.filter(user=request.user).values()
    return JsonResponse(list(work_experiences), safe=False)


# Skill

@login_required
def skill_data(request):
    skills = Skill.objects.filter(user=request.user).values()
    return JsonResponse(list(skills), safe=False)


# Project

@login_required
def project_data(request):
    projects = Project.objects.filter(user=request.user).values()
    return JsonResponse(list(projects), safe=False)


# Certification

@login_required
def certification_data(request):
    certifications = Certification.objects.filter(user=request.user).values()
    return JsonResponse(list(certifications), safe=False)


# Resume

@login_required
def resume_info(request):
    resumes = Resume.objects.filter(user=request.user).values('id', 'name', 'purpose', 'created_date')
    return JsonResponse(list(resumes), safe=False)


@login_required
def single_resume_info(request, resume_id=False):
    if not resume_id:
        resume_id = request.GET.get('id')

    if not resume_id:
        return JsonResponse({'error': 'Resume ID is required'}, status=400)

    resume = get_object_or_404(request.user.resumes, id=resume_id)

    # Prepare tailored work experience data
    work_experience_data = {
        rwe.workExperience_id: rwe.tailoredDescription
        for rwe in resume.resumeworkexperience_set.all()
    }

    # Prepare tailored project data (if applicable)
    project_data = {
        rp.project_id: rp.tailoredDescription
        for rp in resume.resumeproject_set.all()
    }

    # Construct JSON response
    resume_info = {
        "name": resume.name,
        "purpose": resume.purpose,
        "includePersonalInfo": {
            "name": request.user.first_name + " " + request.user.last_name,
            "summary": resume.tailoredSummary,
            "phone": request.user.user_info.phone_number if resume.showPhone else None,
            "email": request.user.email if resume.showEmail else None,
            "address": request.user.user_info.address if resume.showAddress else None,
        },
        "educations": [
            {
                "degree": edu.degree,
                "field_of_study": edu.field_of_study,
                "school_name": edu.school_name,
                "start_date": edu.start_date.strftime('%Y-%m-%d'),
                "end_date": edu.end_date.strftime('%Y-%m-%d') if edu.end_date else None,
            }
            for edu in resume.educations.all()
        ],
        "workExperiences": [
            {
                "title": work.job_title,
                "company": work.company_name,
                "description": work_experience_data.get(work.id) or work.job_description,
                "start_date": work.start_date.strftime('%Y-%m-%d'),
                "end_date": work.end_date.strftime('%Y-%m-%d') if work.end_date else None,
            }
            for work in resume.workExperiences.all()
        ],
        "skills": [
            {
                "name": skill.skill_name,
                "years_of_experience": skill.years_of_experience,
            }
            for skill in resume.skills.all()
        ],
        "projects": [
            {
                "title": project.project_title,
                "description": project_data.get(project.id) or project.description,
                "technologies_used": project.technologies_used,
                "url": project.project_url,
                "start_date": project.start_date.strftime('%Y-%m-%d') if project.start_date else None,
                "end_date": project.end_date.strftime('%Y-%m-%d') if project.end_date else None,
            }
            for project in resume.projects.all()
        ],
        "certifications": [
            {
                "title": cert.certification_name,
                "issuer": cert.issuing_organization,
                "issue_date": cert.issue_date.strftime('%Y-%m-%d'),
                "expiration_date": cert.expiration_date.strftime('%Y-%m-%d') if cert.expiration_date else None,
                "credential_id": cert.credential_id,
                "credential_url": cert.credential_url,
            }
            for cert in resume.certifications.all()
        ],
    }

    return JsonResponse(resume_info)



# Cover Letter

@login_required
def cover_letter_info(request):
    cover_letters = CoverLetter.objects.filter(user=request.user).values('id', 'name', 'purpose', 'created_date')
    return JsonResponse(list(cover_letters), safe=False)


@login_required
def single_cover_letter_info(request, coverletter_id=False):
    if not coverletter_id:
        coverletter_id = request.GET.get('id')

    if not coverletter_id:
        return JsonResponse({'error': 'Cover Letter ID is required'}, status=400)

    coverletter = get_object_or_404(request.user.cover_letters, id=coverletter_id)

    # Convert the cover letter to a dictionary
    coverletter_data = {
        'id': coverletter.id,
        'name': coverletter.name,
        'purpose': coverletter.purpose,
        'text': coverletter.text,
    }

    return JsonResponse(coverletter_data, safe=False)


# Job Search

@login_required
def job_search_info(request):
    if request.method == "POST":
        try:
            # Parse JSON request
            data = json.loads(request.body)

            # Extract custom filters and request details
            custom_filters = data.get("custom_filters", "")
            search_string = data.get("search_string", "")

            # Call the job search workflow
            ranked_jobs = jobsearch_workflow(request, search_string, custom_filters)

            # Return the ranked jobs as a JSON response
            return JsonResponse({"jobs": ranked_jobs}, safe=False)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        except Exception as e:
            print(e)
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)