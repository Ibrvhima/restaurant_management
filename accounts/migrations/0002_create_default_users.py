from django.db import migrations
from django.db.models import Q
from django.contrib.auth.hashers import make_password


def create_default_users(apps, schema_editor):
    """
    Crée les utilisateurs par défaut s'ils n'existent pas déjà
    """
    User = apps.get_model('accounts', 'User')
    
    default_users = [
        {
            'login': 'Table1',
            'password': 'Table1@',
            'role': 'Rtable',
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'login': 'Cuisinier1',
            'password': 'Cuisinier1@',
            'role': 'Rcuisinier',
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'login': 'Serveur1',
            'password': 'Serveur1@',
            'role': 'Rserveur',
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'login': 'Comptable1',
            'password': 'Comptable1@',
            'role': 'Rcomptable',
            'is_staff': False,
            'is_superuser': False,
        },
    ]
    
    for user_data in default_users:
        # Vérifier si l'utilisateur existe déjà
        if not User.objects.filter(login=user_data['login']).exists():
            # Créer l'utilisateur avec le mot de passe hashé
            User.objects.create(
                login=user_data['login'],
                password=make_password(user_data['password']),
                role=user_data['role'],
                is_staff=user_data['is_staff'],
                is_superuser=user_data['is_superuser'],
                actif=True
            )
            print(f"Utilisateur {user_data['login']} créé avec succès")
        else:
            print(f"Utilisateur {user_data['login']} existe déjà")


def reverse_create_default_users(apps, schema_editor):
    """
    Supprime les utilisateurs par défaut (migration inverse)
    """
    User = apps.get_model('accounts', 'User')
    
    default_logins = ['Table1', 'Cuisinier1', 'Serveur1', 'Comptable1']
    
    for login in default_logins:
        User.objects.filter(login=login).delete()
        print(f"Utilisateur {login} supprimé")


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            create_default_users,
            reverse_create_default_users,
        ),
    ]
