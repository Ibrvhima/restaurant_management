from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from orders.models import Commande


class MethodePaiement(models.TextChoices):
    """Méthodes de paiement possibles"""
    ESPECE = 'ESPECE', 'Espèce'
    CARTE = 'CARTE', 'Carte bancaire'
    MOBILE_MONEY = 'MOBILE_MONEY', 'Mobile Money'
    VIREMENT = 'VIREMENT', 'Virement bancaire'
    CHEQUE = 'CHEQUE', 'Chèque'


class Paiement(models.Model):
    """
    Modèle pour les paiements des commandes
    """
    commande = models.OneToOneField(
        Commande,
        on_delete=models.CASCADE,
        related_name='paiement',
        verbose_name='Commande'
    )
    methode = models.CharField(
        max_length=20,
        choices=MethodePaiement.choices,
        default=MethodePaiement.ESPECE,
        verbose_name='Méthode de paiement'
    )
    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Montant'
    )
    caissier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role__in': ['Rcaissier', 'Radmin']},
        verbose_name='Caissier'
    )
    date_paiement = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'paiements'
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'
        ordering = ['-date_paiement']
    
    def __str__(self):
        return f"Paiement #{self.id} - Commande #{self.commande.id} - {self.montant} FCFA"


class Caisse(models.Model):
    """
    Modèle pour la caisse du restaurant (Singleton)
    """
    solde_actuel = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Solde actuel'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    derniere_mise_a_jour = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'caisse'
        verbose_name = 'Caisse'
        verbose_name_plural = 'Caisse'
    
    def __str__(self):
        return f"Caisse - Solde: {self.solde_actuel} FCFA"
    
    def save(self, *args, **kwargs):
        """Assure qu'il n'y a qu'une seule instance de Caisse"""
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Empêche la suppression de la caisse"""
        pass
    
    @classmethod
    def get_instance(cls):
        """Retourne l'instance unique de la caisse"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    def ajouter_montant(self, montant):
        """Ajoute un montant à la caisse"""
        from decimal import Decimal
        if isinstance(montant, (int, float, str)):
            montant = Decimal(str(montant))
        self.solde_actuel += montant
        self.save()
    
    def retirer_montant(self, montant):
        """Retire un montant de la caisse"""
        from decimal import Decimal
        if isinstance(montant, (int, float, str)):
            montant = Decimal(str(montant))
        if self.solde_actuel >= montant:
            self.solde_actuel -= montant
            self.save()
            return True
        return False
