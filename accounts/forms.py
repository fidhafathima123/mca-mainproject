# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from guardian.models import Guardian
from child.models import Child

class GuardianRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class GuardianProfileEditForm(forms.ModelForm):
    class Meta:
        model = Guardian
        fields = ['phone_number', 'address']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ChildProfileEditForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['age']
        widgets = {
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class GuardianProfileEditForm(forms.ModelForm):
    class Meta:
        model = Guardian
        fields = ['phone_number', 'address']  # Add fields from your Guardian model

class ChildProfileEditForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['age']  # Add any other fields from your Child model