from django import forms
from .models import UserInfo, Education, WorkExperience, Skill, Project, Certification

class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        fields = ['phone_number', 'address', 'linkedin_url', 'github_url', 'portfolio_url', 'summary']
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 3}),
        }

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['school_name', 'degree', 'field_of_study', 'start_date', 'end_date', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        fields = ['job_title', 'company_name', 'start_date', 'end_date', 'job_description']
        widgets = {
            'job_description': forms.Textarea(attrs={'rows': 3}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['skill_name', 'proficiency_level']
        widgets = {
            'proficiency_level': forms.Select(choices=[
                ("Beginner", "Beginner"),
                ("Intermediate", "Intermediate"),
                ("Expert", "Expert"),
            ]),
        }

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project_title', 'description', 'technologies_used', 'project_url', 'start_date', 'end_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'technologies_used': forms.Textarea(attrs={'rows': 2}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['certification_name', 'issuing_organization', 'issue_date', 'expiration_date', 'credential_id', 'credential_url']
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
        }
