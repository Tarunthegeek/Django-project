"""Custom User model with role-based access and approval system."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_admin_role(self):
        return self.role == 'admin'

    def save(self, *args, **kwargs):
        # Admin users are auto-approved
        if self.role == 'admin':
            self.is_approved = True
            self.is_staff = True
            self.is_superuser = True
        super().save(*args, **kwargs)
