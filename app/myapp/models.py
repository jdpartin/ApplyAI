from django.db import models

# Create your models here.

class user(models.Model):

    email = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
