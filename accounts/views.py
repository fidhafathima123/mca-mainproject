from django.shortcuts import render, redirect
from django.contrib.auth import login, views as auth_views
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from .forms import GuardianRegistrationForm
from .models import User

class LoginView(auth_views.LoginView):
    template_name = 'accounts/login.html'

    def get_success_url(self):
        """
        Redirect users based on their user_type after login.
        """
        user = self.request.user
        
        # Check user type and redirect accordingly
        if user.user_type == 'guardian':
            return reverse_lazy('guardian:dashboard')
        elif user.user_type == 'child':
            return reverse_lazy('child:dashboard')
        elif user.user_type == 'trainer':
            # ✅ Automatically create a Trainer profile if it does not exist
            from trainer.models import Trainer
            trainer, created = Trainer.objects.get_or_create(user=user)
            
            # Now redirect to trainer profile
            return reverse_lazy('dashboard', kwargs={'trainer_id': trainer.id})
        else:
            return reverse_lazy('home')

class GuardianRegistrationView(CreateView):
    model = User
    form_class = GuardianRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.user_type = 'guardian'
        user.save()
        
        # ✅ Create guardian profile after registration
        from guardian.models import Guardian
        Guardian.objects.create(user=user)
        
        return super().form_valid(form)

@login_required
def login_redirect(request):
    user_type = request.user.user_type
    if user_type == 'guardian':
        return redirect('guardian:dashboard')
    elif user_type == 'child':
        return redirect('child:dashboard')
    else:
        # For other user types (trainer, health professional)
        return redirect('home')
from django.contrib.auth.views import (
    PasswordResetView, 
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from django.urls import reverse_lazy

class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'accounts/password_reset_email.html'
    success_url = reverse_lazy('accounts:password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'