# guardian/forms.py
from django import forms
from accounts.models import User

class ChildRegistrationForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    age = forms.IntegerField(min_value=1, max_value=18)
    
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username
        
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords don't match.")
        
        return cleaned_data


from django import forms
from .models import Appointment
from child.models import Child

from django import forms
from .models import Appointment, Child

from django import forms
from .models import Appointment
from child.models import Child

class AppointmentForm(forms.ModelForm):
    # New fields added
    allergy_details = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        label="Does the child have any allergy? (Optional)"
    )
    
    current_medication = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        label="Is the child taking any medication currently? (Optional)"
    )
    
    class Meta:
        model = Appointment
        fields = ['child', 'date']  # Existing fields in the model
    
    def __init__(self, *args, **kwargs):
        guardian = kwargs.pop('guardian', None)
        super().__init__(*args, **kwargs)
        
        # Filter child's queryset based on guardian
        if guardian:
            self.fields['child'].queryset = Child.objects.filter(guardian=guardian)
        else:
            self.fields['child'].queryset = Child.objects.none()
        
        # Add custom placeholder text
        self.fields['child'].empty_label = "Select Child"
        self.fields['date'].widget.attrs.update({
            'placeholder': 'Select Appointment Date',
            'type': 'date'
        })
    
    def clean(self):
        cleaned_data = super().clean()
        allergy = cleaned_data.get('allergy_details')
        medication = cleaned_data.get('current_medication')
        
        # If any of the optional fields is provided, it's fine. No strict validation.
        return cleaned_data
