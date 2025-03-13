from django.shortcuts import render
from datetime import datetime
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Trainer, Specialization, Certification
from django.forms import modelformset_factory
from django import forms
from child.models import *
from .forms import *
from django.utils import timezone
class TrainerProfileForm(forms.ModelForm):
    class Meta:
        model = Trainer
        fields = ['profile_picture', 'phone_number', 'bio', 'years_of_experience', 'address']
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

@login_required
def dashboard(request):
    # Check if the logged-in user is a trainer
    try:
        trainer = Trainer.objects.get(user=request.user)
    except Trainer.DoesNotExist:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
    
    # Fetch related data
    specializations = trainer.specializations.all()
    certifications = trainer.certifications.all()
    assigned_children = Child.objects.filter(trainer_assignments__trainer=trainer).distinct()

    # Fetch pending tasks
    pending_tasks = Task.objects.filter(
        trainer=trainer, 
        status__in=['assigned', 'submitted']
    ).order_by('due_date')

    # ✅ Correct way to get upcoming sessions for children assigned to the trainer
    now = datetime.now()
    upcoming_sessions = VideoSession.objects.filter(
    participants__child__in=assigned_children,
    date__gte=now.date(),
    time__gte=now.time()
).order_by('date', 'time').distinct()
    # Pass data to the template
    context = {
        'trainer': trainer,
        'specializations': specializations,
        'certifications': certifications,
        'assigned_children': assigned_children,
        'pending_tasks': pending_tasks,
        'upcoming_sessions': upcoming_sessions,
    }
    return render(request, 'trainers/dashboard.html', context)
    

@login_required
def edit_profile(request):
    # Check if the logged-in user is a trainer
    try:
        trainer = Trainer.objects.get(user=request.user)
    except Trainer.DoesNotExist:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
    
    if request.method == 'POST':
        form = TrainerProfileForm(request.POST, request.FILES, instance=trainer)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('trainer:dashboard')
    else:
        form = TrainerProfileForm(instance=trainer)
    
    context = {
        'form': form,
    }
    
    return render(request, 'trainers/edit_profile.html', context)
@login_required
def manage_specializations(request):
    # Check if the logged-in user is a health professional
    try:
        trainer = Trainer.objects.get(user=request.user)  # Use 'trainer' instead of 'Trainer'
    except Trainer.DoesNotExist:
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
            queryset=Specialization.objects.filter(Trainer=trainer)
        )
        
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.Trainer = trainer
                instance.save()
                
            formset.save_m2m()
            
            messages.success(request, "Specializations updated successfully.")
            return redirect('trainer:dashboard')
        else:
            messages.error(request, "There was an error updating specializations.")
    else:
        formset = SpecializationFormSet(queryset=Specialization.objects.filter(Trainer=trainer))
   
    context = {
        'formset': formset,
    }
   
    return render(request, 'trainers/manage_specializations.html', context)


@login_required
def manage_certifications(request):
    # Check if the logged-in user is a trainer
    try:
        trainer = Trainer.objects.get(user=request.user)
    except Trainer.DoesNotExist:
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
            queryset=Certification.objects.filter(trainer=trainer)
        )
        if formset.is_valid():
            instances = formset.save(commit=False)
            
            for instance in instances:
                instance.trainer = trainer
                instance.save()
            
            for obj in formset.deleted_objects:
                obj.delete()
                
            messages.success(request, "Certifications updated successfully.")
            return redirect('trainer_dashboard')
    else:
        formset = CertificationFormSet(queryset=Certification.objects.filter(trainer=trainer))
    
    context = {
        'formset': formset,
    }
    
    return render(request, 'trainers/manage_certifications.html', context)
from django.shortcuts import render, get_object_or_404
from .models import Trainer

def trainer_profile(request, trainer_id):
    trainer = get_object_or_404(Trainer.objects.prefetch_related('specializations', 'certifications'), id=trainer_id)
    
    context = {
        'trainer': trainer,
        'specializations': trainer.specializations.all(),
        'certifications': trainer.certifications.all(),
    }
    
    return render(request, 'trainers/trainer_profile.html', context)


def trainer_list(request):
    trainers = Trainer.objects.all()
    
    context = {
        'trainers': trainers,
    }
    
    return render(request, 'trainers/trainer_list.html', context)

@login_required
def manage_tasks(request):
    try:
        trainer = Trainer.objects.get(user=request.user)
    except Trainer.DoesNotExist:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
   
    # Get all tasks created by this trainer
    all_tasks = Task.objects.filter(trainer=trainer).order_by('-created_at')
    
    # Filter tasks by status
    assigned_tasks = all_tasks.filter(status="assigned")
    submitted_tasks = all_tasks.filter(status="submitted") 
    completed_tasks = all_tasks.filter(status="completed")
   
    context = {
        'all_tasks': all_tasks,
        'assigned_tasks': assigned_tasks,
        'submitted_tasks': submitted_tasks,
        'completed_tasks': completed_tasks,
    }
   
    return render(request, 'trainers/manage_tasks.html', context)
@login_required
def create_task(request):
    try:
        trainer = Trainer.objects.get(user=request.user)
    except Trainer.DoesNotExist:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
   
    if request.method == 'POST':
        form = TaskCreationForm(trainer, request.POST)
        if form.is_valid():
            # Get the children selected in the form
            selected_children = form.cleaned_data.pop('children')
            
            # Create a task for each selected child
            for child in selected_children:
                task = Task(
                    title=form.cleaned_data['title'],
                    description=form.cleaned_data['description'],
                    subject=form.cleaned_data['subject'],
                    skill=form.cleaned_data['skill'],
                    due_date=form.cleaned_data['due_date'],
                    trainer=trainer,
                    child=child
                )
                task.save()
            
            messages.success(request, f"Tasks created successfully for {len(selected_children)} children.")
            return redirect('trainer:manage_tasks')
    else:
        form = TaskCreationForm(trainer)
   
    # Check if trainer has any assigned children
    has_assigned_children = TrainerAssignment.objects.filter(trainer=trainer).exists()
   
    context = {
        'form': form,
        'has_assigned_children': has_assigned_children,
    }
   
    return render(request, 'trainers/create_task.html', context)

@login_required
def task_detail(request, task_id):
    try:
        trainer = Trainer.objects.get(user=request.user)
    except Trainer.DoesNotExist:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
    
    task = get_object_or_404(Task, id=task_id, trainer=trainer)
    
    # Check if there's a submission
    try:
        submission = task.submission
        has_submission = True
    except TaskSubmission.DoesNotExist:
        submission = None
        has_submission = False
    
    if request.method == 'POST' and task.status == 'submitted':
        # Mark task as completed
        task.status = 'completed'
        task.save()
        messages.success(request, "Task marked as completed.")
        return redirect('trainer:manage_tasks')
    
    context = {
        'task': task,
        'submission': submission,
        'has_submission': has_submission,
    }
    
    return render(request, 'trainers/task_detail.html', context)

@login_required
def manage_sessions(request):
    try:
        trainer = Trainer.objects.get(user=request.user)
    except Trainer.DoesNotExist:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
    
    # Get all sessions created by this trainer
   # If you want to sort by date first, then time
    sessions = VideoSession.objects.filter(trainer=trainer).order_by('-date', '-time')
    
    context = {
        'sessions': sessions,
    }
    
    return render(request, 'trainers/manage_sessions.html', context)

@login_required
def create_session(request):
    try:
        trainer = Trainer.objects.get(user=request.user)
    except Trainer.DoesNotExist:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
        
    if request.method == 'POST':
        form = VideoSessionForm(trainer, request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.trainer = trainer
            session.save()
            
            # Get the selected participants
            participants = form.cleaned_data.get('participants', [])
            
            # Create participant records - make sure this part is executing
            for child in participants:
                # Add debug message to verify
                print(f"Creating participant record for child: {child.id}")
                VideoSessionParticipant.objects.create(session=session, child=child)
            
            # Verify count of created participants
            count = VideoSessionParticipant.objects.filter(session=session).count()
            print(f"Created {count} participant records")
            
            messages.success(request, f"Video session created successfully with {count} participants.")
            return redirect('trainer:manage_sessions')
    else:
        form = VideoSessionForm(trainer)
    
    # Check if trainer has any assigned children
    assigned_children = Child.objects.filter(trainer_assignments__trainer=trainer)
        
    context = {
        'form': form,
        'has_assigned_children': assigned_children.exists(),
        'assigned_children': assigned_children,
    }
        
    return render(request, 'trainers/create_session.html', context)

@login_required
def session_detail(request, session_id):
    try:
        trainer = Trainer.objects.get(user=request.user)
    except Trainer.DoesNotExist:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
    
    session = get_object_or_404(VideoSession, id=session_id, trainer=trainer)
    participants = session.participants.all()
    
    context = {
        'session': session,
        'participants': participants,
    }
    
    return render(request, 'trainers/session_detail.html', context)

from django.shortcuts import render, get_object_or_404
from .models import VideoSession

def view_session(request, session_id):
    session = get_object_or_404(VideoSession, id=session_id)
    return render(request, 'trainers/view_session.html', {
        'session': session
    })

from .models import Trainer

from .models import Trainer
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render
from child.models import TrainerAssignment, Child, Trainer  # Ensure these are imported

@login_required
def view_child_profile(request, child_id):
    if request.user.user_type != 'trainer':
        return redirect('home')
    # Get trainer object for logged-in user
    trainer = get_object_or_404(Trainer, user=request.user)
    # Check if the trainer is assigned to this child
    assignment = TrainerAssignment.objects.filter(trainer=trainer, child_id=child_id).first()
   
    if not assignment:
        messages.error(request, "You don't have permission to view this child's profile.")
        return redirect('trainer:dashboard')
    
    # Redirect to the child's public profile instead of rendering directly
    return redirect('child:public_profile', child_id=child_id)



