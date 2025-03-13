# guardian/urls.py
from django.urls import path
from . import views

app_name = 'guardian'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-child/', views.add_child, name='add_child'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('edit_child_profile/<int:child_id>/', views.edit_child_profile, name='edit_child_profile'),
    path('search/', views.search_professionals, name='search_professionals'),
    path('health-professional-profile/<int:health_professional_id>/', views.health_professional_profile, name='health_professional_profile'),
    path('book-appointment/<int:health_professional_id>/', views.book_appointment, name='book_appointment'),
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
   
    path('view-child/<int:child_id>/', views.view_child_profile, name='view_child_profile'),
    
    
   ]
