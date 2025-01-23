from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from myapp.models import Education, WorkExperience, Skill, Project, Certification, Resume, CoverLetter
from django.shortcuts import get_object_or_404


# Education

@login_required
def education_delete(request):
    education_id = request.GET.get('id')
    education = get_object_or_404(Education, id=education_id, user=request.user)

    if request.method == 'GET':
        education.delete()
        return JsonResponse({"message": "Education deleted successfully!", "status": "success"}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)


# Work Experience

@login_required
def work_experience_delete(request):
    work_experience_id = request.GET.get('id')
    work_experience = get_object_or_404(WorkExperience, id=work_experience_id, user=request.user)

    if request.method == 'GET':
        work_experience.delete()
        return JsonResponse({"message": "Work experience deleted successfully!", "status": "success"}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)


# Skill

@login_required
def skill_delete(request):
    skill_id = request.GET.get('id')
    skill = get_object_or_404(Skill, id=skill_id, user=request.user)

    if request.method == 'GET':
        skill.delete()
        return JsonResponse({"message": "Skill deleted successfully!", "status": "success"}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)


# Project

@login_required
def project_delete(request):
    project_id = request.GET.get('id')
    project = get_object_or_404(Project, id=project_id, user=request.user)

    if request.method == 'GET':
        project.delete()
        return JsonResponse({"message": "Project deleted successfully!", "status": "success"}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)


# Certification

@login_required
def certification_delete(request):
    certification_id = request.GET.get('id')
    certification = get_object_or_404(Certification, id=certification_id, user=request.user)

    if request.method == 'GET':
        certification.delete()
        return JsonResponse({"message": "Certification deleted successfully!", "status": "success"}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)


# Resume

@login_required
def resume_delete(request):
    resume_id = request.GET.get('id')

    if not resume_id:
        return JsonResponse({"error": "Resume ID is required."}, status=400)

    # Ensure the resume belongs to the current user
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    resume.delete()

    return JsonResponse({"message": "Resume deleted successfully!", "status": "success"}, status=200)


# Cover Letter

@login_required
def cover_letter_delete(request):
    cover_letter_id = request.GET.get('id')

    if not cover_letter_id:
        return JsonResponse({"error": "Cover letter ID is required."}, status=400)

    # Ensure the resume belongs to the current user
    cover_letter = get_object_or_404(CoverLetter, id=cover_letter_id, user=request.user)

    cover_letter.delete()

    return JsonResponse({"message": "Cover letter deleted successfully!", "status": "success"}, status=200)
