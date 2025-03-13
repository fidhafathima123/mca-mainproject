from django import forms
from child.models import *
from child.models import Child
from . models import *
class TaskCreationForm(forms.ModelForm):
    # Add a new field for multiple children selection
    children = forms.ModelMultipleChoiceField(
        queryset=Child.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'subject', 'skill', 'due_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }
   
    def __init__(self, trainer, *args, **kwargs):
        super(TaskCreationForm, self).__init__(*args, **kwargs)
        # Only show children assigned to this trainer
        self.fields['children'].queryset = Child.objects.filter(
            trainer_assignments__trainer=trainer
        ).distinct()

# In forms.py
class VideoSessionForm(forms.ModelForm):
    participants = forms.ModelMultipleChoiceField(
    queryset=Child.objects.none(),
    widget=forms.CheckboxSelectMultiple(),  # Use checkboxes for clearer selection
    required=False,
    label="Select Participants"
    )
    
    class Meta:
        model = VideoSession
        fields = ['title', 'description', 'video_link', 'date', 'time', 'duration']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'video_link': forms.URLInput(attrs={'class': 'form-control'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'})
        }
    
    def __init__(self, trainer, *args, **kwargs):
        super(VideoSessionForm, self).__init__(*args, **kwargs)
        
        if trainer:
            # Get only children assigned to this trainer
            children = Child.objects.filter(trainer_assignments__trainer=trainer).distinct()
            self.fields['participants'].queryset = children
            
            # If no children are assigned, add a helpful message
            if not children.exists():
                self.fields['participants'].help_text = "No children assigned to you yet."

