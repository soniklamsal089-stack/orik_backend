#!/usr/bin/env python
"""Create a superuser for accessing the admin dashboard."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Check if superuser already exists
if User.objects.filter(is_superuser=True).exists():
    print("✓ Superuser already exists")
    superuser = User.objects.filter(is_superuser=True).first()
    print(f"  Username: {superuser.username}")
else:
    # Create superuser with environment variables or defaults
    username = os.getenv('ADMIN_USERNAME', 'admin')
    email = os.getenv('ADMIN_EMAIL', 'admin@orikwebcraft.com')
    password = os.getenv('ADMIN_PASSWORD', 'changeme123')
    
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print("✓ Superuser created successfully!")
    print(f"  Username: {username}")
    print(f"  Email: {email}")
    print(f"  Password: {password}")
    print("\n⚠️  IMPORTANT: Change the password immediately at /admin/")
