from myapp.models import Resume, Education, Skill, Project, Certification, WorkExperience
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json


@login_required
def add_or_update_resume(request, data=None):
    try:
        # Parse JSON body
        if not data:
            data = json.loads(request.body)

        # Check if an ID is provided for updating
        resume_id = data.get('id')
        if resume_id:
            # Fetch the existing resume
            resume = get_object_or_404(Resume, id=resume_id, user=request.user)
            # Update the existing resume fields
            resume.name = data.get('name', resume.name)
            resume.purpose = data.get('purpose', resume.purpose)
            resume.tailoredSummary = data['includePersonalInfo'].get('summary', resume.tailoredSummary)
            resume.showPhone = data['includePersonalInfo'].get('phone', resume.showPhone)
            resume.showEmail = data['includePersonalInfo'].get('email', resume.showEmail)
            resume.showAddress = data['includePersonalInfo'].get('address', resume.showAddress)
        else:
            # Create a new Resume object
            resume = Resume.objects.create(
                user=request.user,
                name=data.get('name', 'Untitled Resume'),
                purpose=data.get('purpose', ''),
                tailoredSummary=data['includePersonalInfo'].get('summary', ''),
                showPhone=data['includePersonalInfo'].get('phone', False),
                showEmail=data['includePersonalInfo'].get('email', False),
                showAddress=data['includePersonalInfo'].get('address', False)
            )

        # Clear existing related data if updating
        if resume_id:
            resume.educations.clear()
            resume.workExperiences.clear()
            resume.skills.clear()
            resume.projects.clear()
            resume.certifications.clear()

        # Add related data (Education, WorkExperience, Skills, etc.)
        # 1. Education
        education_ids = [item['id'] for item in data.get('educations', [])]
        educations = Education.objects.filter(id__in=education_ids)
        resume.educations.add(*educations)

        # 2. Work Experience
        for work_experience_data in data.get('workExperiences', []):
            work_experience = get_object_or_404(WorkExperience, id=work_experience_data['id'])
            resume.workExperiences.add(work_experience, through_defaults={
                'tailoredDescription': work_experience_data.get('tailoredSummary', '')
            })

        # 3. Skills
        skill_ids = [item['id'] for item in data.get('skills', [])]
        skills = Skill.objects.filter(id__in=skill_ids)
        resume.skills.add(*skills)

        # 4. Projects
        for project_data in data.get('projects', []):
            project = get_object_or_404(Project, id=project_data['id'])
            resume.projects.add(project, through_defaults={
                'tailoredDescription': project_data.get('tailoredSummary', '')
            })

        # 5. Certifications
        certification_ids = [item['id'] for item in data.get('certifications', [])]
        certifications = Certification.objects.filter(id__in=certification_ids)
        resume.certifications.add(*certifications)

        # Save and return success
        resume.save()
        return JsonResponse({'status': 'success', 'message': 'Resume saved successfully.', 'resume_id': resume.id})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)
    except KeyError as e:
        return JsonResponse({'status': 'error', 'message': f'Missing key: {e}'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=500)
