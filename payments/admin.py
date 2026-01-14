from django.contrib import admin
from .models import Paiement, Caisse


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ['id', 'commande', 'methode', 'montant', 'caissier', 'date_paiement']
    list_filter = ['methode', 'date_paiement']
    search_fields = ['commande__id', 'commande__table__numero_table', 'caissier__login']
    ordering = ['-date_paiement']
    readonly_fields = ['date_paiement']


@admin.register(Caisse)
class CaisseAdmin(admin.ModelAdmin):
    list_display = ['solde_actuel', 'date_creation', 'derniere_mise_a_jour']
    readonly_fields = ['date_creation', 'derniere_mise_a_jour']
    
    def has_add_permission(self, request):
        # Il ne peut y avoir qu'une seule caisse
        return not Caisse.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # La caisse ne peut pas être supprimée
        return False
