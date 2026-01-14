from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class CategorieDepense(models.Model):
    """
    Modèle pour les catégories de dépenses
    """
    nom = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nom de la catégorie'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'categories_depenses'
        verbose_name = 'Catégorie de dépense'
        verbose_name_plural = 'Catégories de dépenses'
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class Depense(models.Model):
    """
    Modèle pour les dépenses du restaurant
    """
    description = models.CharField(
        max_length=255,
        verbose_name='Description'
    )
    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Montant'
    )
    categorie = models.ForeignKey(
        CategorieDepense,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Catégorie'
    )
    date_depense = models.DateField(
        verbose_name='Date de la dépense'
    )
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role__in': ['Radmin', 'Rcomptable']},
        verbose_name='Utilisateur'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'depenses'
        verbose_name = 'Dépense'
        verbose_name_plural = 'Dépenses'
        ordering = ['-date_depense']
    
    def __str__(self):
        return f"{self.description} - {self.montant} FCFA ({self.date_depense.strftime('%d/%m/%Y')})"
