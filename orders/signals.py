from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.db import transaction
from .models import Commande, CommandePlat

@receiver(post_save, sender=CommandePlat)
def mettre_a_jour_total_commande_ajout(sender, instance, created, **kwargs):
    """
    Met à jour le total de la commande lors de l'ajout d'un plat
    """
    if created:
        with transaction.atomic():
            instance.commande.calculer_total()

@receiver(post_delete, sender=CommandePlat)
def mettre_a_jour_total_commande_suppression(sender, instance, **kwargs):
    """
    Met à jour le total de la commande lors de la suppression d'un plat
    """
    with transaction.atomic():
        instance.commande.calculer_total()

@receiver(post_save, sender=CommandePlat)
def mettre_a_jour_total_commande_modification(sender, instance, **kwargs):
    """
    Met à jour le total de la commande lors de la modification d'un plat
    """
    if not kwargs.get('created', False):
        with transaction.atomic():
            instance.commande.calculer_total()
