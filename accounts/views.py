from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from .models import User
from .forms import UserCreationForm, UserEditForm
from .utils import export_dashboard_excel
from .pdf_utils import export_dashboard_pdf
from orders.models import Commande, EtatCommande
from restaurant.models import Plat
from payments.models import Paiement
from django.utils import timezone

def home(request):
    """Page d'accueil du restaurant"""
    return render(request, 'accounts/home.html')

def login_view(request):
    """Vue de connexion"""
    if request.method == 'POST':
        login_input = request.POST.get('login')
        password = request.POST.get('password')
        
        user = authenticate(request, username=login_input, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenue {user.login}!')
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Identifiant ou mot de passe incorrect.')
    
    return render(request, 'accounts/login.html')

@login_required
def logout_view(request):
    """Vue de déconnexion"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('accounts:login')

@login_required
def dashboard(request):
    """Tableau de bord principal"""
    user = request.user
    
    # Rediriger selon le rôle
    if user.role == 'Rtable':
        return redirect('restaurant:table_home')
    elif user.role == 'Rserveur':
        return redirect('restaurant:serveur_home')
    elif user.role == 'Rcuisinier':
        return redirect('restaurant:cuisinier_home')
    elif user.role == 'Rcomptable':
        return redirect('restaurant:comptable_home')
    
    # Calculer les statistiques pour les autres rôles
    from orders.models import Commande, EtatCommande
    from restaurant.models import Plat
    from payments.models import Paiement
    
    # Statistiques des commandes
    total_commandes = Commande.objects.count()
    commandes_en_cours = Commande.objects.filter(
        etat__in=[EtatCommande.EN_ATTENTE, EtatCommande.EN_PREPARATION, EtatCommande.EN_COURS]
    ).count()
    commandes_terminees = Commande.objects.filter(etat=EtatCommande.TERMINEE).count()
    
    # Statistiques des plats
    total_plats = Plat.objects.count()
    plats_disponibles = Plat.objects.filter(disponible=True).count()
    
    # Statistiques des paiements du jour
    from django.utils import timezone
    today = timezone.now().date()
    paiements_aujourdhui = Paiement.objects.filter(date_paiement__date=today).count()
    total_ventes_aujourdhui = Paiement.objects.filter(date_paiement__date=today).aggregate(
        total=models.Sum('montant')
    )['total'] or 0
    
    # Total des revenus (tous les paiements)
    total_revenus = Paiement.objects.aggregate(
        total=models.Sum('montant')
    )['total'] or 0
    
    # Nombre total de paiements
    total_paiements = Paiement.objects.count()
    
    # Statistiques des dépenses (total)
    from expenses.models import Depense
    total_depenses = Depense.objects.count()
    depenses_aujourdhui = Depense.objects.filter(date_depense=today).count()
    total_depenses_aujourdhui = Depense.objects.filter(date_depense=today).aggregate(
        total=models.Sum('montant')
    )['total'] or 0
    
    # Dépenses récentes (pour le dashboard admin)
    depenses_recentes = Depense.objects.order_by('-date_depense')[:5]
    
    context = {
        'user': user,
        'role_display': user.get_role_display(),
        'total_commandes': total_commandes,
        'commandes_en_cours': commandes_en_cours,
        'commandes_terminees': commandes_terminees,
        'total_plats': total_plats,
        'plats_disponibles': plats_disponibles,
        'paiements_aujourdhui': paiements_aujourdhui,
        'total_ventes_aujourdhui': total_ventes_aujourdhui,
        'total_revenus': total_revenus,
        'total_paiements': total_paiements,
        'depenses_aujourdhui': total_depenses,
        'total_depenses_aujourdhui': total_depenses_aujourdhui,
        'depenses_recentes': depenses_recentes,
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def profile(request):
    """Profil de l'utilisateur"""
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def admin_user_list(request):
    """Liste des utilisateurs (admin seulement)"""
    if request.user.role != 'Radmin':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:dashboard')
    
    users = User.objects.all().order_by('-date_creation')
    context = {'users': users}
    return render(request, 'accounts/admin_user_list_simple.html', context)

@login_required
def admin_create_user(request):
    """Créer un utilisateur (admin seulement)"""
    if request.user.role != 'Radmin':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Utilisateur {form.cleaned_data['login']} créé avec succès!")
            return redirect('accounts:admin_user_list')
    else:
        form = UserCreationForm()
    
    context = {
        'form': form,
        'title': 'Créer un utilisateur'
    }
    return render(request, 'accounts/admin_create_user_simple.html', context)

@login_required
def admin_toggle_user(request, user_id):
    """Activer/Désactiver un utilisateur (admin seulement)"""
    if request.user.role != 'Radmin':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:dashboard')
    
    user = get_object_or_404(User, id=user_id)
    if user.role == 'Radmin':
        messages.error(request, "Impossible de désactiver un administrateur.")
    else:
        user.actif = not user.actif
        user.save()
        status = "activé" if user.actif else "désactivé"
        messages.success(request, f"Utilisateur {user.login} {status} avec succès!")
    
    return redirect('accounts:admin_user_list')

@login_required
def admin_data_management(request):
    """Gestion des données (admin seulement)"""
    if request.user.role != 'Radmin':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:dashboard')
    
    # Statistiques actuelles
    from orders.models import Commande
    from payments.models import Paiement
    from expenses.models import Depense
    from payments.models import Caisse
    
    stats = {
        'total_commandes': Commande.objects.count(),
        'total_paiements': Paiement.objects.count(),
        'total_depenses': Depense.objects.count(),
        'solde_caisse': Caisse.get_instance().solde_actuel if Caisse.objects.exists() else 0,
    }
    
    context = {'stats': stats}
    return render(request, 'accounts/admin_data_management.html', context)

@login_required
def admin_clear_commandes(request):
    """Supprimer toutes les commandes (admin seulement)"""
    if request.user.role != 'Radmin':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        from orders.models import Commande
        count = Commande.objects.count()
        Commande.objects.all().delete()
        messages.success(request, f"{count} commande(s) supprimée(s) avec succès!")
    
    return redirect('accounts:admin_data_management')

@login_required
def admin_clear_paiements(request):
    """Supprimer tous les paiements (admin seulement)"""
    if request.user.role != 'Radmin':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        from payments.models import Paiement
        count = Paiement.objects.count()
        Paiement.objects.all().delete()
        messages.success(request, f"{count} paiement(s) supprimé(s) avec succès!")
    
    return redirect('accounts:admin_data_management')

@login_required
def admin_clear_depenses(request):
    """Supprimer toutes les dépenses (admin seulement)"""
    if request.user.role != 'Radmin':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        from expenses.models import Depense
        count = Depense.objects.count()
        Depense.objects.all().delete()
        messages.success(request, f"{count} dépense(s) supprimée(s) avec succès!")
    
    return redirect('accounts:admin_data_management')

@login_required
def admin_reset_caisse(request):
    """Réinitialiser la caisse (admin seulement)"""
    if request.user.role != 'Radmin':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        from payments.models import Caisse
        caisse = Caisse.get_instance()
        old_solde = caisse.solde_actuel
        caisse.solde_actuel = 0
        caisse.save()
        messages.success(request, f"Caisse réinitialisée! Ancien solde: {old_solde} GNF")
    
    return redirect('accounts:admin_data_management')

@login_required
def export_excel_dashboard(request):
    """Exporter les données du dashboard en Excel (admin seulement)"""
    if request.user.role != 'Radmin':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:dashboard')
    
    return export_dashboard_excel(request)

@login_required
def export_pdf_dashboard(request):
    """Exporter les données du dashboard en PDF (admin seulement)"""
    if request.user.role != 'Radmin':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:dashboard')
    
    return export_dashboard_pdf(request)

@login_required
def admin_edit_user(request, user_id):
    """Modifier un utilisateur (admin seulement)"""
    if request.user.role != 'Radmin':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:dashboard')
    
    user_to_edit = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user_to_edit)
        if form.is_valid():
            form.save()
            messages.success(request, f"Utilisateur {user_to_edit.login} modifié avec succès!")
            return redirect('accounts:admin_user_list')
    else:
        form = UserEditForm(instance=user_to_edit)
    
    context = {
        'form': form,
        'user_to_edit': user_to_edit,
        'title': 'Modifier un utilisateur'
    }
    return render(request, 'accounts/admin_create_user_simple.html', context)

@login_required
def admin_delete_user(request, user_id):
    """Supprimer un utilisateur (admin seulement)"""
    if request.user.role != 'Radmin':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:dashboard')
    
    user_to_delete = get_object_or_404(User, id=user_id)
    
    # Empêcher la suppression du dernier admin
    if user_to_delete.role == 'Radmin':
        messages.error(request, "Impossible de supprimer un administrateur.")
        return redirect('accounts:admin_user_list')
    
    if request.method == 'POST':
        username = user_to_delete.login
        user_to_delete.delete()
        messages.success(request, f"Utilisateur {username} supprimé avec succès!")
        return redirect('accounts:admin_user_list')
    
    context = {
        'user_to_delete': user_to_delete,
        'title': 'Supprimer un utilisateur'
    }
    return render(request, 'accounts/admin_delete_user.html', context)
