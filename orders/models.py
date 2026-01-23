from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from restaurant.models import TableRestaurant, Plat


class EtatCommande(models.TextChoices):
    """États possibles pour une commande"""
    EN_ATTENTE = 'EN_ATTENTE', 'En attente'
    EN_COURS = 'EN_COURS', 'En cours'
    EN_PREPARATION = 'EN_PREPARATION', 'En préparation'
    TERMINEE = 'TERMINEE', 'Terminée'
    ANNULEE = 'ANNULEE', 'Annulée'


class Commande(models.Model):
    """
    Modèle pour les commandes
    """
    table = models.ForeignKey(
        TableRestaurant,
        on_delete=models.CASCADE,
        related_name='commandes',
        verbose_name='Table'
    )
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role__in': ['Rtable', 'Rserveur', 'Radmin']},
        verbose_name='Utilisateur',
        related_name='commandes_utilisateur'
    )
    serveur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role__in': ['Rserveur', 'Radmin']},
        verbose_name='Serveur',
        related_name='commandes_serveur'
    )
    etat = models.CharField(
        max_length=20,
        choices=EtatCommande.choices,
        default=EtatCommande.EN_ATTENTE,
        verbose_name='État'
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
        verbose_name='Total'
    )
    date_commande = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'commandes'
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'
        ordering = ['-date_commande']
    
    def __str__(self):
        return f"Commande #{self.id} - Table {self.table.numero_table} - {self.total} GNF"
    
    def calculer_total(self):
        """Calcule le total de la commande à partir des items"""
        total = 0
        for item in self.commandeplat_set.all():
            total += item.sous_total()
        self.total = total
        self.save()
        return total


class CommandePlat(models.Model):
    """
    Modèle pour les plats d'une commande
    """
    commande = models.ForeignKey(
        Commande,
        on_delete=models.CASCADE,
        related_name='commandeplat_set',
        verbose_name='Commande'
    )
    plat = models.ForeignKey(
        Plat,
        on_delete=models.CASCADE,
        verbose_name='Plat'
    )
    quantite = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Quantité'
    )
    prix_unitaire = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Prix unitaire'
    )
    
    class Meta:
        db_table = 'commande_plats'
        verbose_name = 'Plat commandé'
        verbose_name_plural = 'Plats commandés'
        unique_together = ['commande', 'plat']
    
    def __str__(self):
        return f"{self.plat.nom} x{self.quantite}"
    
    def sous_total(self):
        """Calcule le sous-total"""
        return self.prix_unitaire * self.quantite
    
    def save(self, *args, **kwargs):
        """Enregistre le prix unitaire au moment de la commande"""
        if not self.prix_unitaire:
            self.prix_unitaire = self.plat.prix_unitaire
        super().save(*args, **kwargs)
