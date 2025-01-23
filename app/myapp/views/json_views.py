from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from myapp.models import UserInfo, Education, WorkExperience, Skill, Project, Certification, Resume, CoverLetter
from django.shortcuts import get_object_or_404


# This file is for views that return JSON data


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


# Cover Letter

@login_required
def cover_letter_info(request):
    cover_letters = CoverLetter.objects.filter(user=request.user).values('id', 'name', 'purpose', 'created_date')
    return JsonResponse(list(cover_letters), safe=False)