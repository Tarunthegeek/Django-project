"""Admin configuration for inference app."""
from django.contrib import admin
from .models import InferenceResult, AuditLog


@admin.register(InferenceResult)
class InferenceResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'risk_level', 'risk_score', 'timestamp')
    list_filter = ('risk_level',)
    search_fields = ('user__username',)
    readonly_fields = ('input_hash', 'risk_score', 'risk_level', 'top_factors', 'timestamp')

    def has_add_permission(self, request):
        return False  # Never manually add inference results


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'risk_level', 'ip_address', 'timestamp')
    list_filter = ('action', 'risk_level')
    search_fields = ('user__username',)
    readonly_fields = ('user', 'action', 'risk_level', 'ip_address', 'details', 'timestamp')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False  # Audit logs are immutable
