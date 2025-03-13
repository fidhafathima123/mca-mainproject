from django.db import models

# Create your models here.
# child/models.py
from django.db import models
from django.conf import settings
from guardian.models import Guardian

class Child(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='child_profile')
    guardian = models.ForeignKey(Guardian, on_delete=models.CASCADE)
    age = models.IntegerField()
    dob = models.DateField()
    subjects = models.TextField()
    medical_conditions = models.TextField()
    def __str__(self):
        return self.user.get_full_name() or self.user.username
class ChildSkill(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    skill_name = models.CharField(max_length=100)
    rating = models.IntegerField()

# Add to child/models.py

from django.db import models
from django.conf import settings
from guardian.models import Guardian
from trainer.models import Trainer
import os

class TrainerAssignment(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='trainer_assignments')
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='assigned_children')
    subject = models.CharField(max_length=100)
    skill = models.CharField(max_length=100)
    assigned_date = models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = ('child', 'trainer', 'subject', 'skill')
    
    def __str__(self):
        return f"{self.child.user.username} - {self.trainer.user.username} - {self.subject}"

class Task(models.Model):
    STATUS_CHOICES = (
        ('assigned', 'Assigned'),
        ('submitted', 'Submitted'),
        ('completed', 'Completed')
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='created_tasks')
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='assigned_tasks')
    subject = models.CharField(max_length=100)
    skill = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    
    def __str__(self):
        return self.title

def task_submission_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/task_submissions/child_<id>/<filename>
    return f'task_submissions/child_{instance.task.child.id}/{filename}'

class TaskSubmission(models.Model):
    SUBMISSION_TYPE_CHOICES = (
        ('photo', 'Photo'),
        ('video', 'Video')
    )
    
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='submission')
    submitted_at = models.DateTimeField(auto_now_add=True)
    submission_file = models.FileField(upload_to=task_submission_path)
    submission_type = models.CharField(max_length=10, choices=SUBMISSION_TYPE_CHOICES)
    comments = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Submission for {self.task.title}"
    
    def get_file_extension(self):
        return os.path.splitext(self.submission_file.name)[1].lower()

