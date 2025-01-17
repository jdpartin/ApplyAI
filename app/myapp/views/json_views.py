from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from ..models import UserInfo, Education, WorkExperience, Skill, Project, Certification
from django.shortcuts import get_object_or_404

# The modules in this file are imported in the __init__.py file (the one in the same folder)
# That is what makes these views available to the Django app
# Currently we are using * to import all modules which simplifies setup, but risks namespace pollution

# This file should contain simple views that return a JsonResponse
# Any views that render a page or form should not be put here


@login_required
def user_info_data(request):
    """
    Get information about the user
    Args: None
    Returns Name, Email, Phone, Address, LinkedIn URL, GitHub URL, PortfolioURL, and Summary in JSON format
    """
    user_info = UserInfo.objects.filter(user=request.user).first()
    if user_info:
        data = {
            "email": request.user.email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "phone_number": user_info.phone_number,
            "address": user_info.address,
            "linkedin_url": user_info.linkedin_url,
            "github_url": user_info.github_url,
            "portfolio_url": user_info.portfolio_url,
        }
    else:
        data = {}
    return JsonResponse(data, safe=False)


@login_required
def education_data(request):
    """Returns education data in JSON format."""
    educations = Education.objects.filter(user=request.user).values()
    return JsonResponse(list(educations), safe=False)

@login_required
def education_delete(request):
    """Handles deletion of an Education record."""
    education_id = request.GET.get('id')
    education = get_object_or_404(Education, id=education_id, user=request.user)

    if request.method == 'GET':
        education.delete()
        return JsonResponse({"message": "Education deleted successfully!", "status": "success"}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)


@login_required
def work_experience_data(request):
    """Returns work experience data in JSON format."""
    work_experiences = WorkExperience.objects.filter(user=request.user).values()
    return JsonResponse(list(work_experiences), safe=False)

@login_required
def work_experience_delete(request):
    """Handles deletion of a Work Experience record."""
    work_experience_id = request.GET.get('id')
    work_experience = get_object_or_404(WorkExperience, id=work_experience_id, user=request.user)

    if request.method == 'GET':
        work_experience.delete()
        return JsonResponse({"message": "Work experience deleted successfully!", "status": "success"}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)


@login_required
def skill_data(request):
    """Returns skill data in JSON format."""
    skills = Skill.objects.filter(user=request.user).values()
    return JsonResponse(list(skills), safe=False)

@login_required
def skill_delete(request):
    """Handles deletion of a Skill record."""
    skill_id = request.GET.get('id')
    skill = get_object_or_404(Skill, id=skill_id, user=request.user)

    if request.method == 'GET':
        skill.delete()
        return JsonResponse({"message": "Skill deleted successfully!", "status": "success"}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)


@login_required
def project_data(request):
    """Returns project data in JSON format."""
    projects = Project.objects.filter(user=request.user).values()
    return JsonResponse(list(projects), safe=False)

@login_required
def project_delete(request):
    """Handles deletion of a Project record."""
    project_id = request.GET.get('id')
    project = get_object_or_404(Project, id=project_id, user=request.user)

    if request.method == 'GET':
        project.delete()
        return JsonResponse({"message": "Project deleted successfully!", "status": "success"}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)


@login_required
def certification_data(request):
    """Returns certification data in JSON format."""
    certifications = Certification.objects.filter(user=request.user).values()
    return JsonResponse(list(certifications), safe=False)

@login_required
def certification_delete(request):
    """Handles deletion of a Certification record."""
    certification_id = request.GET.get('id')
    certification = get_object_or_404(Certification, id=certification_id, user=request.user)

    if request.method == 'GET':
        certification.delete()
        return JsonResponse({"message": "Certification deleted successfully!", "status": "success"}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)
