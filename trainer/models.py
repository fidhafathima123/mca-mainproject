from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Trainer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='trainer_profiles/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    address = models.TextField(blank=True)
    
    def __str__(self):
        return self.user.username

    def get_specializations(self):
        return ", ".join([spec.name for spec in self.specializations.all()])

    def get_certifications(self):
        return ", ".join([cert.name for cert in self.certifications.all()])

class Specialization(models.Model):
    Trainer = models.ForeignKey(Trainer, related_name='specializations', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    board_issuing_certificate = models.CharField(max_length=255)
    year_earned = models.IntegerField()
    def __str__(self):
        return f"{self.name} ({self.board_issuing_certificate}, {self.year_earned})"

class Certification(models.Model):
    trainer = models.ForeignKey(Trainer, related_name='certifications', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    issuing_organization = models.CharField(max_length=100)
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    certificate_file = models.FileField(upload_to='trainer_certificates/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.issuing_organization}"

# In one app (preferably trainer app)
class VideoSession(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video_link = models.URLField()
    date = models.DateField()
    time = models.TimeField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    trainer = models.ForeignKey('trainer.Trainer', on_delete=models.CASCADE, related_name='sessions')
    
    def __str__(self):
        return self.title
    
    def is_session_active(self):
        # Your existing method
        pass

class VideoSessionParticipant(models.Model):
    session = models.ForeignKey(VideoSession, on_delete=models.CASCADE, related_name='participants')
    child = models.ForeignKey('child.Child', on_delete=models.CASCADE, related_name='sessions')
    
    class Meta:
        unique_together = ('session', 'child')
    
    def __str__(self):
        return f"{self.child.user.username} in {self.session.title}"