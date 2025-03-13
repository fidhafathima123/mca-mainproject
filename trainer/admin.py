from django.contrib import admin
from .models import Trainer, Specialization, Certification
from django import forms
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model

User = get_user_model()

class TrainerAdminForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=True,
        label="Select User"
    )
    
    class Meta:
        model = Trainer
        fields = '__all__'


class SpecializationInline(admin.TabularInline):
    model = Specialization
    extra = 1

class CertificationInline(admin.TabularInline):
    model = Certification
    extra = 1

class TrainerAdmin(admin.ModelAdmin):
    form = TrainerAdminForm
    inlines = [SpecializationInline, CertificationInline]
    list_display = ('profile_picture_display', 'get_username', 'get_email', 'get_full_name', 
                    'years_of_experience', 'get_specializations')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'
    
    def get_specializations(self, obj):
        return obj.get_specializations()
    get_specializations.short_description = 'Specializations'

    def profile_picture_display(self, obj):
        if obj.profile_picture:
            return f'<img src="{obj.profile_picture.url}" width="40" height="40" style="border-radius:50%;">'
        return "No Image"
    profile_picture_display.allow_tags = True
    profile_picture_display.short_description = 'Profile Picture'
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new trainer
            # Get values from the form's cleaned_data
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            first_name = form.cleaned_data.get('first_name', '')
            last_name = form.cleaned_data.get('last_name', '')
            
            # Create user if it doesn't exist
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_staff': False,
                    'is_superuser': False
                }
            )
            
            # Generate random password if option is selected
            if form.cleaned_data.get('generate_password'):
                password = get_random_string(12)
                user.set_password(password)
                user.save()
                self.message_user(request, f"Generated password for {username}: {password}")
            
            obj.user = user
            
        super().save_model(request, obj, form, change)

admin.site.register(Trainer, TrainerAdmin)