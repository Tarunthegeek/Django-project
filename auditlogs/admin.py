from django.contrib import admin

from auditlogs.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'endpoint', 'method', 'status_code', 'timestamp')
    list_filter = ('method', 'status_code', 'timestamp')
    search_fields = ('user__username', 'endpoint')
    readonly_fields = ('user', 'endpoint', 'method', 'status_code', 'timestamp')
