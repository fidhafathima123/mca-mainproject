from django.shortcuts import render

# Create your views here.
# guardian/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from accounts.models import User
from child.models import Child
from .models import Guardian
from .forms import ChildRegistrationForm
from accounts.forms import UserEditForm, GuardianProfileEditForm, ChildProfileEditForm
from accounts.models import User
from child.models import *
from .models import Guardian


@login_required
def dashboard(request):
    if request.user.user_type != 'guardian':
        return redirect('home')
    
    guardian = Guardian.objects.get(user=request.user)
    children = Child.objects.filter(guardian=guardian)
    
    # Count unread messages
    unread_count = Message.objects.filter(receiver=request.user, is_read=False).count()

    return render(request, 'guardian/dashboard.html', {
        'guardian': guardian,
        'children': children,
        'unread_count': unread_count
    })

@login_required
def add_child(request):
    if request.user.user_type != 'guardian':
        return redirect('home')
        
    if request.method == 'POST':
        form = ChildRegistrationForm(request.POST)
        if form.is_valid():
            # Create user account for child
            child_user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],  
                user_type='child'
            )
            
            # Create child profile linked to guardian
            guardian = Guardian.objects.get(user=request.user)
            child = Child.objects.create(
                user=child_user,
                guardian=guardian,
                age=form.cleaned_data['age'],
                dob = request.POST.get('dob'),
                

                medical_conditions = request.POST.get('medical_conditions', ''),

                
            )

            # Save skills
            skills = request.POST.getlist('skills[]')
            ratings = request.POST.getlist('ratings[]')
            for skill, rating in zip(skills, ratings):
                if skill:
                    ChildSkill.objects.create(
                        child=child,
                        skill_name=skill,
                        rating=int(rating)
                    )
            
            messages.success(request, f"Child account for {child_user.username} created successfully.")
            return redirect('guardian:dashboard')
    else:
        form = ChildRegistrationForm()
    
    return render(request, 'guardian/add_child.html', {'form': form})



@login_required
def edit_profile(request):
    if request.user.user_type != 'guardian':
        return redirect('home')
    
    user = request.user
    guardian = Guardian.objects.get(user=user)
    
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = GuardianProfileEditForm(request.POST, instance=guardian)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('guardian:dashboard')
    else:
        user_form = UserEditForm(instance=user)
        profile_form = GuardianProfileEditForm(instance=guardian)
    
    return render(request, 'guardian/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def edit_child_profile(request, child_id):
    if request.user.user_type != 'guardian':
        return redirect('home')
    
    # Get the child and verify guardian relationship
    child = get_object_or_404(Child, id=child_id)
    guardian = Guardian.objects.get(user=request.user)
    
    # Security check - ensure guardian is editing their own child
    if child.guardian != guardian:
        messages.error(request, "You don't have permission to edit this profile.")
        return redirect('guardian:dashboard')
    
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=child.user)
        profile_form = ChildProfileEditForm(request.POST, instance=child)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, f"{child.user.first_name}'s profile has been updated successfully.")
            return redirect('guardian:dashboard')
    else:
        user_form = UserEditForm(instance=child.user)
        profile_form = ChildProfileEditForm(instance=child)
    
    return render(request, 'guardian/edit_child_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'child': child
    })

@login_required
def view_child_profile(request, child_id):
    if request.user.user_type != 'guardian':
        return redirect('home')
        
    # Security check - ensure guardian is viewing their own child
    guardian = Guardian.objects.get(user=request.user)
    child = get_object_or_404(Child, id=child_id)
        
    if child.guardian != guardian:
        messages.error(request, "You don't have permission to view this profile.")
        return redirect('guardian:dashboard')
        
    # Redirect to the child's public profile
    return redirect('child:public_profile', child_id=child.id)

from django.db.models import Q
from trainer.models import Trainer
from Health_professional.models import HealthProfessional

@login_required
def search_professionals(request):
    query = request.GET.get('q', '')
    professional_type = request.GET.get('type', 'all')
    
    trainers = []
    health_professionals = []
    
    if query:
        if professional_type in ['all', 'trainer']:
            trainers = Trainer.objects.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(specializations__name__icontains=query) |
                Q(bio__icontains=query)
            ).distinct()
        
        if professional_type in ['all', 'health_professional']:
            # Debug: Get all health professionals first
            all_health_pros = HealthProfessional.objects.all()
            print(f"Total health professionals in database: {all_health_pros.count()}")
            
            # Print each health professional's details to verify data
            for hp in all_health_pros:
                print(f"HP ID: {hp.id}, User: {hp.user.username}, Name: {hp.user.first_name} {hp.user.last_name}, Profession: {hp.profession}")
            
            # Try a very simple query first
            basic_query = HealthProfessional.objects.filter(profession__icontains=query)
            print(f"Health professionals matching profession '{query}': {basic_query.count()}")
            
            # Try each part of the query separately
            name_query = HealthProfessional.objects.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query)
            )
            print(f"Health professionals matching name '{query}': {name_query.count()}")
            
            # Try the full query
            health_professionals = HealthProfessional.objects.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(specializations__name__icontains=query) |
                Q(bio__icontains=query) |
                Q(profession__icontains=query)
            ).distinct()
            
            print(f"Final health professionals count: {health_professionals.count()}")
    
    context = {
        'query': query,
        'professional_type': professional_type,
        'trainers': trainers,
        'health_professionals': health_professionals,
    }
    
    return render(request, 'guardian/search_professionals.html', context)


@login_required
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

@login_required
def trainer_profile(request, health_professional_id):
    trainer = get_object_or_404(Trainer, id=health_professional_id)
    specializations = trainer.specializations.all()
    certifications = trainer.certifications.all()
    
    context = {
        'trainer': trainer,
        'specializations': specializations,
        'certifications': certifications,
    }
    
    return render(request, 'trainers/trainer_profile.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from child.models import Child
from guardian.models import Appointment

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Appointment, HealthProfessional, Child, Guardian
from .forms import AppointmentForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .forms import AppointmentForm
from .models import Appointment
from child.models import Child

from guardian.models import Guardian

def book_appointment(request, health_professional_id):
    # Fetch the health professional by ID
    health_professional = get_object_or_404(HealthProfessional, id=health_professional_id)
    
    # Fetch the guardian based on the logged-in user
    guardian = get_object_or_404(Guardian, user=request.user)
    
    # Handle form submission
    if request.method == 'POST':
        form = AppointmentForm(request.POST, guardian=guardian)
        if form.is_valid():
            # Create an appointment without saving it to the database yet
            appointment = form.save(commit=False)
            appointment.guardian = guardian
            appointment.health_professional = health_professional
            appointment.status = 'pending'  # Set initial status
            
            # Capture the allergy and medication details from the form
            appointment.allergy_details = form.cleaned_data['allergy_details']
            appointment.current_medication = form.cleaned_data['current_medication']
            
            # Save the appointment to the database
            appointment.save()
            
            # Success message to the user
            messages.success(request, "Appointment request submitted successfully! Awaiting confirmation.")
            
            # Redirect to the appointment list or any other page
            return redirect('guardian:appointment_list')
        else:
            # Show error if form is invalid
            messages.error(request, "Please correct the errors below.")
    else:
        # Prepopulate the form with the guardian's children
        form = AppointmentForm(guardian=guardian)
    
    # Render the template with context
    context = {
        'form': form,
        'health_professional': health_professional,
    }
    return render(request, 'guardian/book_appointment.html', context)


from django.shortcuts import render, get_object_or_404
from appointment_messages.models import Message
from guardian.models import Guardian

def appointment_list(request):
    guardian = get_object_or_404(Guardian, user=request.user)
    appointments = Appointment.objects.filter(guardian=request.user).order_by('date')
    
    # Attach unread message count for each appointment
    for appointment in appointments:
        appointment.unread_count = appointment.messages.filter(receiver=request.user, is_read=False).count()
    
    context = {
        'appointments': appointments
    }
    return render(request, 'guardian/appointment_list.html', context)


@login_required
def cancel_appointment(request, appointment_id):
    # Check based on user_type
    if request.user.user_type != 'guardian':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
    
    appointment = get_object_or_404(Appointment, id=appointment_id, guardian=request.user)
    
    # Only allow cancelling pending appointments
    if appointment.status != 'pending':
        messages.error(request, "You can only cancel pending appointments.")
        return redirect('guardian:appointment_list')
    
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, "Appointment cancelled successfully.")
        return redirect('guardian:appointment_list')
    
    context = {
        'appointment': appointment
    }
    return render(request, 'guardian/cancel_appointment.html', context)
