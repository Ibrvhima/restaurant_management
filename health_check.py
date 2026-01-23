#!/usr/bin/env python
"""
Script de diagnostic pour le déploiement Render
"""
import os
import sys
import django
from django.conf import settings

def check_environment():
    """Vérifie les variables d'environnement"""
    print("=== Vérification des variables d'environnement ===")
    
    required_vars = [
        'DJANGO_SETTINGS_MODULE',
        'SECRET_KEY',
        'DEBUG'
    ]
    
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: MANQUANT")
    
    # Base de données
    db_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST']
    print("\n=== Base de données ===")
    for var in db_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: {'*' * len(value) if 'PASSWORD' in var else value}")
        else:
            print(f"❌ {var}: MANQUANT")

def check_database():
    """Test la connexion à la base de données"""
    print("\n=== Test de connexion base de données ===")
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Connexion base de données réussie")
    except Exception as e:
        print(f"❌ Erreur connexion base de données: {e}")

def check_static_files():
    """Vérifie les fichiers statiques"""
    print("\n=== Fichiers statiques ===")
    static_root = getattr(settings, 'STATIC_ROOT', None)
    if static_root and os.path.exists(static_root):
        print(f"✅ STATIC_ROOT: {static_root}")
    else:
        print(f"❌ STATIC_ROOT manquant ou inexistant")

def main():
    """Fonction principale"""
    print("🔍 Diagnostic du déploiement Restaurant Management")
    print("=" * 50)
    
    # Configuration Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings_production')
    django.setup()
    
    check_environment()
    check_database()
    check_static_files()
    
    print("\n" + "=" * 50)
    print("🏁 Diagnostic terminé")

if __name__ == '__main__':
    main()
