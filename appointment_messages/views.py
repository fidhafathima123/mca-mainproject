from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

# Create your views here.
# messages/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.http import JsonResponse
from guardian.models import Appointment
from .models import Message
from Health_professional.models import HealthProfessional
from guardian.models import Guardian
from django.contrib import messages as django_messages
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Appointment, Message
from django.utils.html import format_html
@login_required
def send_message(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Security check - only allow involved parties to message
    if request.user != appointment.guardian and request.user != appointment.health_professional.user:
        django_messages.error(request, "You are not authorized to send messages for this appointment.")
        return redirect('login')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        
        if not content:
            django_messages.error(request, "Message cannot be empty.")
            return redirect(request.META.get('HTTP_REFERER', reverse('appointment_messages:conversation', args=[appointment_id])))
        
        # Determine receiver (if sender is guardian, receiver is health professional, and vice versa)
        if request.user == appointment.guardian:
            receiver = appointment.health_professional.user
        else:
            receiver = appointment.guardian
        
        # Create message
        message = Message.objects.create(
            appointment=appointment,
            sender=request.user,
            receiver=receiver,
            content=content
        )
        
        # Handle AJAX request for real-time chat updates
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        
        django_messages.success(request, "Message sent successfully.")
        return redirect(reverse('appointment_messages:conversation', args=[appointment_id]))
    
    return redirect(reverse('appointment_messages:conversation', args=[appointment_id]))
def formatted_content(self):
        return format_html(self.content)

@login_required
def conversation(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Security check - only allow involved parties to view conversation
    if request.user != appointment.guardian and request.user != appointment.health_professional.user:
        django_messages.error(request, "You are not authorized to view this conversation.")
        return redirect('login')
    
    # Get all messages for this appointment
    conversation_messages = Message.objects.filter(appointment=appointment).order_by('created_at')
    
    # Mark as read any messages where current user is the receiver
    unread_messages = conversation_messages.filter(receiver=request.user, is_read=False)
    for msg in unread_messages:
        msg.is_read = True
        msg.save()
    
    context = {
        'appointment': appointment,
        'messages': conversation_messages,
        'is_guardian': request.user == appointment.guardian,
    }
    
    return render(request, 'messages/conversation.html', context)

@login_required
def mark_as_read(request, message_id):
    message = get_object_or_404(Message, id=message_id, receiver=request.user)
    message.is_read = True
    message.save()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('messages:conversation', appointment_id=message.appointment.id)