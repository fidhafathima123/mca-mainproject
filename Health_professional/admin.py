from django.contrib import admin
from .models import HealthProfessional, Specialization, Certification
# Replace the direct User import with get_user_model
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.utils.crypto import get_random_string

class HealthProfessionalAdminForm(forms.ModelForm):
    email = forms.EmailField(required=False)
    username = forms.CharField(required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    generate_password = forms.BooleanField(required=False, initial=False, 
                                         help_text="Generate a random password for a new user")
    
    class Meta:
        model = HealthProfessional
        fields = '__all__'

class SpecializationInline(admin.TabularInline):
    model = Specialization
    extra = 1

class CertificationInline(admin.TabularInline):
    model = Certification
    extra = 1

class HealthProfessionalAdmin(admin.ModelAdmin):
    form = HealthProfessionalAdminForm
    inlines = [SpecializationInline, CertificationInline]
    list_display = ('get_username', 'get_email', 'get_full_name', 'profession', 'license_number')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'profession')
    list_filter = ('profession',)
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new health professional
            # Only create a new user if username is provided and user doesn't exist
            username = request.POST.get('username')
            if username:
                email = request.POST.get('email', '')
                first_name = request.POST.get('first_name', '')
                last_name = request.POST.get('last_name', '')
                
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
                if created and form.cleaned_data.get('generate_password'):
                    password = get_random_string(12)
                    user.set_password(password)
                    user.save()
                    self.message_user(request, f"Generated password for {username}: {password}")
                
                obj.user = user
        
        super().save_model(request, obj, form, change)

admin.site.register(HealthProfessional, HealthProfessionalAdmin)