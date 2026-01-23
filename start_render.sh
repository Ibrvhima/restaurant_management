#!/bin/bash

echo "🚀 Démarrage de Restaurant Management sur Render..."

# Configuration Django
export DJANGO_SETTINGS_MODULE=core.settings_postgresql

echo "📊 Vérification de la base de données..."
python manage.py showmigrations --plan

echo "🔄 Exécution des migrations..."
python manage.py migrate --noinput

echo "👤 Vérification du superutilisateur..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('❌ Aucun superutilisateur trouvé')
    print('📝 Créez un superutilisateur avec:')
    print('   python manage.py createsuperuser')
else:
    print('✅ Superutilisateur trouvé')
"

echo "🌐 Démarrage de Gunicorn..."
exec gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
