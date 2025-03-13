from django.shortcuts import render
from django.utils import timezone
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import HealthProfessional, Specialization, Certification
from django.forms import modelformset_factory
from django import forms
from guardian.models import *

class HealthProfessionalProfileForm(forms.ModelForm):
    class Meta:
        model = HealthProfessional
        fields = ['profile_picture', 'phone_number', 'bio', 'years_of_experience', 'address', 'license_number']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class SpecializationForm(forms.ModelForm):
    class Meta:
        model = Specialization
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['name', 'issuing_organization', 'issue_date', 'expiry_date', 'certificate_file']
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'required': False}),
        }
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import HealthProfessional
from appointment_messages.models import Message  # Import your Message model

@login_required
def dashboard(request):
    # Check based on user_type instead of model relationship
    if request.user.user_type != 'health_professional':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
    
    # Try to get the related health professional profile
    try:
        health_professional = HealthProfessional.objects.get(user=request.user)
    except HealthProfessional.DoesNotExist:
        # Create a new profile if one doesn't exist
        health_professional = HealthProfessional.objects.create(user=request.user)
        messages.warning(request, "Your professional profile was incomplete. Please update your information.")
    
    # Get specializations and certifications
    specializations = health_professional.specializations.all()
    certifications = health_professional.certifications.all()
    
    # Get pending and upcoming appointments
    pending_appointments = Appointment.objects.filter(
        health_professional=health_professional,
        status='pending'
    ).order_by('date')
    
    upcoming_appointments = Appointment.objects.filter(
        health_professional=health_professional,
        status='approved',
        date__gte=timezone.now().date()
    ).order_by('date')
    
    # ✅ Add unread message count for each appointment
    for appointment in upcoming_appointments:
        # ✅ This is the correct way to count unread messages
        unread_count = Message.objects.filter(
            appointment=appointment,
            receiver=request.user,
            is_read=False
        ).count()
        appointment.unread_messages_count = unread_count

    context = {
        'health_professional': health_professional,
        'specializations': specializations,
        'certifications': certifications,
        'pending_appointments': pending_appointments,
        'upcoming_appointments': upcoming_appointments,
        'pending_count': pending_appointments.count(),
    }
    
    return render(request, 'health_professionals/dashboard.html', context)

@login_required
def edit_profile(request):
    # Check if the logged-in user is a health professional
    try:
        health_professional = HealthProfessional.objects.get(user=request.user)
    except HealthProfessional.DoesNotExist:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
    
    if request.method == 'POST':
        form = HealthProfessionalProfileForm(request.POST, request.FILES, instance=health_professional)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('health_professionals:dashboard')
    else:
        form = HealthProfessionalProfileForm(instance=health_professional)
    
    context = {
        'form': form,
    }
    
    return render(request, 'health_professionals/edit_profile.html', context)

@login_required
def manage_specializations(request):
    # Check if the logged-in user is a health professional
    try:
        health_professional = HealthProfessional.objects.get(user=request.user)
    except HealthProfessional.DoesNotExist:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
   
    SpecializationFormSet = modelformset_factory(
        Specialization,
        fields=['name', 'board_issuing_certificate', 'year_earned','description'],
        extra=1,
        can_delete=True
    )
   
    if request.method == 'POST':
        formset = SpecializationFormSet(
            request.POST,
            queryset=Specialization.objects.filter(health_professional=health_professional)
        )
        
        print("POST data received:", request.POST)  # Debug print
        
        if formset.is_valid():
            print("Formset is valid")  # Debug print
            instances = formset.save(commit=False)
            
            print(f"Number of instances to save: {len(instances)}")  # Debug print
            
            for instance in instances:
                print(f"Saving instance: {instance.name}")  # Debug print
                instance.health_professional = health_professional
                instance.save()
                print(f"Instance saved with ID: {instance.id}")  # Debug print
                
            formset.save_m2m()
            
            # Debug: Check for deleted objects
            if hasattr(formset, 'deleted_objects'):
                print(f"Number of objects to delete: {len(formset.deleted_objects)}")
                for obj in formset.deleted_objects:
                    print(f"Deleting: {obj}")
                    obj.delete()
            else:
                print("No deleted_objects attribute")
               
            messages.success(request, "Specializations updated successfully.")
            return redirect('health_professionals:dashboard')
        else:
            # Print detailed form errors
            print("Formset is invalid. Errors:")
            print(formset.errors)
            print("Non-form errors:", formset.non_form_errors())
            
            for i, form in enumerate(formset.forms):
                print(f"Form {i} errors:", form.errors)
                
            messages.error(request, "There was an error updating specializations.")
    else:
        formset = SpecializationFormSet(queryset=Specialization.objects.filter(health_professional=health_professional))
   
    context = {
        'formset': formset,
    }
   
    return render(request, 'health_professionals/manage_specializations.html', context)

@login_required
def manage_certifications(request):
    # Check if the logged-in user is a health professional
    try:
        health_professional = HealthProfessional.objects.get(user=request.user)
    except HealthProfessional.DoesNotExist:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
    
    CertificationFormSet = modelformset_factory(
        Certification, 
        form=CertificationForm, 
        extra=1, 
        can_delete=True
    )
    
    if request.method == 'POST':
        formset = CertificationFormSet(
            request.POST, 
            request.FILES,
            queryset=Certification.objects.filter(health_professional=health_professional)
        )
        if formset.is_valid():
            instances = formset.save(commit=False)
            
            for instance in instances:
                instance.health_professional = health_professional
                instance.save()
            
            for obj in formset.deleted_objects:
                obj.delete()
                
            messages.success(request, "Certifications updated successfully.")
            return redirect('health_professional_dashboard')
    else:
        formset = CertificationFormSet(queryset=Certification.objects.filter(health_professional=health_professional))
    
    context = {
        'formset': formset,
    }
    
    return render(request, 'health_professionals/manage_certifications.html', context)

def health_professional_profile(request, health_professional_id):
    health_professional = get_object_or_404(HealthProfessional, id=health_professional_id)
    specializations = health_professional.specializations.all()
    certifications = health_professional.certifications.all()
    
    context = {
        'health_professional': health_professional,
        'specializations': specializations,
        'certifications': certifications,
    }
    
    return render(request, 'health_professionals/health_professional_profile.html', context)

def health_professional_list(request):
    health_professionals = HealthProfessional.objects.all()
    
    context = {
        'health_professionals': health_professionals,
    }
    
    return render(request, 'health_professionals/health_professional_list.html', context)

from django.shortcuts import get_object_or_404, render
from .models import HealthProfessional

def health_professional_profile(request, health_professional_id):
    health_professional = HealthProfessional.objects.get(user=request.user)
    specializations = health_professional.specializations.all()
    certifications = health_professional.certifications.all()
    
    context = {
        'user': request.user,
        'health_professional': health_professional,
        'specializations': specializations,
        'certifications': certifications,
    }
    
    return render(request, 'health_professionals/health_professional_profile.html', context)
# In health_professionals/views.py - modify the existing function


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def respond_to_appointment(request, appointment_id):
    # Ensure only health professionals can access this page
    if request.user.user_type != 'health_professional':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
    
    # Get the health professional object
    health_professional = get_object_or_404(HealthProfessional, user=request.user)
    
    # Fetch the appointment
    appointment = get_object_or_404(Appointment, id=appointment_id, health_professional=health_professional)
    
    # Handle POST request
    if request.method == 'POST':
        action = request.POST.get('action')
        feedback = request.POST.get('feedback', '')
        initial_message = request.POST.get('initial_message', '')
       
        # Handle approval
        if action == 'approve':
            appointment.status = 'approved'
            messages.success(request, "Appointment approved successfully!")
            
            # If there's an initial message, create it
            if initial_message:
                Message.objects.create(
                    appointment=appointment,
                    sender=request.user,
                    receiver=appointment.guardian.user,
                    content=initial_message
                )
                messages.success(request, "Initial message sent to the guardian.")
        
        # Handle rejection
        elif action == 'reject':
            appointment.status = 'rejected'
            appointment.feedback = feedback
            messages.success(request, "Appointment rejected with feedback.")
        
        # Save the appointment status
        appointment.save()
        return redirect('health_professionals:dashboard')
    
    # Render the response template with appointment details
    context = {
        'appointment': appointment,
        'child': appointment.child,
    }
    return render(request, 'health_professionals/respond_to_appointment.html', context)



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
@login_required
def start_video_call(request, appointment_id):
    if request.user.user_type != 'health_professional':
        return redirect('home')
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Generate a unique Jitsi Meet link
    unique_code = get_random_string(length=10)
    meeting_link = f'https://meet.jit.si/appointment-{appointment.id}-{unique_code}'
    
    # Send the meeting link to the Guardian as a clickable button
    message_content = f'''
        <p>Join the video call by clicking the button below:</p>
        <a href="{meeting_link}" target="_blank" 
            style="background-color: #4CAF50; color: white; 
            padding: 10px 20px; text-decoration: none; 
            border-radius: 5px; display: inline-block; font-weight: bold;">
            ✅ Join Video Call
        </a>
    '''
    
    # Create a message with the button content
    message = Message.objects.create(
        sender=request.user,
        receiver=appointment.guardian,
        content=message_content,
        appointment=appointment
    )
    
    # Redirect back to the dashboard
    return redirect('health_professionals:dashboard')