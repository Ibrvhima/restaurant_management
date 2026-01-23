"""
Vue d'initialisation pour créer les tables et un utilisateur par défaut
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.core.management import call_command
import os

def init_database(request):
    """Initialise la base de données et crée un utilisateur par défaut"""
    try:
        # Exécuter les migrations
        call_command('migrate', verbosity=0, interactive=False)
        
        # Créer un superutilisateur par défaut
        User = get_user_model()
        if not User.objects.filter(login='admin').exists():
            User.objects.create_superuser(
                login='admin',
                password='admin123'
            )
            return JsonResponse({
                'status': 'success',
                'message': 'Base de données initialisée avec succès!',
                'login': 'admin / admin123'
            })
        else:
            return JsonResponse({
                'status': 'exists',
                'message': 'Base de données déjà initialisée',
                'login': 'admin / admin123'
            })
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Erreur: {str(e)}'
        })
