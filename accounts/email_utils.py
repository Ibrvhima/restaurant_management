from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from django.db import models
from decimal import Decimal
import io
from .pdf_utils import export_dashboard_pdf

def send_daily_balance_report(date=None):
    """Envoyer un rapport quotidien du solde de caisse par email à l'administrateur"""
    from accounts.models import User
    from payments.models import Paiement
    from expenses.models import Depense
    
    # Utiliser la date du jour si non spécifiée
    if date is None:
        date = timezone.now().date()
    
    # Calculer les statistiques
    total_entrées = Paiement.objects.filter(date_paiement__date=date).aggregate(
        total=models.Sum('montant')
    )['total'] or 0
    
    total_sorties = Depense.objects.filter(date_depense=date).aggregate(
        total=models.Sum('montant')
    )['total'] or 0
    
    solde_jour = total_entrées - total_sorties
    
    # Solde cumulé
    total_entrées_cumul = Paiement.objects.aggregate(total=models.Sum('montant'))['total'] or 0
    total_sorties_cumul = Depense.objects.aggregate(total=models.Sum('montant'))['total'] or 0
    solde_cumul = total_entrées_cumul - total_sorties_cumul
    
    # Récupérer les administrateurs
    admins = User.objects.filter(role='Radmin', actif=True)
    
    if not admins.exists():
        print("Aucun administrateur actif trouvé pour l'envoi du rapport")
        return False
    
    # Préparer le contexte pour l'email
    context = {
        'date': date,
        'total_entrées': total_entrées,
        'total_sorties': total_sorties,
        'solde_jour': solde_jour,
        'solde_cumul': solde_cumul,
        'nombre_paiements': Paiement.objects.filter(date_paiement__date=date).count(),
        'nombre_depenses': Depense.objects.filter(date_depense=date).count(),
        'paiements': Paiement.objects.filter(date_paiement__date=date).order_by('-date_paiement')[:10],
        'depenses': Depense.objects.filter(date_depense=date).order_by('-date_depense')[:10],
    }
    
    # Générer le contenu HTML de l'email
    sujet = f"📊 Rapport Journalier Caisse - {date.strftime('%d/%m/%Y')}"
    
    message_html = render_to_string('accounts/email_daily_report.html', context)
    
    # Générer le PDF en pièce jointe
    try:
        # Créer une requête factice pour l'export PDF
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/')
        
        # Générer le PDF
        pdf_response = export_dashboard_pdf(request)
        pdf_content = pdf_response.content
        
        # Envoyer l'email avec pièce jointe
        success_count = 0
        for admin in admins:
            try:
                from django.core.mail import EmailMessage
                email = EmailMessage(
                    sujet,
                    message_html,
                    settings.DEFAULT_FROM_EMAIL,
                    [admin.login],  # Utiliser le login comme email (adapter selon besoin)
                )
                email.content_subtype = 'html'
                
                # Ajouter la pièce jointe PDF
                email.attach(
                    f'rapport_caisse_{date.strftime("%Y%m%d")}.pdf',
                    pdf_content,
                    'application/pdf'
                )
                
                email.send()
                success_count += 1
                print(f"Email envoyé à l'administrateur: {admin.login}")
                
            except Exception as e:
                print(f"Erreur lors de l'envoi à {admin.login}: {str(e)}")
        
        return success_count > 0
        
    except Exception as e:
        print(f"Erreur lors de la génération du PDF: {str(e)}")
        return False

def send_balance_alert(solde, seuil_alerte=100000):
    """Envoyer une alerte email si le solde de caisse est bas"""
    from accounts.models import User
    
    if solde < seuil_alerte:
        admins = User.objects.filter(role='Radmin', actif=True)
        
        if not admins.exists():
            return False
        
        sujet = f"⚠️ ALERTE CAISSE - Solde Critique: {solde:,.0f} GNF"
        
        message_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #dc3545; margin: 0;">⚠️ ALERTE CAISSE</h1>
                    <h2 style="color: #dc3545; margin: 10px 0;">Solde Critique Détecté</h2>
                </div>
                
                <div style="background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 0; font-size: 18px; color: #721c24;">
                        <strong>Solde actuel:</strong> <span style="font-size: 24px; color: #dc3545;">{solde:,.0f} GNF</span>
                    </p>
                    <p style="margin: 10px 0 0 0; color: #721c24;">
                        <strong>Seuil d'alerte:</strong> {seuil_alerte:,.0f} GNF
                    </p>
                </div>
                
                <div style="margin: 30px 0;">
                    <h3 style="color: #333; margin-bottom: 15px;">Actions recommandées:</h3>
                    <ul style="color: #666; line-height: 1.6;">
                        <li>Vérifier les dépenses récentes</li>
                        <li>Confirmer que tous les paiements ont été enregistrés</li>
                        <li>Envisager un apport en caisse si nécessaire</li>
                        <li>Contacter le gestionnaire si le solde continue de baisser</li>
                    </ul>
                </div>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 14px;">
                    <p>Ceci est une alerte automatique du système Restaurant Management</p>
                    <p>Date: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        success_count = 0
        for admin in admins:
            try:
                send_mail(
                    sujet,
                    "Alerte caisse - Veuillez consulter le système pour plus de détails.",
                    settings.DEFAULT_FROM_EMAIL,
                    [admin.login],  # Adapter selon la configuration email
                    html_message=message_html,
                    fail_silently=False,
                )
                success_count += 1
                print(f"Alerte envoyée à l'administrateur: {admin.login}")
                
            except Exception as e:
                print(f"Erreur lors de l'envoi de l'alerte à {admin.login}: {str(e)}")
        
        return success_count > 0
    
    return True  # Pas d'alerte nécessaire

def update_daily_balance(date=None):
    """Mettre à jour automatiquement le solde de caisse pour une date donnée"""
    from payments.models import Paiement
    from expenses.models import Depense
    
    if date is None:
        date = timezone.now().date()
    
    # Calculer le solde du jour
    total_entrées = Paiement.objects.filter(date_paiement__date=date).aggregate(
        total=models.Sum('montant')
    )['total'] or 0
    
    total_sorties = Depense.objects.filter(date_depense=date).aggregate(
        total=models.Sum('montant')
    )['total'] or 0
    
    solde_jour = total_entrées - total_sorties
    
    # Mettre à jour le solde cumulé
    total_entrées_cumul = Paiement.objects.aggregate(total=models.Sum('montant'))['total'] or 0
    total_sorties_cumul = Depense.objects.aggregate(total=models.Sum('montant'))['total'] or 0
    solde_cumul = total_entrées_cumul - total_sorties_cumul
    
    # Envoyer le rapport quotidien
    rapport_envoye = send_daily_balance_report(date)
    
    # Envoyer une alerte si le solde est critique
    alerte_envoyee = send_balance_alert(solde_cumul)
    
    return {
        'date': date,
        'solde_jour': solde_jour,
        'solde_cumul': solde_cumul,
        'rapport_envoye': rapport_envoye,
        'alerte_envoyee': alerte_envoyee,
        'total_entrées': total_entrées,
        'total_sorties': total_sorties,
    }
