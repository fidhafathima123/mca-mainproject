from django.db import models

# Create your models here.
# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('guardian', 'Guardian'),
        ('child', 'Child'),
        ('trainer', 'Trainer'),
        ('health_professional', 'Health Professional'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"