# Guide de Déploiement - Restaurant Management System

## 📋 Prérequis

### Environnement de Développement
- Python 3.8+
- MySQL 8.0+
- Git
- Node.js (pour Tailwind CSS)

### Environnement de Production
- Serveur web (Apache/Nginx)
- Python 3.8+
- MySQL/PostgreSQL
- Domaine et SSL

---

## 🚀 Étapes de Déploiement

### 1. Cloner le Repository

```bash
git clone <repository-url>
cd appdjango
```

### 2. Configurer l'Environnement

```bash
# Copier le fichier d'environnement
cp .env.example .env

# Éditer les variables
nano .env
```

**Variables à configurer :**
- `SECRET_KEY`: Clé secrète Django
- `DB_NAME`: Nom de la base de données
- `DB_USER`: Utilisateur MySQL
- `DB_PASSWORD`: Mot de passe MySQL
- `ALLOWED_HOSTS`: Domaines autorisés

### 3. Installer les Dépendances

```bash
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 4. Configurer la Base de Données

```sql
-- Créer la base de données
CREATE DATABASE restaurant_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Créer l'utilisateur (optionnel)
CREATE USER 'restaurant_user'@'localhost' IDENTIFIED BY 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON restaurant_management.* TO 'restaurant_user'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Appliquer les Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Créer le Superutilisateur

```bash
python manage.py createsuperuser
```

### 7. Collecter les Fichiers Statiques

```bash
python manage.py collectstatic
```

### 8. Démarrer le Serveur

```bash
# Développement
python manage.py runserver

# Production (avec Gunicorn)
pip install gunicorn
gunicorn core.wsgi:application --bind 0.0.0.0:8000
```

---

## 🔧 Configuration Production

### Apache avec mod_wsgi

```apache
<VirtualHost *:80>
    ServerName votre-domaine.com
    DocumentRoot /var/www/appdjango
    
    WSGIDaemonProcess restaurant-management python-path=/var/www/appdjango/venv/lib/python3.8/site-packages
    WSGIProcessGroup restaurant-management
    WSGIScriptAlias / /var/www/appdjango/core/wsgi.py
    
    Alias /static/ /var/www/appdjango/staticfiles/
    <Directory /var/www/appdjango/staticfiles>
        Require all granted
    </Directory>
    
    Alias /media/ /var/www/appdjango/media/
    <Directory /var/www/appdjango/media>
        Require all granted
    </Directory>
</VirtualHost>
```

### Nginx avec Gunicorn

```nginx
server {
    listen 80;
    server_name votre-domaine.com;
    
    location /static/ {
        alias /var/www/appdjango/staticfiles/;
    }
    
    location /media/ {
        alias /var/www/appdjango/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🔐 Sécurité Production

### 1. Variables d'Environnement
```bash
# .env
DEBUG=False
SECRET_KEY=votre-clé-secrète-très-longue
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com
```

### 2. Permissions des Fichiers
```bash
chmod 600 .env
chmod 755 manage.py
chmod -R 755 staticfiles/
```

### 3. Configuration HTTPS
- Installer SSL Certificate (Let's Encrypt recommandé)
- Rediriger HTTP vers HTTPS

---

## 📊 Scripts Utiles

### Script de Démarrage (start.sh)
```bash
#!/bin/bash
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn core.wsgi:application --bind 0.0.0.0:8000
```

### Script de Redémarrage
```bash
#!/bin/bash
sudo systemctl restart apache2  # ou nginx
sudo systemctl restart gunicorn
```

---

## 🐛 Dépannage

### Problèmes Communs

1. **Erreur de connexion MySQL**
   - Vérifier les credentials dans `.env`
   - S'assurer que MySQL est en cours d'exécution

2. **Fichiers statiques non trouvés**
   - Exécuter `python manage.py collectstatic`
   - Vérifier les permissions

3. **Erreur 500 en production**
   - Vérifier les logs : `/var/log/apache2/error.log`
   - S'assurer que `DEBUG=False`

---

## 📱 Déploiement Mobile

### Progressive Web App (PWA)
Le site est optimisé pour mobile avec :
- Design responsive
- Performance optimisée
- Navigation offline partielle

---

## 🔄 Mise à Jour

```bash
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
sudo systemctl restart apache2
```

---

## 📞 Support

Pour toute question de déploiement :
- Documentation Django officielle
- Logs du serveur
- Issues GitHub
