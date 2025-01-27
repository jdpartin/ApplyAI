from myapp.models import Resume, Education, Skill, Project, Certification, WorkExperience
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json


@login_required
def add_or_update_resume(request, data=None):
    print("Add or update resume called")
    try:
        # Parse JSON body
        if not data:
            data = json.loads(request.body)
        print(f"Parsed data: {data}")

        # Check if an ID is provided for updating
        resume_id = data.get('id')
        print(f"Resume ID: {resume_id}")

        if resume_id and resume_id != 'undefined':  # Validate resume_id
            try:
                resume_id = int(resume_id)  # Convert to integer
                print(f"Validated Resume ID: {resume_id}")

                # Fetch the existing resume
                resume = get_object_or_404(Resume, id=resume_id, user=request.user)
                print(f"Fetched Resume: {resume}")

                # Update the existing resume fields
                resume.name = data.get('name', resume.name)
                resume.purpose = data.get('purpose', resume.purpose)
                resume.tailoredSummary = data['includePersonalInfo'].get('summary', resume.tailoredSummary)
                resume.showPhone = data['includePersonalInfo'].get('phone', resume.showPhone)
                resume.showEmail = data['includePersonalInfo'].get('email', resume.showEmail)
                resume.showAddress = data['includePersonalInfo'].get('address', resume.showAddress)

            except ValueError:
                print("Invalid resume ID format.")
                return JsonResponse({'status': 'error', 'message': 'Invalid resume ID.'}, status=400)
        else:
            print("Creating new resume.")
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
            print(f"Created Resume: {resume}")

        # Clear existing related data if updating
        if resume_id and resume_id != 'undefined':
            print("Clearing existing related data.")
            resume.educations.clear()
            resume.workExperiences.clear()
            resume.skills.clear()
            resume.projects.clear()
            resume.certifications.clear()

        # Add related data (Education, WorkExperience, Skills, etc.)
        print("Adding related data.")
        # 1. Education
        education_ids = [
            int(item['id']) for item in data.get('educations', [])
            if item['id'] and item['id'] != 'undefined'
        ]
        print(f"Education IDs: {education_ids}")
        educations = Education.objects.filter(id__in=education_ids)
        resume.educations.add(*educations)

        # 2. Work Experience
        for work_experience_data in data.get('workExperiences', []):
            work_experience_id = work_experience_data.get('id')
            print(f"Processing Work Experience ID: {work_experience_id}")

            if work_experience_id and work_experience_id != 'undefined':
                try:
                    work_experience = get_object_or_404(WorkExperience, id=int(work_experience_id))
                    print(f"Fetched Work Experience: {work_experience}")
                    resume.workExperiences.add(work_experience, through_defaults={
                        'tailoredDescription': work_experience_data.get('tailoredSummary', '')
                    })
                except Exception as e:
                    print(f"Error adding Work Experience {work_experience_id}: {e}")

        # 3. Skills
        skill_ids = [
            int(item['id']) for item in data.get('skills', [])
            if item['id'] and item['id'] != 'undefined'
        ]
        print(f"Skill IDs: {skill_ids}")
        skills = Skill.objects.filter(id__in=skill_ids)
        resume.skills.add(*skills)

        # 4. Projects
        for project_data in data.get('projects', []):
            project_id = project_data.get('id')
            print(f"Processing Project ID: {project_id}")

            if project_id and project_id != 'undefined':
                try:
                    project = get_object_or_404(Project, id=int(project_id))
                    print(f"Fetched Project: {project}")
                    resume.projects.add(project, through_defaults={
                        'tailoredDescription': project_data.get('tailoredSummary', '')
                    })
                except Exception as e:
                    print(f"Error adding Project {project_id}: {e}")

        # 5. Certifications
        certification_ids = [
            int(item['id']) for item in data.get('certifications', [])
            if item['id'] and item['id'] != 'undefined'
        ]
        print(f"Certification IDs: {certification_ids}")
        certifications = Certification.objects.filter(id__in=certification_ids)
        resume.certifications.add(*certifications)

        # Save and return success
        resume.save()
        print(f"Resume saved successfully: {resume.id}")
        return JsonResponse({'status': 'success', 'message': 'Resume saved successfully.', 'resume_id': resume.id})

    except json.JSONDecodeError:
        print("Invalid JSON format.")
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)
    except KeyError as e:
        print(f"Missing key: {e}")
        return JsonResponse({'status': 'error', 'message': f'Missing key: {e}'}, status=400)
    except Exception as e:
        print(f"An error occurred: {e}")
        return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=500)
