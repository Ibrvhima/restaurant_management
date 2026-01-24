#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import User

def create_default_users():
    """Créer les utilisateurs par défaut"""
    User = get_user_model()
    
    # Liste des utilisateurs à créer
    users_to_create = [
        {
            'login': 'admin',
            'password': 'admin123',
            'role': 'Radmin',
            'nom': 'Administrateur',
            'prenom': 'System',
            'email': 'admin@restaurant.com',
            'telephone': '123456789',
            'actif': True
        },
        {
            'login': 'serveur1',
            'password': 'serveur123',
            'role': 'Rserveur',
            'nom': 'Serveur',
            'prenom': 'Principal',
            'email': 'serveur@restaurant.com',
            'telephone': '987654321',
            'actif': True
        },
        {
            'login': 'cuisinier1',
            'password': 'cuisinier123',
            'role': 'Rcuisinier',
            'nom': 'Cuisinier',
            'prenom': 'Chef',
            'email': 'cuisinier@restaurant.com',
            'telephone': '456789123',
            'actif': True
        },
        {
            'login': 'comptable1',
            'password': 'comptable123',
            'role': 'Rcomptable',
            'nom': 'Comptable',
            'prenom': 'Finance',
            'email': 'comptable@restaurant.com',
            'telephone': '789123456',
            'actif': True
        },
        {
            'login': 'table1',
            'password': 'table123',
            'role': 'Rtable',
            'nom': 'Table',
            'prenom': 'Client',
            'email': 'table@restaurant.com',
            'telephone': '321654987',
            'actif': True
        }
    ]
    
    created_count = 0
    updated_count = 0
    
    for user_data in users_to_create:
        login = user_data.pop('login')
        password = user_data.pop('password')
        
        try:
            user, created = User.objects.update_or_create(
                login=login,
                defaults=user_data
            )
            
            if created:
                user.set_password(password)
                user.save()
                created_count += 1
                print(f"✅ Utilisateur '{login}' créé avec succès")
            else:
                # Mettre à jour le mot de passe si l'utilisateur existe déjà
                user.set_password(password)
                user.save(**user_data)
                updated_count += 1
                print(f"🔄 Utilisateur '{login}' mis à jour")
                
        except Exception as e:
            print(f"❌ Erreur lors de la création de '{login}': {e}")
    
    print(f"\n📊 Résumé:")
    print(f"   - Utilisateurs créés: {created_count}")
    print(f"   - Utilisateurs mis à jour: {updated_count}")
    print(f"   - Total: {created_count + updated_count}")

if __name__ == '__main__':
    print("🚀 Initialisation des utilisateurs par défaut...")
    create_default_users()
    print("✅ Initialisation terminée!")
