# GUIDE D'INSTALLATION - Système de Gestion de Restaurant

## 📋 Table des matières
1. [Prérequis](#prérequis)
2. [Installation de Python et MySQL](#installation-de-python-et-mysql)
3. [Configuration du projet](#configuration-du-projet)
4. [Configuration de Tailwind CSS](#configuration-de-tailwind-css)
5. [Initialisation de la base de données](#initialisation-de-la-base-de-données)
6. [Lancement de l'application](#lancement-de-lapplication)
7. [Données de test](#données-de-test)

---

## 1. Prérequis

### Logiciels requis
- Python 3.10 ou supérieur
- MySQL 8.0 ou supérieur
- Node.js 18 ou supérieur
- npm (inclus avec Node.js)
- Git (optionnel)

### Vérification des versions
```bash
python --version      # Python 3.10+
mysql --version       # MySQL 8.0+
node --version        # Node.js 18+
npm --version         # npm 9+
```

---

## 2. Installation de Python et MySQL

### Sur Windows

#### Python
1. Télécharger depuis https://www.python.org/downloads/
2. Cocher "Add Python to PATH" lors de l'installation
3. Vérifier : `python --version`

#### MySQL
1. Télécharger MySQL Community Server : https://dev.mysql.com/downloads/mysql/
2. Installer avec les paramètres par défaut
3. Noter le mot de passe root
4. Vérifier : `mysql --version`

#### Node.js
1. Télécharger depuis https://nodejs.org/
2. Installer avec les paramètres par défaut
3. Vérifier : `node --version` et `npm --version`

### Sur Linux (Ubuntu/Debian)

```bash
# Python
sudo apt update
sudo apt install python3 python3-pip python3-venv

# MySQL
sudo apt install mysql-server
sudo mysql_secure_installation

# Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

### Sur macOS

```bash
# Utiliser Homebrew
brew install python
brew install mysql
brew install node

# Démarrer MySQL
brew services start mysql
```

---

## 3. Configuration du projet

### Étape 1 : Récupérer le projet
```bash
# Si vous avez le code source
cd /chemin/vers/restaurant_management

# Ou cloner depuis un repository
git clone <repository-url>
cd restaurant_management
```

### Étape 2 : Créer l'environnement virtuel
```bash
# Créer l'environnement
python -m venv venv

# Activer l'environnement
# Sur Windows
venv\Scripts\activate

# Sur Linux/macOS
source venv/bin/activate
```

Vous devriez voir `(venv)` avant votre prompt.

### Étape 3 : Installer les dépendances Python
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note** : Si vous rencontrez des erreurs avec `mysqlclient`, installez les dépendances système :

**Windows** : Télécharger le wheel depuis https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient

**Linux** :
```bash
sudo apt install python3-dev default-libmysqlclient-dev build-essential
```

**macOS** :
```bash
brew install mysql-client
export PATH="/usr/local/opt/mysql-client/bin:$PATH"
```

### Étape 4 : Configurer les variables d'environnement
```bash
# Copier le fichier exemple
cp .env.example .env

# Éditer le fichier .env avec vos paramètres
# Sur Windows, utiliser notepad .env
# Sur Linux/macOS, utiliser nano .env ou vim .env
```

Exemple de contenu `.env` :
```
SECRET_KEY=votre-cle-secrete-tres-longue-et-aleatoire
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=restaurant_db
DB_USER=root
DB_PASSWORD=votre_mot_de_passe_mysql
DB_HOST=localhost
DB_PORT=3306

EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app
```

---

## 4. Configuration de Tailwind CSS

### Étape 1 : Installer les dépendances Node.js
```bash
npm install
```

### Étape 2 : Compiler Tailwind CSS

#### Mode développement (avec auto-recompilation)
```bash
npm run dev
```
Laisser cette commande tourner dans un terminal séparé.

#### Mode production (une seule fois)
```bash
npm run build
```

Le fichier CSS sera généré dans `static/css/output.css`

---

## 5. Initialisation de la base de données

### Étape 1 : Créer la base de données MySQL

**Option A : Via la ligne de commande**
```bash
mysql -u root -p < init_database.sql
```

**Option B : Manuellement**
```bash
# Se connecter à MySQL
mysql -u root -p

# Dans le prompt MySQL
CREATE DATABASE restaurant_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'restaurant_user'@'localhost' IDENTIFIED BY 'Restaurant@2024';
GRANT ALL PRIVILEGES ON restaurant_db.* TO 'restaurant_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Étape 2 : Appliquer les migrations Django
```bash
# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate
```

### Étape 3 : Créer l'instance de la caisse
```bash
python manage.py shell
```

Dans le shell Python :
```python
from payments.models import Caisse
caisse = Caisse.get_instance()
print(f"Caisse créée avec solde : {caisse.solde_actuel}")
exit()
```

### Étape 4 : Créer un superutilisateur
```bash
python manage.py createsuperuser
```

Suivre les instructions :
- Login : `ADMIN001` (exemple)
- Mot de passe : choisir un mot de passe sécurisé

### Étape 5 : Collecter les fichiers statiques
```bash
python manage.py collectstatic --noinput
```

---

## 6. Lancement de l'application

### Démarrer le serveur Django
```bash
python manage.py runserver
```

L'application sera accessible à : **http://localhost:8000**

### En parallèle (dans un autre terminal)
```bash
# Activer l'environnement virtuel
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate  # Windows

# Lancer Tailwind en mode watch
npm run dev
```

---

## 7. Données de test

### Créer des utilisateurs de test

**Via l'interface admin** : http://localhost:8000/admin

1. Se connecter avec le superutilisateur
2. Aller dans "Utilisateurs"
3. Créer des utilisateurs :

**Table**
- Login : `TABLE001`
- Rôle : Table
- Actif : ✓

**Serveur**
- Login : `SERV001`
- Rôle : Serveur/Servante
- Actif : ✓

**Cuisinier**
- Login : `CHEF001`
- Rôle : Cuisinier
- Actif : ✓

**Comptable**
- Login : `COMPTA001`
- Rôle : Comptable
- Actif : ✓

### Créer des tables de restaurant

1. Dans l'admin, aller dans "Tables"
2. Créer une table :
   - Numéro : `01`
   - Nombre de places : `4`
   - Utilisateur : `TABLE001`

### Ajouter des plats

1. Dans l'admin, aller dans "Plats"
2. Ajouter quelques plats :
   - Nom : `Poulet Yassa`
   - Prix : `25000`
   - Disponible : ✓
   - Image : (optionnel)

---

## 8. Tests et vérification

### Vérifier que tout fonctionne

1. **Page d'accueil** : http://localhost:8000
2. **Admin** : http://localhost:8000/admin
3. **Login table** : http://localhost:8000/login avec `TABLE001`
4. **Login serveur** : http://localhost:8000/login avec `SERV001`

### Résolution des problèmes courants

**Erreur : Can't connect to MySQL**
- Vérifier que MySQL est démarré
- Vérifier les identifiants dans `.env`

**Erreur : Module not found**
- Vérifier que l'environnement virtuel est activé
- Réinstaller les dépendances : `pip install -r requirements.txt`

**Tailwind CSS ne se compile pas**
- Vérifier que Node.js est installé
- Réinstaller les dépendances : `npm install`
- Relancer : `npm run dev`

**Images ne s'affichent pas**
- Vérifier que le dossier `media` existe
- Vérifier les paramètres `MEDIA_URL` et `MEDIA_ROOT` dans `settings.py`

---

## 9. Commandes utiles

```bash
# Créer de nouvelles migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver

# Lancer le serveur sur un port différent
python manage.py runserver 8080

# Accéder au shell Django
python manage.py shell

# Compiler Tailwind CSS
npm run build

# Mode développement Tailwind
npm run dev
```

---

## 10. Prochaines étapes

Une fois l'installation terminée, vous pouvez :

1. Créer des utilisateurs pour chaque rôle
2. Ajouter des tables de restaurant
3. Créer un menu avec des plats
4. Tester le processus de commande complet
5. Développer les fonctionnalités avancées (dashboard, exports, etc.)

---

## 📞 Support

En cas de problème, vérifier :
1. Les logs du serveur Django
2. La console du navigateur (F12)
3. Les messages d'erreur MySQL

Bonne installation ! 🚀
