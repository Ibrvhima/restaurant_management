from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages

def admin_or_role_required(*allowed_roles):
    """
    Décorateur qui permet l'accès aux administrateurs (tous les privilèges) 
    et aux rôles spécifiés
    """
    def check_role(user):
        # Les administrateurs ont tous les accès
        if user.is_authenticated and user.role == 'Radmin':
            return True
        
        # Vérifier si l'utilisateur a un rôle autorisé
        if user.is_authenticated and user.role in allowed_roles:
            return True
            
        return False
    
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if not check_role(request.user):
                messages.error(request, "Accès non autorisé. Privilèges insuffisants.")
                return redirect('accounts:dashboard')
            return view_func(request, *args, **kwargs)
        return wrapped_view
    
    return decorator

def admin_required(view_func):
    """
    Décorateur qui exige uniquement le rôle administrateur
    """
    return user_passes_test(lambda u: u.is_authenticated and u.role == 'Radmin', 
                           login_url='accounts:login')(view_func)

def admin_or_serveur_required(view_func):
    """
    Décorateur pour les vues accessibles par admin et serveur
    """
    return admin_or_role_required('Rserveur')(view_func)

def admin_or_cuisinier_required(view_func):
    """
    Décorateur pour les vues accessibles par admin et cuisinier
    """
    return admin_or_role_required('Rcuisinier')(view_func)

def admin_or_caissier_required(view_func):
    """
    Décorateur pour les vues accessibles par admin et caissier
    """
    return admin_or_role_required('Rcaissier')(view_func)

def admin_or_comptable_required(view_func):
    """
    Décorateur pour les vues accessibles par admin et comptable
    """
    return admin_or_role_required('Rcomptable')(view_func)

def admin_or_table_required(view_func):
    """
    Décorateur pour les vues accessibles par admin et table
    """
    return admin_or_role_required('Rtable')(view_func)

# Décorateurs pour les accès multiples
def admin_or_staff_required(view_func):
    """
    Décorateur pour les vues accessibles par admin et tout le personnel
    (sauf les tables qui sont des clients)
    """
    return admin_or_role_required('Rserveur', 'Rcuisinier', 'Rcaissier', 'Rcomptable')(view_func)

def admin_or_financial_required(view_func):
    """
    Décorateur pour les vues financières (admin, caissier, comptable)
    """
    return admin_or_role_required('Rcaissier', 'Rcomptable')(view_func)

def admin_or_restaurant_staff_required(view_func):
    """
    Décorateur pour le personnel restaurant (admin, serveur, cuisinier)
    """
    return admin_or_role_required('Rserveur', 'Rcuisinier')(view_func)
