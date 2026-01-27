from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import qrcode
import io
import base64


class Categorie(models.Model):
    """
    Modèle pour les catégories de plats
    """
    nom = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nom de la catégorie'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class TableRestaurant(models.Model):
    """
    Modèle pour les tables du restaurant
    """
    numero_table = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='Numéro de table'
    )
    nombre_places = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        verbose_name='Nombre de places',
        default=4
    )
    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='table',
        limit_choices_to={'role': 'Rtable'},
        verbose_name='Utilisateur associé',
        null=True,
        blank=True
    )
    est_occupee = models.BooleanField(
        default=False,
        verbose_name='Table occupée'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tables_restaurant'
        verbose_name = 'Table'
        verbose_name_plural = 'Tables'
        ordering = ['numero_table']
    
    def __str__(self):
        return f"Table {self.numero_table} ({self.nombre_places} places)"


class Plat(models.Model):
    """
    Modèle pour les plats du restaurant
    """
    TYPE_PLAT_CHOICES = [
        ('entree', 'Entrée'),
        ('principal', 'Plat principal'),
        ('special', 'Plat spécial'),
        ('dessert', 'Dessert'),
        ('boisson', 'Boisson'),
        ('accompagnement', 'Accompagnement'),
    ]
    
    nom = models.CharField(
        max_length=200,
        verbose_name='Nom du plat'
    )
    prix_unitaire = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Prix unitaire'
    )
    type_plat = models.CharField(
        max_length=20,
        choices=TYPE_PLAT_CHOICES,
        default='principal',
        verbose_name='Type de plat'
    )
    image = models.ImageField(
        upload_to='plats/',
        blank=True,
        null=True,
        verbose_name='Image du plat'
    )
    disponible = models.BooleanField(
        default=True,
        verbose_name='Disponible'
    )
    necessite_preparation = models.BooleanField(
        default=True,
        verbose_name='Nécessite une préparation en cuisine',
        help_text='Décochez pour les boissons, desserts froids, etc.'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description'
    )
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Catégorie'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'plats'
        verbose_name = 'Plat'
        verbose_name_plural = 'Plats'
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} - {self.prix_unitaire} FCFA"

class Panier(models.Model):
    """
    Modèle pour les paniers (temporaire, lié à une table)
    """
    table = models.OneToOneField(
        TableRestaurant,
        on_delete=models.CASCADE,
        related_name='panier',
        verbose_name='Table'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'paniers'
        verbose_name = 'Panier'
        verbose_name_plural = 'Paniers'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Panier Table {self.table.numero_table}"

class PanierItem(models.Model):
    """
    Modèle pour les items dans un panier
    """
    panier = models.ForeignKey(
        Panier,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Panier'
    )
    plat = models.ForeignKey(
        Plat,
        on_delete=models.CASCADE,
        verbose_name='Plat'
    )
    quantite = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Quantité'
    )
    prix_unitaire = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Prix unitaire'
    )
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'panier_items'
        verbose_name = 'Item du panier'
        verbose_name_plural = 'Items du panier'
        unique_together = ['panier', 'plat']
        ordering = ['-date_ajout']
    
    def __str__(self):
        return f"{self.plat.nom} x{self.quantite}"
    
    def sous_total(self):
        """Calcule le sous-total de l'item"""
        return self.prix_unitaire * self.quantite


class QRCode(models.Model):
    """Modèle pour stocker les QR codes des tables"""
    table = models.OneToOneField(TableRestaurant, on_delete=models.CASCADE, related_name='qr_code')
    code = models.CharField(max_length=255, unique=True)
    qr_code_image = models.TextField(blank=True, null=True)
    date_generation = models.DateTimeField(auto_now_add=True)
    est_actif = models.BooleanField(default=True)
    nombre_utilisations = models.PositiveIntegerField(default=0)
    dernier_scan = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'qr_codes'
        verbose_name = 'Code QR'
        verbose_name_plural = 'Codes QR'
        ordering = ['-date_generation']
    
    def __str__(self):
        return "QR Code - Table {}".format(self.table.numero_table)
    
    def generer_qr_code(self):
        """Génère le QR code et le stocke en base64"""
        import qrcode
        from io import BytesIO
        import base64
        
        # URL vers laquelle le QR code pointera (page de détails de la table)
        from django.conf import settings
        
        # Détection de l'environnement
        if hasattr(settings, 'PRODUCTION_URL') and settings.PRODUCTION_URL:
            # En production (Render)
            base_url = settings.PRODUCTION_URL
        else:
            # En développement local
            import socket
            local_ip = None
            try:
                # Obtenir l'IP locale
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                
                # Vérifier si c'est une IP locale valide
                if local_ip.startswith('127.') or local_ip == 'localhost':
                    # Alternative: connexion internet pour obtenir l'IP
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.connect(("8.8.8.8", 80))
                    local_ip = s.getsockname()[0]
                    s.close()
                    
            except Exception:
                local_ip = "192.168.1.100"
            
            base_url = "http://{}:8000".format(local_ip)
        
        url = "{}/restaurant/table/{}/".format(base_url, self.table.id)
        
        # Créer le QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        # Créer l'image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir en base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        self.qr_code_image = qr_code_base64
        self.save()
    
    def est_valide(self):
        """Vérifie si le QR code est valide (actif)"""
        return self.est_actif
    
    def incrementer_utilisation(self):
        """Incrémente le compteur d'utilisation"""
        self.nombre_utilisations += 1
        self.dernier_scan = timezone.now()
        self.save()
