from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings 

class HealthProfessional(models.Model):
    PROFESSION_CHOICES = [
        ('doctor', 'Doctor'),
        ('nutritionist', 'Nutritionist'),
        ('physiotherapist', 'Physiotherapist'),
        ('psychologist', 'Psychologist'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profession = models.CharField(max_length=50, choices=PROFESSION_CHOICES)
    profile_picture = models.ImageField(upload_to='health_professional_profiles/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    address = models.TextField(blank=True)
    license_number = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"{self.user.username} {self.user.last_name} ({self.get_profession_display()})"

class Specialization(models.Model):
    health_professional = models.ForeignKey(HealthProfessional, related_name='specializations', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    board_issuing_certificate = models.CharField(max_length=255)
    year_earned = models.IntegerField()
    def __str__(self):
        return f"{self.name} ({self.board_issuing_certificate}, {self.year_earned})"

class Certification(models.Model):
    health_professional = models.ForeignKey(HealthProfessional, related_name='certifications', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    issuing_organization = models.CharField(max_length=100)
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    certificate_file = models.FileField(upload_to='health_professional_certificates/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.issuing_organization}"
    
