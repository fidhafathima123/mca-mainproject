# child/views.py - Updated
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from trainer.models import *
from accounts.forms import UserEditForm
from .models import *
from .forms import TaskSubmissionForm

@login_required
def dashboard(request):
    if request.user.user_type != 'child':
        return redirect('home')
        
    child = request.user.child_profile
    guardian = child.guardian
    
    today = timezone.now().date()
    
    # Get assigned tasks
    tasks = Task.objects.filter(child=child).order_by('-created_at')
    
    # Get upcoming video sessions (today or future dates)
    upcoming_sessions = VideoSessionParticipant.objects.filter(
        child=child,
        session__date__gte=today
    ).order_by('session__date', 'session__time')
    
    # Get past sessions (dates before today)
    past_sessions = VideoSessionParticipant.objects.filter(
        child=child,
        session__date__lt=today
    ).order_by('-session__date', '-session__time')  # Note the '-' for descending order
    
    # Get completed tasks history
    completed_tasks = Task.objects.filter(
        child=child, 
        status='completed'
    ).order_by('-created_at')
    
    return render(request, 'child/dashboard.html', {
        'child': child,
        'guardian': guardian,
        'tasks': tasks,
        'upcoming_sessions': upcoming_sessions,
        'past_sessions': past_sessions,
        'completed_tasks': completed_tasks
    })

@login_required
def edit_profile(request):
    if request.user.user_type != 'child':
        return redirect('home')
        
    user = request.user
        
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
                
        if user_form.is_valid():
            user_form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('child:dashboard')
    else:
        user_form = UserEditForm(instance=user)
        
    return render(request, 'child/edit_profile.html', {
        'user_form': user_form
    })

@login_required
def task_detail(request, task_id):
    if request.user.user_type != 'child':
        return redirect('home')
    
    child = request.user.child_profile
    task = get_object_or_404(Task, id=task_id, child=child)
    
    # Check if task already has a submission
    try:
        submission = task.submission
        has_submission = True
    except TaskSubmission.DoesNotExist:
        submission = None
        has_submission = False
    
    if request.method == 'POST' and task.status == 'assigned':
        form = TaskSubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.task = task
            submission.save()
            
            # Update task status
            task.status = 'submitted'
            task.save()
            
            messages.success(request, "Task submitted successfully!")
            return redirect('child:dashboard')
    else:
        form = TaskSubmissionForm(instance=submission)
    
    return render(request, 'child/task_detail.html', {
        'task': task,
        'form': form,
        'has_submission': has_submission,
        'submission': submission
    })



@login_required
def child_profile(request, child_id):
    # Ensure only trainers or authorized users can view the profile
    if request.user.user_type != 'trainer':
        return redirect('home')

    # Get the child's profile
    child = get_object_or_404(Child, id=child_id)
    
    return render(request, 'child/child_profile.html', {
        'child': child
    })

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q  # Import Q properly

# Import models from trainer app
from trainer.models import VideoSessionParticipant
from child.models import Child

from django.utils.timezone import now
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.contrib import messages


@login_required
def view_session_detail(request, session_id):
    if request.user.user_type != 'child':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')

    try:
        child = Child.objects.get(user=request.user)
    except Child.DoesNotExist:
        messages.error(request, "Child profile not found.")
        return redirect('home')

    # Get current date and time
    current_datetime = timezone.now()

    # Fetch upcoming sessions (date-time comparison)
    upcoming_sessions = VideoSessionParticipant.objects.filter(
        child=child
    ).select_related('session').filter(
        Q(session__date__gt=current_datetime.date()) | 
        (Q(session__date=current_datetime.date()) & Q(session__time__gt=current_datetime.time()))
    ).order_by('session__date', 'session__time')

    # Fetch past sessions (date-time comparison)
    past_sessions = VideoSessionParticipant.objects.filter(
        child=child
    ).select_related('session').filter(
        Q(session__date__lt=current_datetime.date()) | 
        (Q(session__date=current_datetime.date()) & Q(session__time__lt=current_datetime.time()))
    ).order_by('-session__date', '-session__time')

    return render(request, 'child/sessions.html', {
        'upcoming_sessions': upcoming_sessions,
        'past_sessions': past_sessions,
    })


# child/views.py - Add this new view
@login_required
def public_profile(request, child_id):
    # Get the child's profile
    child = get_object_or_404(Child, id=child_id)
    
    # Check permissions - only guardian of this child, trainers, or admins can access
    if request.user.user_type not in ['trainer', 'admin'] and \
       (request.user.user_type != 'guardian' or request.user.guardian_profile != child.guardian):
        messages.error(request, "You don't have permission to view this profile.")
        return redirect('home')
    
    # Get the child's skills
    skills = ChildSkill.objects.filter(child=child)
    
    # Get task history - make sure to fetch ALL tasks regardless of status
    tasks = Task.objects.filter(child=child).order_by('-created_at')
    
    # Get task history categorized by status
    completed_tasks = tasks.filter(status='completed')
    submitted_tasks = tasks.filter(status='submitted')
    assigned_tasks = tasks.filter(status='assigned')
    subjects_list = child.subjects.split(',') 
    
    # Get video sessions the child has participated in
    past_sessions = VideoSessionParticipant.objects.filter(
        child=child,
        session__date__lt=timezone.now().date()
    ).order_by('-session__date', '-session__time')
    
    # Get upcoming sessions
    upcoming_sessions = VideoSessionParticipant.objects.filter(
        child=child,
        session__date__gte=timezone.now().date()
    ).order_by('session__date', 'session__time')
    
    # ✅ Allow trainers to see tasks
    if request.user.user_type == 'trainer':
        can_view_tasks = True
    else:
        can_view_tasks = False
    
    return render(request, 'child/public_profile.html', {
        'child': child,
        'subjects_list': subjects_list,
        'skills': skills,
        'tasks': tasks,
        'completed_tasks': completed_tasks,
        'submitted_tasks': submitted_tasks,
        'assigned_tasks': assigned_tasks,
        'past_sessions': past_sessions,
        'upcoming_sessions': upcoming_sessions,
        'is_guardian': request.user.user_type == 'guardian' and request.user.guardian_profile == child.guardian,
        'is_trainer': request.user.user_type == 'trainer',
        'can_view_tasks': can_view_tasks
    })

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

