"""Models for inference results and audit logs."""
from django.db import models
from django.conf import settings


class InferenceResult(models.Model):
    RISK_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inference_results'
    )
    input_hash = models.CharField(max_length=64, db_index=True)
    risk_score = models.FloatField()
    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS)
    top_factors = models.JSONField(default=list)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} | {self.risk_level} ({self.risk_score:.1f}) | {self.timestamp:%Y-%m-%d %H:%M}"

    @property
    def risk_color(self):
        return {
            'low': 'emerald',
            'medium': 'yellow',
            'high': 'orange',
            'critical': 'red',
        }.get(self.risk_level, 'gray')


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('inference_run', 'Inference Run'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('access_denied', 'Access Denied'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=30, choices=ACTION_CHOICES, default='inference_run')
    risk_level = models.CharField(max_length=10, blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    details = models.TextField(blank=True, default='')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} | {self.action} | {self.timestamp:%Y-%m-%d %H:%M}"

    @staticmethod
    def mask_ip(ip: str) -> str:
        """Mask last octet: 192.168.1.100 → 192.168.1.***"""
        if not ip:
            return '***'
        parts = ip.split('.')
        if len(parts) == 4:
            return '.'.join(parts[:3]) + '.***'
        return '***'
