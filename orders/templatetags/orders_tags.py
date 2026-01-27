from django import template
from ..models import EtatCommande

register = template.Library()

@register.simple_tag
def etat_commande_choices():
    """Retourne les choix d'état de commande"""
    return EtatCommande.choices
