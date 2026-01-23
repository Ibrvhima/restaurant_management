#!/usr/bin/env python
"""
Script pour créer un superutilisateur automatiquement
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings_postgresql')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Créer un superutilisateur par défaut
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@restaurant.com',
        password='admin123'
    )
    print("✅ Superutilisateur 'admin' créé avec le mot de passe 'admin123'")
else:
    print("✅ Superutilisateur 'admin' existe déjà")

print("🎯 Login: admin / admin123")
