from django.db import models

# Create your models here.
# guardian/models.py
from django.db import models
from django.conf import settings

class Guardian(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='guardian_profile')
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    
    def __str__(self):
        return f"Guardian: {self.user.username}"

from django.db import models
from django.contrib.auth.models import User
from child.models import Child
from Health_professional.models import HealthProfessional
from django.conf import settings

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    health_professional = models.ForeignKey(HealthProfessional, on_delete=models.CASCADE)
    guardian = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    allergy_details = models.TextField(blank=True, null=True)
    current_medication = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.child.user.get_full_name()} - {self.health_professional.user.get_full_name()}"
    
