"""Middleware that records authenticated user activity without storing payloads."""
from __future__ import annotations

from auditlogs.models import AuditLog


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        user = getattr(request, 'user', None)
        if user and user.is_authenticated and not request.path.startswith('/static/'):
            AuditLog.objects.create(
                user=user,
                endpoint=request.path,
                method=request.method,
                status_code=response.status_code,
            )
        return response
