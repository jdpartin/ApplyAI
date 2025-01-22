from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from myapp.models import UserInfo, Education, WorkExperience, Skill, Project, Certification, Resume, CoverLetter
from django.shortcuts import get_object_or_404


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
            "linkedin_url": user_info.linkedin_url,
            "github_url": user_info.github_url,
            "portfolio_url": user_info.portfolio_url,
        }
    else:
        data = {}
    return JsonResponse(data, safe=False)

@login_required
def education_data(request):
    educations = Education.objects.filter(user=request.user).values()
    return JsonResponse(list(educations), safe=False)

@login_required
def education_delete(request):
    education_id = request.GET.get('id')
    education = get_object_or_404(Education, id=education_id, user=request.user)

    if request.method == 'GET':
        education.delete()
        return JsonResponse({"message": "Education deleted successfully!", "status": "success"}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)

@login_required
def work_experience_data(request):
    work_experiences = WorkExperience.objects.filter(user=request.user).values()
    return JsonResponse(list(work_experiences), safe=False)

@login_required
def work_experience_delete(request):
    work_experience_id = request.GET.get('id')
    work_experience = get_object_or_404(WorkExperience, id=work_experience_id, user=request.user)

    if request.method == 'GET':
        work_experience.delete()
        return JsonResponse({"message": "Work experience deleted successfully!", "status": "success"}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)

@login_required
def skill_data(request):
    skills = Skill.objects.filter(user=request.user).values()
    return JsonResponse(list(skills), safe=False)

@login_required
def skill_delete(request):
    skill_id = request.GET.get('id')
    skill = get_object_or_404(Skill, id=skill_id, user=request.user)

    if request.method == 'GET':
        skill.delete()
        return JsonResponse({"message": "Skill deleted successfully!", "status": "success"}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)

@login_required
def project_data(request):
    projects = Project.objects.filter(user=request.user).values()
    return JsonResponse(list(projects), safe=False)

@login_required
def project_delete(request):
    project_id = request.GET.get('id')
    project = get_object_or_404(Project, id=project_id, user=request.user)

    if request.method == 'GET':
        project.delete()
        return JsonResponse({"message": "Project deleted successfully!", "status": "success"}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)

@login_required
def certification_data(request):
    certifications = Certification.objects.filter(user=request.user).values()
    return JsonResponse(list(certifications), safe=False)

@login_required
def certification_delete(request):
    certification_id = request.GET.get('id')
    certification = get_object_or_404(Certification, id=certification_id, user=request.user)

    if request.method == 'GET':
        certification.delete()
        return JsonResponse({"message": "Certification deleted successfully!", "status": "success"}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)

@login_required
def resume_info(request):
    resumes = Resume.objects.filter(user=request.user).values('id', 'name', 'purpose', 'created_date')
    return JsonResponse(list(resumes), safe=False)

@login_required
def cover_letter_info(request):
    cover_letters = CoverLetter.objects.filter(user=request.user).values('id', 'name', 'purpose', 'created_date')
    return JsonResponse(list(cover_letters), safe=False)