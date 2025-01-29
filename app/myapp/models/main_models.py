from django.db import models
from django.contrib.auth.models import User


class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_info")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    summary = models.TextField(blank=True, null=True) # Currently being used as career goals and additional info

    def __str__(self):
        return self.user.username


class Education(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="educations")
    school_name = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    description = models.TextField(blank=True, null=True) # Not currently used

    def __str__(self):
        return f"{self.degree} from {self.school_name}"


class WorkExperience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="work_experiences")
    job_title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    job_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"


class Skill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="skills")
    skill_name = models.CharField(max_length=255)
    years_of_experience = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.skill_name} ({self.years_of_experience} years)"


class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    project_title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    technologies_used = models.TextField(blank=True, null=True)
    project_url = models.URLField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.project_title


class Certification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="certifications")
    certification_name = models.CharField(max_length=255)
    issuing_organization = models.CharField(max_length=255)
    issue_date = models.DateField()
    expiration_date = models.DateField(blank=True, null=True)
    credential_id = models.CharField(max_length=255, blank=True, null=True)
    credential_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.certification_name
