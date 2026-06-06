"""Admin configuration for accounts app."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_approved', 'date_joined')
    list_filter = ('role', 'is_approved')
    list_editable = ('is_approved',)
    fieldsets = UserAdmin.fieldsets + (
        ('MediScan', {'fields': ('role', 'is_approved')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('MediScan', {'fields': ('role', 'is_approved')}),
    )
    actions = ['approve_users', 'revoke_approval']

    def approve_users(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} user(s) approved.")
    approve_users.short_description = "✅ Approve selected users"

    def revoke_approval(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f"{queryset.count()} user(s) approval revoked.")
    revoke_approval.short_description = "❌ Revoke approval for selected users"
