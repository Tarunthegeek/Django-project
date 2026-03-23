"""Database models for audit logging."""
from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    status_code = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['-timestamp']

    def __str__(self) -> str:
        username = self.user.username if self.user else 'anonymous'
        return f'{username} {self.method} {self.endpoint} [{self.status_code}]'
