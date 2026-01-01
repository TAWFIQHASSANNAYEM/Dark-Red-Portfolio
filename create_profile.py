#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Dark_Red_Portfolio.settings')
django.setup()

from main.models import Profile

if not Profile.objects.exists():
    Profile.objects.create(
        full_name='Your Name',
        headline='Your Headline',
        email='you@example.com',
        about='Your bio here.',
    )
    print('Profile created')
else:
    print('Profile already exists')
