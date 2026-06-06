"""URL patterns for the inference app."""
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('infer/', views.infer, name='infer'),
    path('history/', views.history, name='history'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('audit/', views.audit, name='audit'),
]
