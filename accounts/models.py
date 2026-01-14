from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator, MinLengthValidator


class UserManager(BaseUserManager):
    """
    Custom user manager for User model
    """
    def create_user(self, login, password=None, **extra_fields):
        if not login:
            raise ValueError('Le login est obligatoire')
        
        user = self.model(login=login, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, login, password=None, **extra_fields):
        extra_fields.setdefault('role', 'Radmin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('actif', True)
        
        return self.create_user(login, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with role-based access
    """
    ROLE_CHOICES = [
        ('Rtable', 'Table'),
        ('Rserveur', 'Serveur/Servante'),
        ('Rcuisinier', 'Cuisinier'),
        ('Rcaissier', 'Caissier'),
        ('Rcomptable', 'Comptable'),
        ('Radmin', 'Administrateur'),
    ]
    
    # Validators
    login_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9]{6,}$',
        message='Le login doit contenir au moins 6 caractères alphanumériques'
    )
    
    login = models.CharField(
        max_length=50,
        unique=True,
        validators=[login_validator, MinLengthValidator(6)],
        help_text='Identifiant unique (minimum 6 caractères alphanumériques)'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='Rtable'
    )
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    # Required for Django admin
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.login} ({self.get_role_display()})"
    
    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        return True
    
    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        return True
    
    # Role checking methods
    def is_table(self):
        return self.role == 'Rtable'
    
    def is_serveur(self):
        return self.role == 'Rserveur'
    
    def is_cuisinier(self):
        return self.role == 'Rcuisinier'
    
    def is_caissier(self):
        return self.role == 'Rcaissier'
    
    def is_comptable(self):
        return self.role == 'Rcomptable'
    
    def is_admin(self):
        return self.role == 'Radmin'
