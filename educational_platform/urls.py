"""
URL configuration for educational_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('admin/', admin.site.urls),
    path('accounts/login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('accounts/', include('accounts.urls')),
    path('guardian/', include('guardian.urls')),
    path('child/', include('child.urls')),
    path('trainer/',include('trainer.urls')),
    path('accounts/login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('health-professionals/', include('Health_professional.urls',namespace='health_professionals')),
    path('appointment-messages/', include('appointment_messages.urls', namespace='appointment_messages')),
     path('support/', include('support.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
