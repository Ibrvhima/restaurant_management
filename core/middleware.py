import os
import threading
from django.core.management import call_command
from django.db import connection
from django.contrib.auth import get_user_model
from django.http import JsonResponse

# Variables globales pour éviter les exécutions multiples
migrations_applied = False
migrations_lock = threading.Lock()

class AutoMigrationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        global migrations_applied
        
        # Vérifier si les migrations doivent être appliquées
        if not migrations_applied:
            with migrations_lock:
                if not migrations_applied:
                    try:
                        # Vérifier si la table django_session existe
                        with connection.cursor() as cursor:
                            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_session'")
                            session_table_exists = cursor.fetchone()
                        
                        if not session_table_exists:
                            # Forcer toutes les migrations
                            call_command('migrate', verbosity=0, interactive=False)
                            
                            # Créer les utilisateurs par défaut
                            User = get_user_model()
                            
                            # Superutilisateur admin
                            if not User.objects.filter(login='admin').exists():
                                User.objects.create_superuser(
                                    login='admin',
                                    password='admin123'
                                )
                            
                            # Utilisateurs de test
                            if not User.objects.filter(login='manager').exists():
                                User.objects.create_user(
                                    login='manager',
                                    password='manager123',
                                    role='Rmanager'
                                )
                            
                            if not User.objects.filter(login='employe').exists():
                                User.objects.create_user(
                                    login='employe',
                                    password='employe123',
                                    role='Remploye'
                                )
                        
                        migrations_applied = True
                        
                    except Exception as e:
                        # En cas d'erreur, essayer une fois de plus
                        try:
                            call_command('migrate', verbosity=0, interactive=False)
                            User = get_user_model()
                            
                            # Créer les utilisateurs par défaut même en cas d'erreur
                            if not User.objects.filter(login='admin').exists():
                                User.objects.create_superuser(
                                    login='admin',
                                    password='admin123'
                                )
                            
                            if not User.objects.filter(login='manager').exists():
                                User.objects.create_user(
                                    login='manager',
                                    password='manager123',
                                    role='Rmanager'
                                )
                            
                            if not User.objects.filter(login='employe').exists():
                                User.objects.create_user(
                                    login='employe',
                                    password='employe123',
                                    role='Remploye'
                                )
                            
                            migrations_applied = True
                        except:
                            pass

        response = self.get_response(request)
        return response
