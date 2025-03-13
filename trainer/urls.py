from django.urls import path
from . import views
from .views import *
app_name='trainer'
urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/edit/', views.edit_profile, name='trainer_edit_profile'),
    path('specializations/', views.manage_specializations, name='trainer_manage_specializations'),
    path('certifications/', views.manage_certifications, name='trainer_manage_certifications'),
    path('profile/<int:trainer_id>/', views.trainer_profile, name='trainer_profile'),
    path('list/', views.trainer_list, name='trainer_list'),
    path('tasks/', views.manage_tasks, name='manage_tasks'),
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('view-child/<int:child_id>/', views.view_child_profile, name='view_child_profile'),

    # New URLs for video sessions
    path('sessions/', views.manage_sessions, name='manage_sessions'),
    path('sessions/create/', views.create_session, name='create_session'),
    path('sessions/<int:session_id>/', views.session_detail, name='session_detail'),
        path('create-session/', views.create_session, name='create_session'),
    path('session/<int:session_id>/', views.view_session, name='view_session'),
    
]