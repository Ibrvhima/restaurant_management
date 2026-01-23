#!/bin/bash

echo "=== DÉMARRAGE RESTAURANT MANAGEMENT ==="
echo "Date: $(date)"
echo "User: $(whoami)"
echo "Directory: $(pwd)"
echo "Python: $(python --version)"

# Configuration Django
export DJANGO_SETTINGS_MODULE=core.settings_postgresql

echo "=== VARIABLES D'ENVIRONNEMENT ==="
echo "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
echo "DATABASE_URL: $DATABASE_URL"

echo "=== VÉRIFICATION DJANGO ==="
python manage.py check --deploy

echo "=== MIGRATIONS ==="
python manage.py showmigrations
python manage.py migrate --noinput

echo "=== SUPERUTILISATEUR ==="
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
superusers = User.objects.filter(is_superuser=True)
if superusers.exists():
    print(f'✅ Superutilisateur trouvé: {superusers.count()}')
else:
    print('❌ Aucun superutilisateur - Créez-en un avec: python manage.py createsuperuser')
"

echo "=== DÉMARRAGE GUNICORN ==="
echo "Port: $PORT"
exec gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --log-level debug
