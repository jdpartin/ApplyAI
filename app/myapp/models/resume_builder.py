from django.db import models
from django.contrib.auth.models import User
from .main_models import *


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="resumes")
    name = models.TextField(max_length=255)
    purpose = models.TextField(blank=True, null=True)
    workExperiences = models.ManyToManyField(WorkExperience, through="ResumeWorkExperience", related_name="resumes")

    def __str__(self):
        return self.name

class ResumeWorkExperience(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    workExperience = models.ForeignKey(WorkExperience, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)  # Example additional field

    class Meta:
        ordering = ["order"]  # Order jobs in the resume

    def __str__(self):
        return f"{self.resume.name} - {self.job.title}"
