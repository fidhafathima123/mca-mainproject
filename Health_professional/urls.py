from django.urls import path
from . import views
from .views import *


app_name = 'health_professionals'  # Changed to match the template reference (lowercase and plural)

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),  # Keep only one dashboard path
    path('profile/edit/', views.edit_profile, name='health_professional_edit_profile'),
    path('specializations/', views.manage_specializations, name='health_professional_manage_specializations'),
    path('certifications/', views.manage_certifications, name='health_professional_manage_certifications'),
    path('profile/<int:health_professional_id>/', views.health_professional_profile, name='health_professional_profile'),
    path('list/', views.health_professional_list, name='health_professional_list'),
    path('appointments/<int:appointment_id>/respond/', views.respond_to_appointment, name='respond_to_appointment'),
    path('respond-appointment/<int:appointment_id>/', respond_to_appointment, name='respond_to_appointment'),
    path('appointment/<int:appointment_id>/video-call/', views.start_video_call, name='start_video_call'),


    
]