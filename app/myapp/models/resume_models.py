from django.db import models
from django.contrib.auth.models import User
from .main_models import WorkExperience, Project, Education, Skill, Certification


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="resumes")

    name = models.CharField(max_length=255)
    purpose = models.TextField(blank=True, null=True)

    showPhone = models.BooleanField(default=True)
    showEmail = models.BooleanField(default=True)
    showAddress = models.BooleanField(default=True)

    tailoredSummary = models.TextField(blank=True, null=True)

    created_date = models.DateField(auto_now_add=True)  # Automatically sets the date when the object is created

    # Associations with through classes
    workExperiences = models.ManyToManyField(WorkExperience, through="ResumeWorkExperience", related_name="resume_work_experiences")
    projects = models.ManyToManyField(Project, through="ResumeProject", related_name="resume_projects")

    # Other associations
    educations = models.ManyToManyField(Education, related_name="resume_educations")
    skills = models.ManyToManyField(Skill, related_name="resume_skills")
    certifications = models.ManyToManyField(Certification, related_name="resume_certifications")

    def __str__(self):
        return self.name


class ResumeWorkExperience(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    workExperience = models.ForeignKey(WorkExperience, on_delete=models.CASCADE)

    order = models.PositiveIntegerField(default=0)
    tailoredDescription = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["order"]  # Order jobs in the resume

    def __str__(self):
        return f"{self.resume.name} - {self.workExperience.title}"


class ResumeProject(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    order = models.PositiveIntegerField(default=0)
    tailoredDescription = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["order"]  # Order projects in the resume

    def __str__(self):
        return f"{self.resume.name} - {self.project.title}"
