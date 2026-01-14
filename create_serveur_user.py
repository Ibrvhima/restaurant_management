#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User

# Créer un utilisateur serveur
try:
    user = User.objects.get(login='serveur1')
    print(f"L'utilisateur {user.login} existe déjà.")
except User.DoesNotExist:
    user = User.objects.create_user(
        login='serveur1',
        password='serveur123',
        role='Rserveur',
        nom='Utilisateur',
        prenom='Serveur 1'
    )
    print(f"Utilisateur {user.login} créé avec succès.")

print("\n✅ UTILISATEUR SERVEUR CRÉÉ AVEC SUCCÈS")
print("📋 Identifiants de connexion :")
print("   Login: serveur1")
print("   Mot de passe: serveur123")
print("   Rôle: Rserveur (Serveur/Servante)")
print("\n🌐 URL de connexion: http://127.0.0.1:8000/login/")
