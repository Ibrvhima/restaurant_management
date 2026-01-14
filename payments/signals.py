from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import Paiement, Caisse
from expenses.models import Depense

@receiver(post_save, sender=Paiement)
def mettre_a_jour_caisse_paiement(sender, instance, created, **kwargs):
    """
    Met à jour le solde de la caisse lors d'un paiement
    """
    if created:
        with transaction.atomic():
            caisse = Caisse.get_instance()
            caisse.ajouter_montant(instance.montant)

@receiver(post_delete, sender=Paiement)
def annuler_mise_a_jour_caisse_paiement(sender, instance, **kwargs):
    """
    Annule la mise à jour du solde de la caisse lors de la suppression d'un paiement
    """
    with transaction.atomic():
        caisse = Caisse.get_instance()
        caisse.retirer_montant(instance.montant)

@receiver(post_save, sender=Depense)
def mettre_a_jour_caisse_depense(sender, instance, created, **kwargs):
    """
    Met à jour le solde de la caisse lors d'une dépense
    """
    if created:
        with transaction.atomic():
            caisse = Caisse.get_instance()
            caisse.retirer_montant(instance.montant)

@receiver(post_delete, sender=Depense)
def annuler_mise_a_jour_caisse_depense(sender, instance, **kwargs):
    """
    Annule la mise à jour du solde de la caisse lors de la suppression d'une dépense
    """
    with transaction.atomic():
        caisse = Caisse.get_instance()
        caisse.ajouter_montant(instance.montant)
