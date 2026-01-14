# 📝 COMMANDES UTILES - Restaurant Management

## 🐍 Environnement virtuel

### Créer l'environnement
```bash
python -m venv venv
```

### Activer l'environnement
```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Désactiver l'environnement
```bash
deactivate
```

---

## 📦 Gestion des dépendances

### Installer toutes les dépendances
```bash
pip install -r requirements.txt
```

### Installer une nouvelle dépendance
```bash
pip install nom_du_package
pip freeze > requirements.txt  # Mettre à jour requirements.txt
```

### Mettre à jour pip
```bash
pip install --upgrade pip
```

---

## 🗄️ Base de données

### Créer la base de données
```bash
mysql -u root -p < init_database.sql
```

### Connexion à MySQL
```bash
mysql -u root -p
```

### Commandes MySQL utiles
```sql
SHOW DATABASES;
USE restaurant_db;
SHOW TABLES;
DESCRIBE users;
SELECT * FROM users;
```

---

## 🔄 Migrations Django

### Créer des migrations
```bash
python manage.py makemigrations
```

### Créer des migrations pour une app spécifique
```bash
python manage.py makemigrations accounts
```

### Appliquer toutes les migrations
```bash
python manage.py migrate
```

### Appliquer les migrations d'une app spécifique
```bash
python manage.py migrate accounts
```

### Voir l'état des migrations
```bash
python manage.py showmigrations
```

### Annuler une migration
```bash
python manage.py migrate accounts 0001  # Revenir à la migration 0001
```

### Voir le SQL d'une migration
```bash
python manage.py sqlmigrate accounts 0001
```

---

## 👤 Gestion des utilisateurs

### Créer un superutilisateur
```bash
python manage.py createsuperuser
```

### Changer le mot de passe d'un utilisateur
```bash
python manage.py changepassword ADMIN001
```

---

## 🖥️ Serveur de développement

### Lancer le serveur
```bash
python manage.py runserver
```

### Lancer sur un port différent
```bash
python manage.py runserver 8080
```

### Lancer sur une IP spécifique
```bash
python manage.py runserver 0.0.0.0:8000
```

---

## 🎨 Tailwind CSS

### Installer les dépendances
```bash
npm install
```

### Mode développement (watch)
```bash
npm run dev
```

### Build production
```bash
npm run build
```

---

## 🐚 Django Shell

### Ouvrir le shell Django
```bash
python manage.py shell
```

### Exemples de commandes dans le shell

#### Créer un utilisateur
```python
from accounts.models import User
user = User.objects.create_user(
    login='TABLE001',
    password='Password123!',
    role='Rtable'
)
```

#### Créer une table
```python
from restaurant.models import TableRestaurant
from accounts.models import User
user = User.objects.get(login='TABLE001')
table = TableRestaurant.objects.create(
    numero_table='01',
    nombre_places=4,
    utilisateur=user
)
```

#### Créer un plat
```python
from restaurant.models import Plat
plat = Plat.objects.create(
    nom='Poulet Yassa',
    prix_unitaire=25000,
    disponible=True
)
```

#### Initialiser la caisse
```python
from payments.models import Caisse
caisse = Caisse.get_instance()
print(f"Solde: {caisse.solde_actuel}")
```

#### Ajouter du solde à la caisse
```python
caisse = Caisse.get_instance()
caisse.ajouter_montant(50000)
print(f"Nouveau solde: {caisse.solde_actuel}")
```

---

## 📊 Fichiers statiques

### Collecter les fichiers statiques
```bash
python manage.py collectstatic
```

### Collecter sans confirmation
```bash
python manage.py collectstatic --noinput
```

### Nettoyer les fichiers statiques
```bash
python manage.py collectstatic --clear --noinput
```

---

## 🧪 Tests

### Lancer tous les tests
```bash
python manage.py test
```

### Tester une app spécifique
```bash
python manage.py test accounts
```

### Tester avec verbosité
```bash
python manage.py test --verbosity=2
```

---

## 🔍 Déboggage

### Vérifier la configuration Django
```bash
python manage.py check
```

### Voir les paramètres Django
```bash
python manage.py diffsettings
```

### Shell interactif avec auto-reload
```bash
python manage.py shell_plus  # Nécessite django-extensions
```

---

## 📝 Données de test

### Créer des fixtures (sauvegarder des données)
```bash
python manage.py dumpdata accounts > accounts_fixture.json
python manage.py dumpdata restaurant > restaurant_fixture.json
```

### Charger des fixtures
```bash
python manage.py loaddata accounts_fixture.json
```

---

## 🗑️ Nettoyage

### Supprimer tous les fichiers .pyc
```bash
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -delete
```

### Réinitialiser la base de données
```bash
# ATTENTION : Supprime toutes les données !
python manage.py flush
```

### Supprimer et recréer la base de données
```bash
# 1. Se connecter à MySQL
mysql -u root -p

# 2. Supprimer et recréer
DROP DATABASE restaurant_db;
CREATE DATABASE restaurant_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# 3. Réappliquer les migrations
python manage.py migrate

# 4. Recréer le superutilisateur
python manage.py createsuperuser
```

---

## 📋 Commandes personnalisées (à créer)

### Structure d'une commande personnalisée
```
accounts/
└── management/
    └── commands/
        └── create_test_users.py
```

### Exemple de commande
```python
from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = 'Créer des utilisateurs de test'

    def handle(self, *args, **options):
        # Créer les utilisateurs
        users_data = [
            {'login': 'TABLE001', 'role': 'Rtable'},
            {'login': 'SERV001', 'role': 'Rserveur'},
        ]
        
        for data in users_data:
            user, created = User.objects.get_or_create(
                login=data['login'],
                defaults={'role': data['role']}
            )
            if created:
                user.set_password('Test123!')
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Utilisateur {user.login} créé')
                )
```

### Utiliser la commande
```bash
python manage.py create_test_users
```

---

## 🔐 Sécurité

### Générer une nouvelle SECRET_KEY
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### Vérifier les problèmes de sécurité
```bash
python manage.py check --deploy
```

---

## 📊 Performance

### Afficher les requêtes SQL
```python
# Dans settings.py (mode DEBUG uniquement)
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

---

## 🚀 Déploiement

### Préparer pour la production
```bash
# 1. Mettre DEBUG à False dans settings.py
DEBUG = False

# 2. Configurer ALLOWED_HOSTS
ALLOWED_HOSTS = ['votre-domaine.com', 'www.votre-domaine.com']

# 3. Collecter les fichiers statiques
python manage.py collectstatic --noinput

# 4. Compiler Tailwind en mode production
npm run build

# 5. Créer un utilisateur pour Gunicorn
pip install gunicorn

# 6. Lancer avec Gunicorn
gunicorn core.wsgi:application --bind 0.0.0.0:8000
```

---

## 📚 Ressources

- Documentation Django : https://docs.djangoproject.com/
- Documentation Tailwind CSS : https://tailwindcss.com/docs
- Documentation MySQL : https://dev.mysql.com/doc/

---

## 💡 Astuces

### Raccourci pour les migrations
```bash
alias mkmig='python manage.py makemigrations'
alias mig='python manage.py migrate'
alias run='python manage.py runserver'
```

### Raccourci Git
```bash
git add .
git commit -m "Message de commit"
git push origin main
```

### Vérification rapide
```bash
# Tout vérifier en une fois
python manage.py check && \
python manage.py makemigrations --check && \
python manage.py test && \
echo "✅ Tout est OK !"
```

---

Ce fichier contient toutes les commandes dont vous aurez besoin pour gérer votre projet ! 🎉
