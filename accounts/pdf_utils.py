from django.http import HttpResponse
from django.utils import timezone
from django.db import models
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import io

def export_dashboard_pdf(request):
    """Exporter les données du dashboard en format PDF"""
    # Récupérer les données
    from orders.models import Commande, EtatCommande
    from restaurant.models import Plat
    from payments.models import Paiement
    from expenses.models import Depense
    
    today = timezone.now().date()
    
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
    paiements_aujourdhui = Paiement.objects.filter(date_paiement__date=today).count()
    total_ventes_aujourdhui = Paiement.objects.filter(date_paiement__date=today).aggregate(
        total=models.Sum('montant')
    )['total'] or 0
    
    # Statistiques des dépenses du jour
    depenses_aujourdhui = Depense.objects.filter(date_depense=today).count()
    total_depenses_aujourdhui = Depense.objects.filter(date_depense=today).aggregate(
        total=models.Sum('montant')
    )['total'] or 0
    
    # Solde de caisse
    total_entrées = Paiement.objects.aggregate(total=models.Sum('montant'))['total'] or 0
    total_sorties = Depense.objects.aggregate(total=models.Sum('montant'))['total'] or 0
    solde_caisse = total_entrées - total_sorties
    
    # Créer le buffer
    buffer = io.BytesIO()
    
    # Créer le document PDF
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=30,
        alignment=1,  # center
        textColor=colors.HexColor('#2E86AB')
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20,
        textColor=colors.HexColor('#2E86AB')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.HexColor('#2E86AB')
    )
    
    # Contenu
    story = []
    
    # Titre
    story.append(Paragraph("RAPPORT DASHBOARD RESTAURANT", title_style))
    story.append(Paragraph(f"Date: {today.strftime('%d/%m/%Y')}", styles['Normal']))
    story.append(Paragraph(f"Généré le {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Section Statistiques
    story.append(Paragraph("STATISTIQUES GLOBALES", subtitle_style))
    
    # Tableau des statistiques
    stats_data = [
        ['Catégorie', 'Indicateur', 'Valeur', 'Détails'],
        ['Commandes', 'Total', str(total_commandes), ''],
        ['', 'En cours', str(commandes_en_cours), f"{(commandes_en_cours/total_commandes*100):.1f}%" if total_commandes > 0 else "0%"],
        ['', 'Terminées', str(commandes_terminees), f"{(commandes_terminees/total_commandes*100):.1f}%" if total_commandes > 0 else "0%"],
        ['Plats', 'Total', str(total_plats), ''],
        ['', 'Disponibles', str(plats_disponibles), f"{(plats_disponibles/total_plats*100):.1f}%" if total_plats > 0 else "0%"],
        ['Paiements du jour', 'Nombre', str(paiements_aujourdhui), ''],
        ['', 'Montant total', f"{total_ventes_aujourdhui:,.0f} GNF", ''],
        ['Dépenses du jour', 'Nombre', str(depenses_aujourdhui), ''],
        ['', 'Montant total', f"{total_depenses_aujourdhui:,.0f} GNF", ''],
        ['Caisse', 'Total entrées', f"{total_entrées:,.0f} GNF", ''],
        ['', 'Total sorties', f"{total_sorties:,.0f} GNF", ''],
        ['', 'Solde actuel', f"{solde_caisse:,.0f} GNF", 'POSITIF' if solde_caisse >= 0 else 'NÉGATIF'],
    ]
    
    stats_table = Table(stats_data, colWidths=[1.5*inch, 1.5*inch, 1.2*inch, 1.2*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    # Couleur spéciale pour le solde
    if solde_caisse >= 0:
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, -1), (2, -1), colors.HexColor('#D4EDDA')),
            ('TEXTCOLOR', (0, -1), (2, -1), colors.HexColor('#155724')),
        ]))
    else:
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, -1), (2, -1), colors.HexColor('#F8D7DA')),
            ('TEXTCOLOR', (0, -1), (2, -1), colors.HexColor('#721C24')),
        ]))
    
    story.append(stats_table)
    story.append(Spacer(1, 20))
    
    # Section Transactions du jour
    story.append(Paragraph("TRANSACTIONS DU JOUR", subtitle_style))
    
    # Paiements du jour
    story.append(Paragraph("Paiements", heading_style))
    
    paiements_du_jour = Paiement.objects.filter(date_paiement__date=today).order_by('-date_paiement')
    if paiements_du_jour:
        paiements_data = [['ID', 'Commande', 'Montant', 'Méthode', 'Heure']]
        for paiement in paiements_du_jour:
            paiements_data.append([
                str(paiement.id),
                f"#{paiement.commande.id}",
                f"{paiement.montant:,.0f} GNF",
                paiement.get_methode_display(),
                paiement.date_paiement.strftime('%H:%M:%S')
            ])
        
        paiements_table = Table(paiements_data, colWidths=[0.8*inch, 0.8*inch, 1.2*inch, 1.2*inch, 1*inch])
        paiements_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28A745')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        story.append(paiements_table)
    else:
        story.append(Paragraph("Aucun paiement aujourd'hui", styles['Normal']))
    
    story.append(Spacer(1, 15))
    
    # Dépenses du jour
    story.append(Paragraph("Dépenses", heading_style))
    
    depenses_du_jour = Depense.objects.filter(date_depense=today).order_by('-date_depense')
    if depenses_du_jour:
        depenses_data = [['ID', 'Description', 'Montant', 'Utilisateur']]
        for depense in depenses_du_jour:
            depenses_data.append([
                str(depense.id),
                depense.description[:30] + '...' if len(depense.description) > 30 else depense.description,
                f"{depense.montant:,.0f} GNF",
                depense.utilisateur.login if depense.utilisateur else "N/A"
            ])
        
        depenses_table = Table(depenses_data, colWidths=[0.8*inch, 2*inch, 1.2*inch, 1.2*inch])
        depenses_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DC3545')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        story.append(depenses_table)
    else:
        story.append(Paragraph("Aucune dépense aujourd'hui", styles['Normal']))
    
    # Pied de page
    story.append(Spacer(1, 30))
    story.append(Paragraph(f"Rapport généré automatiquement par Restaurant Management System", styles['Normal']))
    
    # Générer le PDF
    doc.build(story)
    
    # Préparer la réponse HTTP
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=dashboard_restaurant_{today.strftime("%Y%m%d")}.pdf'
    
    return response
