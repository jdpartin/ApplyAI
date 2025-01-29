from django.contrib.auth.decorators import login_required
from .view_utils import json_utils  # Importing all view utilities

# This file is for views that return JSON data

# Consolidated User Data
@login_required
def consolidated_user_data(request):
    return json_utils.consolidated_user_data(request)

# User Info
@login_required
def user_info_data(request):
    return json_utils.user_info_data(request)

# Education
@login_required
def education_data(request):
    return json_utils.education_data(request)

# Work Experience
@login_required
def work_experience_data(request):
    return json_utils.work_experience_data(request)

# Skill
@login_required
def skill_data(request):
    return json_utils.skill_data(request)

# Project
@login_required
def project_data(request):
    return json_utils.project_data(request)

# Certification
@login_required
def certification_data(request):
    return json_utils.certification_data(request)

# Resume
@login_required
def resume_info(request):
    return json_utils.resume_info(request)

@login_required
def single_resume_info(request, resume_id=False):
    return json_utils.single_resume_info(request, resume_id)

# Cover Letter
@login_required
def cover_letter_info(request):
    return json_utils.cover_letter_info(request)

@login_required
def single_cover_letter_info(request, coverletter_id=False):
    return json_utils.single_cover_letter_info(request, coverletter_id)

# Job Search
@login_required
def job_search_info(request):
    return json_utils.job_search_info(request)
