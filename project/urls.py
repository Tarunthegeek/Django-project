"""URL configuration for the privacy-preserving AI deployment platform."""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from api import views as api_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/register/', api_views.RegisterView.as_view(), name='register'),
    path('', api_views.DashboardView.as_view(), name='dashboard'),
    path('', include('api.urls')),
]
