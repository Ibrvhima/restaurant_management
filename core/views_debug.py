"""
Vue de debug pour diagnostiquer les problèmes
"""
from django.http import JsonResponse
from django.db import connection
from django.core.management import call_command
from django.contrib.auth import get_user_model
import os

def debug_info(request):
    """Retourne des informations de debug"""
    try:
        # Test de connexion à la base de données
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "OK"
    except Exception as e:
        db_status = f"ERREUR: {str(e)}"
    
    # Vérification des variables d'environnement
    env_info = {
        'DJANGO_SETTINGS_MODULE': os.environ.get('DJANGO_SETTINGS_MODULE', 'NON DÉFINI'),
        'DATABASE_URL': os.environ.get('DATABASE_URL', 'NON DÉFINI')[:50] + '...',
        'DEBUG': os.environ.get('DEBUG', 'NON DÉFINI'),
    }
    
    # Test des tables
    tables_exist = False
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
            table_count = cursor.fetchone()[0]
            tables_exist = table_count > 0
    except:
        table_count = 0
    
    # Test des utilisateurs
    users_count = 0
    try:
        User = get_user_model()
        users_count = User.objects.count()
    except:
        pass
    
    return JsonResponse({
        'status': 'debug_info',
        'database_connection': db_status,
        'environment': env_info,
        'tables_count': table_count,
        'tables_exist': tables_exist,
        'users_count': users_count,
        'message': 'Diagnostic complet'
    })
