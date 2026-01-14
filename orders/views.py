from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, date
from .models import Commande, CommandePlat, EtatCommande

@login_required
def commande_list(request):
    """Liste des commandes"""
    commandes = Commande.objects.all().order_by('-date_commande')
    
    # Filtrer par état si spécifié
    etat = request.GET.get('etat')
    if etat:
        commandes = commandes.filter(etat=etat)
    
    # Filtrer par date si spécifié
    date_filter = request.GET.get('date')
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            commandes = commandes.filter(date_commande__date=filter_date)
        except ValueError:
            pass
    
    etats = EtatCommande.choices
    context = {
        'commandes': commandes,
        'etats': etats,
        'etat_filter': etat,
        'date_filter': date_filter
    }
    return render(request, 'orders/commande_list.html', context)

@login_required
def commande_detail(request, commande_id):
    """Détail d'une commande"""
    commande = get_object_or_404(Commande, id=commande_id)
    return render(request, 'orders/commande_detail.html', {'commande': commande})

@login_required
def nouvelle_commande(request):
    """Créer une nouvelle commande"""
    # Récupérer la table pré-sélectionnée si passée en paramètre
    table_preselectionnee = request.GET.get('table')
    
    if request.method == 'POST':
        table_id = request.POST.get('table')
        plats = request.POST.getlist('plats')
        quantites = request.POST.getlist('quantites')
        
        if not table_id or not plats:
            messages.error(request, 'Veuillez sélectionner une table et au moins un plat.')
            return redirect('orders:nouvelle_commande')
        
        # Créer la commande avec total initialisé à 0
        commande = Commande.objects.create(
            table_id=table_id,
            serveur=request.user,
            etat=EtatCommande.EN_COURS,
            total=0  # Initialiser le total à 0
        )
        
        # Ajouter les plats à la commande
        total = 0
        for plat_id, quantite in zip(plats, quantites):
            if quantite and int(quantite) > 0:
                commande_plat = CommandePlat.objects.create(
                    commande=commande,
                    plat_id=plat_id,
                    quantite=int(quantite)
                )
                total += commande_plat.sous_total()
        
        # Mettre à jour le total
        commande.total = total
        commande.save()
        
        messages.success(request, f'Commande #{commande.id} créée avec succès!')
        return redirect('orders:commande_detail', commande_id=commande.id)
    
    # Récupérer les tables et les plats disponibles
    from restaurant.models import TableRestaurant, Plat
    tables = TableRestaurant.objects.all()
    plats = Plat.objects.filter(disponible=True)
    
    context = {
        'tables': tables,
        'plats': plats,
        'table_preselectionnee': table_preselectionnee
    }
    return render(request, 'orders/nouvelle_commande.html', context)

@require_POST
@login_required
def changer_etat_commande(request, commande_id):
    """Changer l'état d'une commande"""
    commande = get_object_or_404(Commande, id=commande_id)
    nouvel_etat = request.POST.get('etat')
    
    if nouvel_etat in [choice[0] for choice in EtatCommande.choices]:
        commande.etat = nouvel_etat
        commande.save()
        messages.success(request, f'État de la commande #{commande.id} mis à jour.')
    else:
        messages.error(request, 'État invalide.')
    
    return redirect('orders:commande_detail', commande_id=commande.id)

@login_required
def commandes_en_cours(request):
    """Liste des commandes en cours"""
    commandes = Commande.objects.filter(
        etat__in=[EtatCommande.EN_COURS, EtatCommande.EN_PREPARATION]
    ).order_by('-date_commande')
    
    return render(request, 'orders/commandes_en_cours.html', {'commandes': commandes})

@login_required
def statistiques_commandes(request):
    """Statistiques des commandes"""
    today = timezone.now().date()
    
    # Statistiques du jour
    commandes_aujourdhui = Commande.objects.filter(date_commande__date=today)
    total_aujourdhui = commandes_aujourdhui.aggregate(Sum('total'))['total__sum'] or 0
    nb_commandes_aujourdhui = commandes_aujourdhui.count()
    
    # Statistiques du mois
    month_start = today.replace(day=1)
    commandes_mois = Commande.objects.filter(date_commande__date__gte=month_start)
    total_mois = commandes_mois.aggregate(Sum('total'))['total__sum'] or 0
    nb_commandes_mois = commandes_mois.count()
    
    # Plats les plus populaires
    plats_populaires = CommandePlat.objects.values('plat__nom').annotate(
        total_quantite=Sum('quantite'),
        nb_commandes=Count('commande')
    ).order_by('-total_quantite')[:10]
    
    context = {
        'total_aujourdhui': total_aujourdhui,
        'nb_commandes_aujourdhui': nb_commandes_aujourdhui,
        'total_mois': total_mois,
        'nb_commandes_mois': nb_commandes_mois,
        'plats_populaires': plats_populaires
    }
    
    return render(request, 'orders/statistiques.html', context)
