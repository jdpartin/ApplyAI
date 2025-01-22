from django.db import models
from django.contrib.auth.models import User


class CoverLetter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cover_letters")

    name = models.CharField(max_length=255, blank=True, null=True)
    purpose = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField(blank=True, null=True)

    created_date = models.DateField(auto_now_add=True)  # Automatically sets the date when the object is created

    def __str__(self):
        return self.name