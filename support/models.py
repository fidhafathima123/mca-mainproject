from django.db import models
from django.conf import settings  # Import settings instead of User directly

class SupportTicket(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )

    ISSUE_CHOICES = (
        ('technical', 'Technical Issue'),
        ('account', 'Account Problem'),
        ('feature', 'Feature Request'),
        ('billing', 'Billing Question'),
        ('other', 'Other'),
    )

    # Change this line to use settings.AUTH_USER_MODEL
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support_tickets')
    issue_type = models.CharField(max_length=20, choices=ISSUE_CHOICES)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.subject} - {self.status}"