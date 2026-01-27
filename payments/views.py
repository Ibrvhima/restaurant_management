from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.http import HttpResponse
from accounts.decorators import (admin_or_financial_required, admin_or_role_required, 
                                  admin_or_table_required, admin_or_serveur_required)
from .models import Paiement, MethodePaiement, Caisse
from django.core.paginator import Paginator
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

@admin_or_financial_required
def paiement_list(request):
    """Liste des paiements (et admin)"""
    paiements = Paiement.objects.all()
    
    # Gérer le tri
    sort_field = request.GET.get('sort')
    if sort_field:
        if sort_field == 'id':
            paiements = paiements.order_by('id')
        elif sort_field == 'commande':
            paiements = paiements.order_by('commande__id')
        elif sort_field == 'caissier':
            paiements = paiements.order_by('caissier__login')
        elif sort_field == 'montant':
            paiements = paiements.order_by('montant')
        elif sort_field == 'date':
            paiements = paiements.order_by('date_paiement')
        else:
            paiements = paiements.order_by('-date_paiement')
    else:
        paiements = paiements.order_by('-date_paiement')
    
    # Filtrer par méthode si spécifié
    methode = request.GET.get('methode')
    if methode:
        if methode == 'NON_SPECIFIE':
            # Filtrer les paiements sans méthode spécifiée
            from django.db.models import Q
            paiements = paiements.filter(Q(methode__isnull=True) | Q(methode=''))
            # Debug: compter les paiements non spécifiés
            non_specifies_count = Paiement.objects.filter(Q(methode__isnull=True) | Q(methode='')).count()
            print(f"DEBUG: Paiements non spécifiés trouvés: {non_specifies_count}")
        else:
            paiements = paiements.filter(methode=methode)
    
    # Filtrer par date si spécifié
    date_filter = request.GET.get('date')
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            paiements = paiements.filter(date_paiement__date=filter_date)
        except ValueError:
            pass
    
    # Pagination
    paginator = Paginator(paiements, 20)  # 20 paiements par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    methodes = MethodePaiement.choices
    context = {
        'paiements': page_obj,
        'methodes': methodes,
        'methode_filter': methode,
        'date_filter': date_filter,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    return render(request, 'payments/paiement_list.html', context)

@admin_or_financial_required
def paiement_detail(request, paiement_id):
    """Détail d'un paiement"""
    paiement = get_object_or_404(Paiement, id=paiement_id)
    return render(request, 'payments/paiement_detail.html', {'paiement': paiement})

@admin_or_financial_required
def modifier_paiement(request, paiement_id):
    """Modifier un paiement (réservé au admin et financier)"""
    paiement = get_object_or_404(Paiement, id=paiement_id)
    
    if request.method == 'POST':
        methode = request.POST.get('methode')
        
        if not methode:
            messages.error(request, 'Veuillez sélectionner une méthode de paiement.')
            return redirect('payments:modifier_paiement', paiement_id=paiement_id)
        
        # Vérifier que la méthode est valide
        methodes_valides = [choice[0] for choice in MethodePaiement.choices]
        if methode not in methodes_valides:
            messages.error(request, 'Méthode de paiement invalide.')
            return redirect('payments:modifier_paiement', paiement_id=paiement_id)
        
        # Mettre à jour la méthode de paiement
        old_methode = paiement.get_methode_paiement_display() if paiement.methode else 'Non spécifié'
        paiement.methode = methode
        paiement.save()
        
        new_methode = paiement.get_methode_paiement_display()
        messages.success(request, f'Méthode de paiement mise à jour : {old_methode} → {new_methode}')
        return redirect('payments:paiement_detail', paiement_id=paiement.id)
    
    methodes = MethodePaiement.choices
    context = {
        'paiement': paiement,
        'methodes': methodes,
        'title': 'Modifier le Paiement'
    }
    return render(request, 'payments/modifier_paiement.html', context)

@admin_or_financial_required
def facture_client(request, paiement_id):
    """Afficher la facture client pour impression"""
    paiement = get_object_or_404(Paiement, id=paiement_id)
    
    # Vérifier que le paiement a une méthode spécifiée
    if not paiement.methode:
        messages.error(request, 'Impossible de générer une facture pour un paiement sans méthode de paiement.')
        return redirect('payments:paiement_detail', paiement_id=paiement.id)
    
    context = {
        'paiement': paiement,
        'title': f'Facture #{paiement.id}'
    }
    return render(request, 'payments/facture_client.html', context)

@admin_or_financial_required
def recu_imprimable(request, paiement_id):
    """Afficher le reçu imprimable d'une page"""
    paiement = get_object_or_404(Paiement, id=paiement_id)
    
    # Vérifier que le paiement a une méthode spécifiée
    if not paiement.methode:
        messages.error(request, 'Impossible de générer un reçu pour un paiement sans méthode de paiement.')
        return redirect('payments:paiement_detail', paiement_id=paiement.id)
    
    context = {
        'paiement': paiement,
        'title': f'Reçu #{paiement.id}'
    }
    return render(request, 'payments/recu_imprimable.html', context)

@admin_or_role_required('Rserveur')
def nouveau_paiement(request):
    """Créer un nouveau paiement (et admin)"""
    
    if request.method == 'POST':
        commande_id = request.POST.get('commande')
        methode = request.POST.get('methode')
        montant = request.POST.get('montant')
        
        if not commande_id or not methode or not montant:
            messages.error(request, 'Veuillez remplir tous les champs.')
            return redirect('payments:nouveau_paiement')
        
        try:
            montant = float(montant)
            if montant <= 0:
                raise ValueError()
        except ValueError:
            messages.error(request, 'Montant invalide.')
            return redirect('payments:nouveau_paiement')
        
        # Vérifier si un paiement existe déjà pour cette commande
        try:
            paiement_existant = Paiement.objects.get(commande_id=commande_id)
            messages.warning(request, f'Un paiement existe déjà pour la commande #{commande_id}. Redirection vers le paiement existant.')
            return redirect('payments:paiement_detail', paiement_id=paiement_existant.id)
        except Paiement.DoesNotExist:
            # Créer le paiement
            paiement = Paiement.objects.create(
                commande_id=commande_id,
                methode=methode,
                montant=montant,
                caissier=request.user
            )
            
            messages.success(request, f'Paiement #{paiement.id} enregistré avec succès!')
            return redirect('payments:paiement_detail', paiement_id=paiement.id)
    
    # Récupérer les commandes non payées
    from orders.models import Commande, EtatCommande
    commandes_query = Commande.objects.exclude(
        id__in=Paiement.objects.values_list('commande_id', flat=True)
    ).filter(
        etat__in=[EtatCommande.TERMINEE, EtatCommande.EN_COURS, EtatCommande.EN_PREPARATION]
    ).order_by('-date_commande')
    
    # Si une commande est spécifiée en paramètre, l'inclure même si elle a déjà un paiement
    commande_id_param = request.GET.get('commande')
    commande_avec_paiement = None
    
    if commande_id_param:
        try:
            commande_specifique = Commande.objects.get(id=commande_id_param)
            # Vérifier si la commande a déjà un paiement
            try:
                paiement_existant = Paiement.objects.get(commande_id=commande_id_param)
                commande_avec_paiement = commande_specifique
                messages.info(request, f'La commande #{commande_id_param} a déjà un paiement enregistré. Vous pouvez le consulter mais pas le modifier.')
            except Paiement.DoesNotExist:
                # Ajouter la commande spécifique si elle n'est pas déjà dans la liste
                if not commandes_query.filter(id=commande_id_param).exists():
                    commandes_query = Commande.objects.filter(
                        Q(id=commande_id_param) | 
                        Q(id__in=commandes_query.values('id'))
                    ).distinct().order_by('-date_commande')
        except Commande.DoesNotExist:
            messages.error(request, f'La commande #{commande_id_param} n\'existe pas.')
    
    commandes = commandes_query
    
    methodes = MethodePaiement.choices
    context = {
        'commandes': commandes,
        'methodes': methodes
    }
    return render(request, 'payments/nouveau_paiement.html', context)

@admin_or_financial_required
def caisse_dashboard(request):
    """Tableau de bord de la caisse (et admin)"""
    caisse = Caisse.get_instance()
    
    # Statistiques du jour
    today = timezone.now().date()
    paiements_aujourdhui = Paiement.objects.filter(date_paiement__date=today)
    total_aujourdhui = paiements_aujourdhui.aggregate(Sum('montant'))['montant__sum'] or 0
    nb_paiements_aujourdhui = paiements_aujourdhui.count()
    
    # Importer les dépenses pour calculer les sorties
    from expenses.models import Depense
    depenses_aujourdhui = Depense.objects.filter(date_depense=today)
    total_sorties_aujourdhui = depenses_aujourdhui.aggregate(Sum('montant'))['montant__sum'] or 0
    
    # Calculer le solde actuel (entrées - sorties)
    solde_calculé = total_aujourdhui - total_sorties_aujourdhui
    
    # Statistiques par méthode (simplifié)
    stats_par_methode = []
    for methode_choice, methode_label in MethodePaiement.choices:
        paiements_methode = paiements_aujourdhui.filter(methode=methode_choice)
        total_methode = paiements_methode.aggregate(Sum('montant'))['montant__sum'] or 0
        count_methode = paiements_methode.count()
        stats_par_methode.append({
            'methode': methode_choice,
            'methode_label': methode_label,
            'total': total_methode,
            'count': count_methode
        })
    
    # Trier par total décroissant
    stats_par_methode.sort(key=lambda x: x['total'], reverse=True)
    
    context = {
        'caisse': caisse,
        'total_aujourdhui': total_aujourdhui,
        'total_sorties_aujourdhui': total_sorties_aujourdhui,
        'solde_calculé': solde_calculé,
        'nb_paiements_aujourdhui': nb_paiements_aujourdhui,
        'stats_par_methode': stats_par_methode
    }
    
    return render(request, 'payments/caisse_dashboard.html', context)

@require_POST
@login_required
def ajouter_montant_caisse(request):
    """Ajouter un montant à la caisse"""
    montant = request.POST.get('montant')
    
    if not montant:
        messages.error(request, 'Veuillez spécifier un montant.')
        return redirect('payments:caisse_dashboard')
    
    try:
        from decimal import Decimal
        montant = Decimal(montant)
        if montant <= 0:
            raise ValueError()
    except ValueError:
        messages.error(request, 'Montant invalide.')
        return redirect('payments:caisse_dashboard')
    
    caisse = Caisse.get_instance()
    caisse.ajouter_montant(montant)
    
    messages.success(request, f'{montant} GNF ajoutés à la caisse.')
    return redirect('payments:caisse_dashboard')

@require_POST
@login_required
def retirer_montant_caisse(request):
    """Retirer un montant de la caisse"""
    montant = request.POST.get('montant')
    
    if not montant:
        messages.error(request, 'Veuillez spécifier un montant.')
        return redirect('payments:caisse_dashboard')
    
    try:
        montant = float(montant)
        if montant <= 0:
            raise ValueError()
    except ValueError:
        messages.error(request, 'Montant invalide.')
        return redirect('payments:caisse_dashboard')
    
    caisse = Caisse.get_instance()
    if caisse.solde_actuel >= montant:
        caisse.retirer_montant(montant)
        messages.success(request, f'{montant} GNF retirés de la caisse.')
    else:
        messages.error(request, 'Solde insuffisant dans la caisse.')
    
    return redirect('payments:caisse_dashboard')

@login_required
def rapport_paiements(request):
    """Rapport des paiements"""
    # Période par défaut : ce mois
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    date_debut = request.GET.get('date_debut', month_start)
    date_fin = request.GET.get('date_fin', today)
    
    try:
        if isinstance(date_debut, str):
            date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
        if isinstance(date_fin, str):
            date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
    except ValueError:
        date_debut = month_start
        date_fin = today
    
    paiements = Paiement.objects.filter(
        date_paiement__date__gte=date_debut,
        date_paiement__date__lte=date_fin
    )
    
    # Statistiques
    total = paiements.aggregate(Sum('montant'))['montant__sum'] or 0
    nb_paiements = paiements.count()
    
    # Par méthode
    stats_par_methode = []
    methode_stats = paiements.values('methode').annotate(
        total=Sum('montant'),
        count=Count('id')
    ).order_by('-total')
    
    # Convertir les dictionnaires en objets simples et normaliser les méthodes
    for stat in methode_stats:
        methode = stat['methode']
        if methode == 'ESPECE':
            methode_affichage = 'Espèce'
        elif methode == 'CARTE':
            methode_affichage = 'Carte bancaire'
        elif methode == 'MOBILE_MONEY':
            methode_affichage = 'Mobile money'
        elif methode == 'VIREMENT':
            methode_affichage = 'Virement bancaire'
        elif methode == 'CHEQUE':
            methode_affichage = 'Chèque'
        else:
            methode_affichage = methode
        
        stats_par_methode.append({
            'methode': methode,
            'methode_affichage': methode_affichage,
            'total': stat['total'],
            'count': stat['count']
        })
    
    context = {
        'paiements': paiements,
        'total': total,
        'nb_paiements': nb_paiements,
        'stats_par_methode': stats_par_methode,
        'date_debut': date_debut,
        'date_fin': date_fin
    }
    
    return render(request, 'payments/rapport_paiements.html', context)

@admin_or_financial_required
def telecharger_recu(request, commande_id):
    """Télécharger le reçu PDF professionnel d'une seule page pour une commande payée (et admin)"""
    
    try:
        # Récupérer la commande et le paiement
        from orders.models import Commande
        commande = Commande.objects.get(id=commande_id)
        paiement = Paiement.objects.get(commande=commande)
        
        # Créer le buffer pour le PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              leftMargin=20, rightMargin=20, topMargin=20, bottomMargin=20)
        
        # Styles professionnels
        styles = getSampleStyleSheet()
        
        # Style pour le titre principal
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            spaceAfter=15,
            alignment=TA_CENTER,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            borderWidth=0,
            padding=0
        )
        
        # Style pour le sous-titre
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.grey,
            fontName='Helvetica',
            borderWidth=0,
            padding=0
        )
        
        # Style pour les sections
        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=12,
            alignment=TA_LEFT,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderPadding=0,
            padding=0
        )
        
        # Style pour les tableaux de données
        data_table_style = TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.lightgrey),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
        ])
        
        # Style pour le tableau des articles
        articles_table_style = TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.lightgrey),
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
        ])
        
        # Style pour le total
        total_style = TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgreen),
            ('LINEABOVE', (0, 0), (-1, -1), 2, colors.green),
        ])
        
        # Style pour le pied de page
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            spaceBefore=25,
            alignment=TA_CENTER,
            textColor=colors.grey,
            fontName='Helvetica',
            borderWidth=0,
            padding=0
        )
        
        # Contenu du reçu professionnel
        story = []
        
        # En-tête avec bordure double
        story.append(Paragraph("REÇU DE PAIEMENT", title_style))
        story.append(Paragraph(f"Reçu #{paiement.id}", subtitle_style))
        
        # Ligne de séparation
        story.append(Spacer(1, 10))
        
        # Informations du restaurant
        restaurant_data = [
            ["RESTAURANT", ""],
            ["Adresse complète du restaurant", ""],
            ["Téléphone: +224 XXX XXX XXX", ""],
            ["Email: contact@restaurant.com", ""],
            ["NIF: XXXXXXXXX | RCCM: XXXXXXXXX", ""],
        ]
        
        restaurant_table = Table(restaurant_data, colWidths=[4*inch, 2*inch])
        restaurant_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(restaurant_table)
        story.append(Spacer(1, 12))
        
        # Section commande
        story.append(Paragraph("INFORMATIONS DE LA COMMANDE", section_style))
        
        commande_data = [
            ["Numéro de commande:", f"#{commande.id}"],
            ["Table:", f"Table {commande.table.numero_table}"],
            ["Date:", commande.date_commande.strftime('%d/%m/%Y à %H:%M')],
            ["Serveur:", commande.serveur.login if commande.serveur else "N/A"],
        ]
        
        commande_table = Table(commande_data, colWidths=[3.5*inch, 2.5*inch])
        commande_table.setStyle(data_table_style)
        
        story.append(commande_table)
        story.append(Spacer(1, 12))
        
        # Section articles
        story.append(Paragraph("DÉTAIL DES ARTICLES", section_style))
        
        # En-tête du tableau des articles
        articles_data = [["Article", "Quantité", "Prix unitaire", "Total"]]
        
        # Ajouter les articles (limité pour tenir sur une page)
        max_articles = 6  # Réduit de 8 à 6 articles
        articles_count = 0
        for item in commande.commandeplat_set.all():
            if articles_count >= max_articles:
                break
            articles_data.append([
                item.plat.nom[:25],  # Limiter la longueur du nom
                str(item.quantite),
                f"{item.prix_unitaire:,} GNF",  # Formatage avec séparateur de milliers
                f"{item.sous_total():,} GNF"
            ])
            articles_count += 1
        
        # Ligne de total
        articles_data.append(["", "", "TOTAL:", f"{commande.total:,} GNF"])
        
        articles_table = Table(articles_data, colWidths=[3.2*inch, 1*inch, 1.4*inch, 1.4*inch])
        articles_table.setStyle(articles_table_style)
        
        # Appliquer un style spécial pour la ligne de total
        articles_table.setStyle(TableStyle([
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
            ('ALIGN', (0, -1), (-1, -1), 'LEFT'),
            ('ALIGN', (1, -1), (-1, -1), 'CENTER'),
            ('ALIGN', (2, -1), (-1, -1), 'RIGHT'),
            ('ALIGN', (3, -1), (-1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 12),
            ('TOPPADDING', (0, -1), (-1, -1), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgreen),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.green),
        ]))
        
        story.append(articles_table)
        story.append(Spacer(1, 15))
        
        # Section paiement
        story.append(Paragraph("INFORMATIONS DE PAIEMENT", section_style))
        
        paiement_data = [
            ["Méthode de paiement:", paiement.get_methode_display()],
            ["Montant payé:", f"{paiement.montant:,} GNF"],
            ["Date de paiement:", paiement.date_paiement.strftime('%d/%m/%Y à %H:%M')],
            ["Caissier:", paiement.caissier.login if paiement.caissier else "N/A"],
        ]
        
        paiement_table = Table(paiement_data, colWidths=[3.5*inch, 2.5*inch])
        paiement_table.setStyle(data_table_style)
        
        story.append(paiement_table)
        story.append(Spacer(1, 20))
        
        # Zone de cachet
        cachet_data = [["", ""]]
        cachet_table = Table(cachet_data, colWidths=[3*inch, 3*inch])
        cachet_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LINEBELOW', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('LINEABOVE', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('PADDING', (0, 0), (-1, -1), 20),
        ]))
        
        story.append(cachet_table)
        story.append(Paragraph("CACHET ET SIGNATURE", subtitle_style))
        
        # Pied de page professionnel
        story.append(Paragraph("MERCI POUR VOTRE CONFIANCE !", footer_style))
        story.append(Paragraph("Ce reçu est généré automatiquement et constitue une preuve de paiement valide.", footer_style))
        story.append(Paragraph(f"Document généré le {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}", footer_style))
        
        # Générer le PDF professionnel
        doc.build(story)
        
        # Préparer la réponse HTTP
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="recu_paiement_{paiement.id}_{commande.id}.pdf"'
        
        return response
        
    except Commande.DoesNotExist:
        messages.error(request, "Commande introuvable.")
        return redirect('restaurant:table_commandes')
    except Paiement.DoesNotExist:
        messages.error(request, "Aucun paiement trouvé pour cette commande.")
        return redirect('restaurant:table_commandes')
