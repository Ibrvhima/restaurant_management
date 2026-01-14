from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from .models import User
from .utils import export_dashboard_excel
from .pdf_utils import export_dashboard_pdf
from .email_utils import update_daily_balance, send_daily_balance_report
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
    
    # Statistiques des dépenses du jour
    from expenses.models import Depense
    depenses_aujourdhui = Depense.objects.filter(date_depense=today).count()
    total_depenses_aujourdhui = Depense.objects.filter(date_depense=today).aggregate(
        total=models.Sum('montant')
    )['total'] or 0
    
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
        'depenses_aujourdhui': depenses_aujourdhui,
        'total_depenses_aujourdhui': total_depenses_aujourdhui,
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
    return render(request, 'accounts/admin_user_list.html', context)

@login_required
def admin_create_user(request):
    """Créer un utilisateur (admin seulement)"""
    if request.user.role != 'Radmin':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        login = request.POST.get('login')
        password = request.POST.get('password')
        role = request.POST.get('role')
        actif = request.POST.get('actif') == 'on'
        
        if not login or not password or not role:
            messages.error(request, "Tous les champs sont obligatoires.")
            return redirect('accounts:admin_create_user')
        
        try:
            user = User.objects.create_user(
                login=login,
                password=password,
                role=role,
                actif=actif
            )
            messages.success(request, f"Utilisateur {login} créé avec succès!")
            return redirect('accounts:admin_user_list')
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    return render(request, 'accounts/admin_create_user.html')

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
@ l o g i n _ r e q u i r e d  
 d e f   s e n d _ b a l a n c e _ r e p o r t _ n o w ( r e q u e s t ) :  
         " " " E n v o y e r   m a n u e l l e m e n t   l e   r a p p o r t   d u   s o l d e   p a r   e m a i l   ( a d m i n   s e u l e m e n t ) " " "  
         i f   r e q u e s t . u s e r . r o l e   ! =   ' R a d m i n ' :  
                 m e s s a g e s . e r r o r ( r e q u e s t ,   " A c c � � s   n o n   a u t o r i s � � . " )  
                 r e t u r n   r e d i r e c t ( ' a c c o u n t s : d a s h b o a r d ' )  
          
         t r y :  
                 #   E n v o y e r   l e   r a p p o r t   p o u r   a u j o u r d ' h u i  
                 s u c c e s s   =   s e n d _ d a i l y _ b a l a n c e _ r e p o r t ( )  
                  
                 i f   s u c c e s s :  
                         m e s s a g e s . s u c c e s s ( r e q u e s t ,   " R a p p o r t   d u   s o l d e   e n v o y � �   a v e c   s u c c � � s   p a r   e m a i l ! " )  
                 e l s e :  
                         m e s s a g e s . e r r o r ( r e q u e s t ,   " E r r e u r   l o r s   d e   l ' e n v o i   d u   r a p p o r t .   V � � r i f i e z   l a   c o n f i g u r a t i o n   e m a i l . " )  
                          
         e x c e p t   E x c e p t i o n   a s   e :  
                 m e s s a g e s . e r r o r ( r e q u e s t ,   f " E r r e u r :   { s t r ( e ) } " )  
          
         r e t u r n   r e d i r e c t ( ' a c c o u n t s : d a s h b o a r d ' )  
  
 @ l o g i n _ r e q u i r e d  
 d e f   u p d a t e _ b a l a n c e _ n o w ( r e q u e s t ) :  
         " " " M e t t r e   � �   j o u r   m a n u e l l e m e n t   l e   s o l d e   e t   e n v o y e r   l e s   r a p p o r t s   ( a d m i n   s e u l e m e n t ) " " "  
         i f   r e q u e s t . u s e r . r o l e   ! =   ' R a d m i n ' :  
                 m e s s a g e s . e r r o r ( r e q u e s t ,   " A c c � � s   n o n   a u t o r i s � � . " )  
                 r e t u r n   r e d i r e c t ( ' a c c o u n t s : d a s h b o a r d ' )  
          
         t r y :  
                 #   M e t t r e   � �   j o u r   l e   s o l d e   p o u r   a u j o u r d ' h u i  
                 r e s u l t   =   u p d a t e _ d a i l y _ b a l a n c e ( )  
                  
                 m e s s a g e s . s u c c e s s ( r e q u e s t ,   f " S o l d e   m i s   � �   j o u r !   S o l d e   a c t u e l :   { r e s u l t [ ' s o l d e _ c u m u l ' ] : , . 0 f }   G N F " )  
                  
                 i f   r e s u l t [ ' r a p p o r t _ e n v o y e ' ] :  
                         m e s s a g e s . s u c c e s s ( r e q u e s t ,   " � S&   R a p p o r t   q u o t i d i e n   e n v o y � �   p a r   e m a i l " )  
                  
                 i f   r e s u l t [ ' a l e r t e _ e n v o y e e ' ] :  
                         m e s s a g e s . w a r n i n g ( r e q u e s t ,   " � a� � � �   A l e r t e   d e   s o l d e   c r i t i q u e   e n v o y � � e " )  
                          
         e x c e p t   E x c e p t i o n   a s   e :  
                 m e s s a g e s . e r r o r ( r e q u e s t ,   f " E r r e u r :   { s t r ( e ) } " )  
          
         r e t u r n   r e d i r e c t ( ' a c c o u n t s : d a s h b o a r d ' )  
 