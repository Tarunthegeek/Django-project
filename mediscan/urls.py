"""MediScan URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('inference.urls')),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
]
