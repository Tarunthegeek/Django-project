"""
Seed script: creates an admin + a test user.
Run: py seed.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mediscan.settings')
django.setup()

from accounts.models import CustomUser

# Admin
if not CustomUser.objects.filter(username='admin').exists():
    admin = CustomUser.objects.create_superuser(
        username='admin',
        email='admin@mediscan.local',
        password='Admin@1234',
        first_name='System',
        last_name='Admin',
    )
    admin.role = 'admin'
    admin.is_approved = True
    admin.save()
    print("[OK] Admin created -> username: admin | password: Admin@1234")
else:
    print("[--] Admin already exists")

# Test user
if not CustomUser.objects.filter(username='testuser').exists():
    user = CustomUser.objects.create_user(
        username='testuser',
        email='user@mediscan.local',
        password='User@1234',
        first_name='Test',
        last_name='User',
    )
    user.role = 'user'
    user.is_approved = True
    user.save()
    print("[OK] Test user created -> username: testuser | password: User@1234 (pre-approved)")
else:
    print("[--] Test user already exists")

print("\nDone! Run: py manage.py runserver")
