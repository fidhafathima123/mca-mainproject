# Create a new file: child/forms.py

from django import forms
from .models import TaskSubmission, Task

class TaskSubmissionForm(forms.ModelForm):
    class Meta:
        model = TaskSubmission
        fields = ['submission_file', 'submission_type', 'comments']
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 3}),
            'submission_type': forms.RadioSelect(),
        }

# Create a new file: trainer/forms.py (or add to existing file)

