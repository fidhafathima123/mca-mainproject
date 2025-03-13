# child/urls.py
from django.urls import path
from . import views

app_name = 'child'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('task/<int:task_id>/', views.task_detail, name='task_detail'),
    path('session/<int:session_id>/', views.view_session_detail, name='view_session_detail'),
    path('profile/<int:child_id>/', views.child_profile, name='child_profile'), 
    path('public-profile/<int:child_id>/', views.public_profile, name='public_profile'),



]