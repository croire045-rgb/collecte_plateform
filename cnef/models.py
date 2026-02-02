from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import FileExtensionValidator, EmailValidator
from django.utils import timezone
from django.urls import reverse
import numpy_financial as npf
import secrets
import string
from datetime import timedelta

# ==========================================
# GESTION DES ÉTABLISSEMENTS
# ==========================================

class Etablissement(models.Model):
    """Modèle pour enregistrer les établissements dans la base CNEF"""
    TYPE_CHOICES = [
        ('BANQUE', 'Banque'),
        ('EMF', 'Établissement de Microfinance'),
    ]
    
    CATEGORIE_EMF_CHOICES = [
        ('PREMIERE_CATEGORIE', '1re Catégorie'),
        ('DEUXIEME_CATEGORIE', '2e Catégorie'),
        ('TROISIEME_CATEGORIE', '3e Catégorie'),
    ]
    
    Nom_etablissement = models.CharField(max_length=100, unique=True, verbose_name="Nom de l'établissement")
    code_etablissement = models.CharField(max_length=50, unique=True, verbose_name="Code établissement")
    type_etablissement = models.CharField(max_length=35, choices=TYPE_CHOICES, verbose_name="Type d'établissement")
    categorie_emf = models.CharField(
        max_length=20, 
        choices=CATEGORIE_EMF_CHOICES, 
        verbose_name="Catégorie EMF",
        blank=True, 
        null=True
    )
    is_active = models.BooleanField(default=True, verbose_name="Établissement actif")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Établissement CNEF"
        verbose_name_plural = "Établissements CNEF"
        ordering = ['Nom_etablissement']
    
    def __str__(self):
        return f"{self.Nom_etablissement} ({self.code_etablissement})"

    def clean(self):
        super().clean()
        if self.type_etablissement == 'EMF' and not self.categorie_emf:
            raise ValidationError({
                'categorie_emf': "Veuillez sélectionner une catégorie pour les EMF"
            })
        if self.type_etablissement == 'BANQUE' and self.categorie_emf:
            self.categorie_emf = None


# ==========================================
# GESTION DES UTILISATEURS AVEC RÔLES
# ==========================================

class UserManager(BaseUserManager):
    """Manager personnalisé pour le modèle User"""
    
    def create_user(self, email, nom, prenom, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse e-mail est obligatoire")
        if not nom or not prenom:
            raise ValueError("Le nom et le prénom sont obligatoires")
        
        email = self.normalize_email(email)
        user = self.model(email=email, nom=nom, prenom=prenom, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, nom, prenom, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ACNEF')
        return self.create_user(email, nom, prenom, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Modèle utilisateur avec gestion des rôles"""
    
    ROLE_CHOICES = [
        ('ACNEF', 'Administrateur CNEF'),
        ('UCNEF', 'Utilisateur CNEF'),
        ('AEF', 'Administrateur Établissement Financier'),
        ('UEF', 'Utilisateur Établissement Financier'),
    ]
    
    # Informations de base
    email = models.EmailField(
        max_length=255, 
        unique=True, 
        verbose_name="Adresse e-mail",
        validators=[EmailValidator(message="Veuillez entrer une adresse e-mail valide")]
    )
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone")
    
    # Rôle et établissement
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name="Rôle")
    etablissement = models.ForeignKey(
        Etablissement, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='utilisateurs',
        verbose_name="Établissement"
    )
    
    # Permissions système
    is_active = models.BooleanField(default=True, verbose_name="Compte actif")
    is_staff = models.BooleanField(default=False, verbose_name="Membre du staff")
    
    # Métadonnées
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    derniere_connexion = models.DateTimeField(null=True, blank=True, verbose_name="Dernière connexion")
    
    # Créé par (pour traçabilité)
    cree_par = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='utilisateurs_crees',
        verbose_name="Créé par"
    )
    
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom']
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.get_role_display()})"
    
    def get_full_name(self):
        return f"{self.prenom} {self.nom}"
    
    def get_short_name(self):
        return self.prenom
    
    def clean(self):
        """Validation pour s'assurer que les établissements sont correctement assignés"""
        super().clean()
        
        # AEF et UEF DOIVENT avoir un établissement
        if self.role in ['AEF', 'UEF'] and not self.etablissement:
            raise ValidationError({
                'etablissement': "Un établissement est obligatoire pour les rôles AEF et UEF"
            })
        
        # ACNEF et UCNEF NE DOIVENT PAS avoir d'établissement
        if self.role in ['ACNEF', 'UCNEF'] and self.etablissement:
            raise ValidationError({
                'etablissement': "Les rôles ACNEF et UCNEF ne peuvent pas être associés à un établissement"
            })
    
    # ==========================================
    # MÉTHODES DE VÉRIFICATION DES RÔLES
    # ==========================================
    
    def is_acnef(self):
        """Vérifie si l'utilisateur est un Administrateur CNEF"""
        return self.role == 'ACNEF'
    
    def is_ucnef(self):
        """Vérifie si l'utilisateur est un Utilisateur CNEF"""
        return self.role == 'UCNEF'
    
    def is_aef(self):
        """Vérifie si l'utilisateur est un Administrateur Établissement"""
        return self.role == 'AEF'
    
    def is_uef(self):
        """Vérifie si l'utilisateur est un Utilisateur Établissement"""
        return self.role == 'UEF'
    
    def is_cnef_user(self):
        """Vérifie si l'utilisateur fait partie du CNEF (ACNEF ou UCNEF)"""
        return self.role in ['ACNEF', 'UCNEF']
    
    def is_etablissement_user(self):
        """Vérifie si l'utilisateur fait partie d'un établissement (AEF ou UEF)"""
        return self.role in ['AEF', 'UEF']
    
    def is_admin_role(self):
        """Vérifie si l'utilisateur a un rôle administrateur (ACNEF ou AEF)"""
        return self.role in ['ACNEF', 'AEF']
    
    # ==========================================
    # PERMISSIONS PAR RÔLE
    # ==========================================
    
    def peut_voir_vue_ensemble(self):
        """Tous les utilisateurs peuvent voir la vue d'ensemble"""
        return True
    
    def peut_voir_analyses(self):
        """ACNEF, UCNEF et AEF peuvent voir les analyses"""
        return self.role in ['ACNEF', 'UCNEF', 'AEF']
    
    def peut_gerer_soumissions(self):
        """ACNEF et UCNEF peuvent gérer les soumissions"""
        return self.role in ['ACNEF', 'UCNEF']
    
    def peut_telecharger(self):
        """ACNEF et UCNEF peuvent télécharger"""
        return self.role in ['ACNEF', 'UCNEF']
    
    def peut_voir_base_donnees(self):
        """ACNEF et UCNEF peuvent voir la base de données"""
        return self.role in ['ACNEF', 'UCNEF']
    
    def peut_gerer_utilisateurs(self):
        """Seul ACNEF peut gérer tous les utilisateurs, AEF peut gérer les UEF de son établissement"""
        return self.role in ['ACNEF', 'AEF']
    
    def peut_creer_etablissement(self):
        """Seul ACNEF peut créer des établissements"""
        return self.role == 'ACNEF'
    
    def peut_voir_tous_etablissements(self):
        """ACNEF et UCNEF peuvent voir tous les établissements"""
        return self.role in ['ACNEF', 'UCNEF']
    
    def peut_voir_son_etablissement(self):
        """AEF et UEF peuvent voir leur établissement"""
        return self.role in ['AEF', 'UEF']


# ==========================================
# GESTION DES FICHIERS ET SOUMISSIONS
# ==========================================

class EtablissementManager(models.Manager):
    """Manager personnalisé pour le modèle Etablissement"""
    
    def get_by_code(self, code):
        """Récupère un établissement par son code"""
        return self.get(code_etablissement=code)
   


class FichierImport(models.Model):
    """Modèle pour l'historique des fichiers importés"""
    STATUS_CHOICES = [
        ('EN_COURS', 'En cours'),
        ('REUSSI', 'Réussi'),
        ('ERREUR', 'Erreur'),
        ('REJETE', 'Rejeté'),
    ]
    
    
    # Nouveau système
    etablissement_cnef = models.ForeignKey(
        Etablissement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fichiers_imports',
        verbose_name="Établissement"
    )
    
    uploader_par = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fichiers_uploades',
        verbose_name="Uploadé par"
    )
    
    fichier = models.FileField(
        upload_to='imports/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        verbose_name="Fichier Excel"
    )
    nom_fichier = models.CharField(max_length=255, verbose_name="Nom du fichier")
    date_import = models.DateTimeField(auto_now_add=True, verbose_name="Date d'import")
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='EN_COURS', verbose_name="Statut")
    
    # Compteurs de lignes importées
    nb_credits_importes = models.IntegerField(default=0, verbose_name="Crédits amortissables")
    nb_decouverts_importes = models.IntegerField(default=0, verbose_name="Découverts")
    nb_affacturages_importes = models.IntegerField(default=0, verbose_name="Affacturages")
    nb_cautions_importes = models.IntegerField(default=0, verbose_name="Cautions")
    nb_effets_importes = models.IntegerField(default=0, verbose_name="Effets de commerce")
    nb_spots_importes = models.IntegerField(default=0, verbose_name="Spots")
    
    # Messages d'erreur
    erreurs = models.TextField(blank=True, null=True, verbose_name="Erreurs rencontrées")
    details = models.TextField(blank=True, null=True, verbose_name="Détails de l'import")
    
    # Validation par CNEF
    valide_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fichiers_valides',
        verbose_name="Validé par"
    )
    date_validation = models.DateTimeField(null=True, blank=True, verbose_name="Date de validation")
    commentaire_validation = models.TextField(blank=True, null=True, verbose_name="Commentaire de validation")
    
    class Meta:
        verbose_name = "Fichier importé"
        verbose_name_plural = "Fichiers importés"
        ordering = ['-date_import']
    
    def __str__(self):
        return f"{self.nom_fichier} - {self.date_import.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def total_lignes_importees(self):
        return (self.nb_credits_importes + self.nb_decouverts_importes + 
                self.nb_affacturages_importes + self.nb_cautions_importes + 
                self.nb_effets_importes + self.nb_spots_importes)
    
    def get_absolute_url(self):
        return reverse('detail_soumission', kwargs={'fichier_id': self.id})
    
    @property
    def donnees_importees(self):
        """Retourne le détail des données importées"""
        return {
            'credits': self.credits_amortissables_files.count(),
            'decouverts': self.decouverts.count(),
            'affacturages': self.affacturages.count(),
            'cautions': self.cautions.count(),
            'effets': self.effets.count(),
            'spots': self.spots.count(),
        }

# ==========================================
# MODÈLES DE DONNÉES
# ==========================================

class Credit_Amortissables(models.Model):
    """Modèle pour des crédits amortissables"""
   
    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE, related_name='credits_amortissables')
    fichier_import = models.ForeignKey(FichierImport, on_delete=models.SET_NULL, null=True, blank=True, related_name='credits_amortissables_files')

    ETABLISSEMENT_I01 = models.CharField(max_length=30, verbose_name="Établissement")
    CODE_ETAB_I02 = models.CharField(max_length=8, verbose_name="Code établissement")
    DATE_MEP_I03 = models.DateField(verbose_name="Date de mise en place")
    CHA_ORI_I04 = models.CharField(max_length=50, verbose_name="Chapitre comptable", blank=True)
    NATURE_PRET_I05 = models.CharField(max_length=75, verbose_name="Nature du prêt")
    BENEFICIAIRE_I06 = models.CharField(max_length=125, verbose_name="Bénéficiaire")
    CATEGORIE_BENEF_I07 = models.CharField(max_length=30, verbose_name="Catégorie bénéficiaire")
    LIEU_RESIDENCE_I08 = models.CharField(max_length=75, verbose_name="Lieu de résidence")
    SECT_ACT_I09 = models.CharField(max_length=50, verbose_name="Secteur d'activité")
    MONTANT_CHAF_I10 = models.FloatField(verbose_name="Montant CA", null=True, blank=True)
    EFFECTIF_I11 = models.IntegerField(verbose_name="Effectif", null=True, blank=True)
    PROFESSION_I12 = models.CharField(max_length=60, verbose_name="Profession")
    MONTANT_PRET_I13 = models.FloatField(verbose_name="Montant du prêt")
    DUREE_I14 = models.IntegerField(verbose_name="Durée (mois)")
    DUREE_DIFFERRE_I15 = models.IntegerField(verbose_name="Durée différé (mois)", default=0)
    FREQ_REMB_I16 = models.CharField(max_length=20, verbose_name="Fréquence remboursement")
    TAUX_NOMINAL_I17 = models.FloatField(verbose_name="Taux nominal (%)")
    FRAIS_DOSSIER_I18 = models.FloatField(verbose_name="Frais de dossier", default=0)
    MODALITEPAIEMENT_ASS_I19 = models.CharField(max_length=100, verbose_name="Modalité de paiement", blank=True)
    MONTANTASSURANCE_I20 = models.FloatField(verbose_name="Montant assurance", default=0)
    FRAIS_ANNEXE_I21 = models.FloatField(verbose_name="Frais annexes", default=0)
    MODEREMBOURSEMENT_I22 = models.CharField(max_length=30, verbose_name="Mode remboursement")
    MONTANT_ECHEANCE_I23 = models.FloatField(verbose_name="Montant échéance")
    MODE_DEBLOCAGE_I24 = models.CharField(max_length=50, verbose_name="Mode déblocage")
    SITUATION_CREANCE_I25 = models.CharField(max_length=20, verbose_name="Situation créance")
    TEG_I26 = models.FloatField(verbose_name="TEG ", default=0.0, null=True, blank=True)
    TEG_mensuel = models.FloatField(verbose_name="TEG mensuel", default=0.0, null=True, blank=True)
    TEG_annualise = models.FloatField(verbose_name="TEG annualisé", default=0.0, null=True, blank=True)
    
    # NOUVEAU CHAMP MATURITE
    MATURITE = models.CharField(
        max_length=10, 
        verbose_name="Maturité", 
        blank=True,
        help_text=""
    )

    def save(self, *args, **kwargs):
        # Normalisation du taux nominal
        if self.TAUX_NOMINAL_I17 and self.TAUX_NOMINAL_I17 > 1:
            self.TAUX_NOMINAL_I17 /= 100
        
        # Normalisation du TEG
        if self.TEG_I26 and self.TEG_I26 > 1:
            self.TEG_I26 /= 100
        
        # Calcul du TEG_mensuel
        try:
            if (self.DUREE_I14 and self.DUREE_I14 > 0 and 
                self.MONTANT_ECHEANCE_I23 and self.MONTANT_PRET_I13):
                
                montant_net = (self.MONTANT_PRET_I13 - 
                            (self.FRAIS_DOSSIER_I18 or 0) - 
                            (self.MONTANTASSURANCE_I20 or 0) - 
                            (self.FRAIS_ANNEXE_I21 or 0))
                
                import numpy_financial as npf
                self.TEG_mensuel = npf.rate(
                    nper=self.DUREE_I14,
                    pmt=-self.MONTANT_ECHEANCE_I23,
                    pv=montant_net,
                    fv=0
                ) * 100
            else:
                self.TEG_mensuel = 0.0
        except Exception as e:
            self.TEG_mensuel = 0.0
        
        # Calcul du TEG_annualisé
        try:
            if self.TEG_mensuel and self.FREQ_REMB_I16:
                freq = str(self.FREQ_REMB_I16).strip().lower()
                
                if freq == '1' or 'mensuel' in freq or 'mois' in freq:
                    multiplicateur = 12
                elif freq == '2' or 'trimestriel' in freq:
                    multiplicateur = 4
                elif freq == '3' or 'semestriel' in freq:
                    multiplicateur = 2
                elif freq == '4' or 'annuel' in freq:
                    multiplicateur = 1
                elif freq == '5' or 'heb' in freq or 'hebdo' in freq:
                    multiplicateur = 52
                else:
                    multiplicateur = 12
                
                self.TEG_annualise = self.TEG_mensuel * multiplicateur
            else:
                self.TEG_annualise = 0.0
        except Exception as e:
            self.TEG_annualise = 0.0
        
        # CALCUL DE LA MATURITE
        try:
            if self.DUREE_I14 is not None:
                if self.DUREE_I14 <= 24:
                    self.MATURITE = "1-CT"  # Court terme
                elif self.DUREE_I14 > 60:
                    self.MATURITE = "3-LT"  # Long terme
                else:
                    self.MATURITE = "2-MT"  # Moyen terme
            else:
                self.MATURITE = "Non définie"
        except Exception as e:
            self.MATURITE = "Erreur"
        
        super().save(*args, **kwargs)   
        
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Crédit amortissable"
        verbose_name_plural = "Crédits amortissables"
        ordering = ['-DATE_MEP_I03']   

class Decouverts(models.Model):
    """Modèle pour les découverts"""
   
    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE, related_name='decouverts')
    fichier_import = models.ForeignKey(FichierImport, on_delete=models.SET_NULL, null=True, blank=True, related_name='decouverts')
    
    SIGLE_I01 = models.CharField(max_length=30, verbose_name="Sigle")
    CODE_BANQUE_I02 = models.CharField(max_length=8, verbose_name="Code banque")
    DATE_MISE_PLACE_I03 = models.DateField(verbose_name="Date mise en place")
    BENEFICAIRE_I04 = models.CharField(max_length=125, verbose_name="Bénéficiaire")
    CATEGORIE_BENEF_I05 = models.CharField(max_length=30, verbose_name="Catégorie")
    LIEU_RESIDENCE_I06 = models.CharField(max_length=50, verbose_name="Lieu résidence")
    SECT_ACT_I07 = models.CharField(max_length=75, verbose_name="Secteur activité")
    MONTANT_DECOUVERT_I08 = models.FloatField(verbose_name="Montant découvert")
    CUMUL_TIRAGES_DEC_I09 = models.FloatField(verbose_name="Cumul tirages", default=0)
    TAUX_NOMINAL_I10 = models.FloatField(verbose_name="Taux nominal (%)")
    FRAIS_DOSSIERS_ET_COMM_I11 = models.FloatField(verbose_name="Frais/Comm", default=0)
    COUTS_ASSURANCE_I12 = models.FloatField(verbose_name="Coûts assurance", default=0)
    FRAIS_ANNEXES_I13 = models.FloatField(verbose_name="Frais annexes", default=0)
    AGIOS_I14 = models.FloatField(verbose_name="Agios", default=0)
    NOMBRE_DEBITEURS_I15 = models.IntegerField(verbose_name="Nb débiteurs", default=1)
    SITUATION_CREANCE_I16 = models.CharField(max_length=20, verbose_name="Situation créance")
    TEG_I17 = models.FloatField(verbose_name="TEG (%)", default=0.0, null=True, blank=True)
    TEG_decouvert = models.FloatField(verbose_name="TEG decouverts (%)", default=0.0, null=True, blank=True)
    
    def save(self, *args, **kwargs):
    # Normalisation du taux nominal
        if self.TAUX_NOMINAL_I10 and self.TAUX_NOMINAL_I10 > 1:
            self.TAUX_NOMINAL_I10 /= 100
        
        # Normalisation du TEG
        if self.TEG_I17 and self.TEG_I17 > 1:
            self.TEG_I17 /= 100
        
        try:
            if self.MONTANT_DECOUVERT_I08 and self.MONTANT_DECOUVERT_I08 != 0:
                interets = self.MONTANT_DECOUVERT_I08 * self.TAUX_NOMINAL_I10
                frais_totaux = ((self.FRAIS_DOSSIERS_ET_COMM_I11 or 0) + 
                            (self.COUTS_ASSURANCE_I12 or 0) + 
                            (self.FRAIS_ANNEXES_I13 or 0))
                
                self.TEG_decouvert = round(((interets + frais_totaux) / 
                                        self.MONTANT_DECOUVERT_I08) * 100, 2)
            else:
                self.TEG_decouvert = 0.0
        except Exception:
            self.TEG_decouvert = 0.0
        
        super().save(*args, **kwargs)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Découvert"
        verbose_name_plural = "Découverts"
        ordering = ['-DATE_MISE_PLACE_I03']
    

class Affacturage(models.Model):
    """Modèle pour l'affacturage"""
    
    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE, related_name='affacturages')
    fichier_import = models.ForeignKey(FichierImport, on_delete=models.SET_NULL, null=True, blank=True, related_name='affacturages')
    
    SIGLE_I01 = models.CharField(max_length=30, verbose_name="Sigle")
    CODE_BANQUE_I02 = models.CharField(max_length=8, verbose_name="Code banque")
    DATE_MISE_PLACE_I03 = models.DateField(verbose_name="Date mise en place")
    DATE_ECHEANCE_I04 = models.DateField(verbose_name="Date échéance")
    DUREE_AFFACTURAGE_I05 = models.IntegerField(verbose_name="Durée (jours)")
    BENEFICAIRE_I06 = models.CharField(max_length=125, verbose_name="Bénéficiaire")
    CATEGORIE_BENEF_I07 = models.CharField(max_length=30, verbose_name="Catégorie")
    LIEU_RESIDENCE_I08 = models.CharField(max_length=50, verbose_name="Lieu résidence")
    SECT_ACT_I09 = models.CharField(max_length=75, verbose_name="Secteur activité")
    MONTANT_CREANCE_I10 = models.IntegerField(verbose_name="Montant de la créance cédée", default=0)
    MONTANT_COM_AFFACTURAGE_I11 = models.FloatField(verbose_name="Montant de commission d'affacturage", default=0.0)
    MONTANT_COMM_FINANCEMENT_I12 = models.IntegerField(verbose_name="Montant de commission de financement", default=0)
    MONTANT_FRAIS_ANNEXES_I13 = models.IntegerField(verbose_name="Frais annexes ou autres frais fixes", default=0)
    TEG_I14 = models.FloatField(
        verbose_name="TEG (%)",
        default=0.0,  
        blank=True,    
        null=True      
    )
    TEG_affacturage = models.FloatField(
        verbose_name="TEG affacturage (%)",
        default=0.0,  
        blank=True,    
        null=True      
    )
    
    def save(self, *args, **kwargs):
    # Normalisation du TEG
        if self.TEG_I14 and self.TEG_I14 > 1:
            self.TEG_I14 /= 100
        
        try:
            if self.MONTANT_CREANCE_I10 and self.MONTANT_CREANCE_I10 != 0:
                frais_totaux = (((self.MONTANT_COM_AFFACTURAGE_I11 or 0) + 
                            (self.MONTANT_COMM_FINANCEMENT_I12 or 0) + 
                            (self.MONTANT_FRAIS_ANNEXES_I13 or 0))/self.MONTANT_CREANCE_I10)
                
                self.TEG_affacturage = round((frais_totaux*360/self.DUREE_AFFACTURAGE_I05)*100, 2)
            else:
                self.TEG_affacturage = 0.0
        except Exception:
            self.TEG_affacturage = 0.0
        
        super().save(*args, **kwargs)
        
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Affacturage"
        verbose_name_plural = "Affacturages"
        ordering = ['-DATE_MISE_PLACE_I03']
    

class Cautions(models.Model):
    """Modèle pour les cautions"""
    
    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE, related_name='cautions')
    fichier_import = models.ForeignKey(FichierImport, on_delete=models.SET_NULL, null=True, blank=True, related_name='cautions')
    
    SIGLE_I01 = models.CharField(max_length=30, verbose_name="Sigle")
    CODE_BANQUE_I02 = models.CharField(max_length=8, verbose_name="Code banque")
    DATE_MISE_PLACE_I03 = models.DateField(verbose_name="Date mise en place")
    DATE_ECHEANCE_I04 = models.DateField(verbose_name="Date échéance")
    DUREE_CAUTION_I05 = models.IntegerField(verbose_name="Durée (jours)")
    BENEFICAIRE_I06 = models.CharField(max_length=125, verbose_name="Bénéficiaire")
    CATEGORIE_BENEF_I07 = models.CharField(max_length=30, verbose_name="Catégorie")
    LIEU_RESIDENCE_I08 = models.CharField(max_length=50, verbose_name="Lieu résidence")
    SECT_ACT_I09 = models.CharField(max_length=75, verbose_name="Secteur activité")
    MONTANT_CAUTION_I10 = models.IntegerField(verbose_name="Montant")
    TAUX_CAUTION_I11 = models.FloatField(verbose_name="Taux (%)", default=0.0)
    MONTANT_FRAIS_COMM_I12 = models.IntegerField(verbose_name="Frais/Comm", default=0)
    MONTANT_FRAIS_ANNEXES_I13 = models.IntegerField(verbose_name="Frais annexes", default=0)
    TEG_I14 = models.FloatField(
        verbose_name="TEG (%)",
        default=0.0,  
        blank=True,    
        null=True      
    )
    TEG_caution = models.FloatField(
        verbose_name="TEG caution (%)",
        default=0.0,  
        blank=True,    
        null=True      
    )

    
    def save(self, *args, **kwargs):
        # Normalisation du taux caution
        if self.TAUX_CAUTION_I11 and self.TAUX_CAUTION_I11 > 1:
            self.TAUX_CAUTION_I11 /= 100
        
        # Normalisation du TEG
        if self.TEG_I14 and self.TEG_I14 > 1:
            self.TEG_I14 /= 100
        
        try:
            if (self.MONTANT_CAUTION_I10 and self.MONTANT_CAUTION_I10 != 0 and
                self.DUREE_CAUTION_I05 and self.DUREE_CAUTION_I05 != 0):
                
                montant_net = (self.MONTANT_CAUTION_I10 - 
                            (self.MONTANT_FRAIS_COMM_I12 or 0) - 
                            (self.MONTANT_FRAIS_ANNEXES_I13 or 0))
                
                if montant_net != 0:
                    cout_annualise = ((self.MONTANT_CAUTION_I10 * 
                                    self.TAUX_CAUTION_I11 * 
                                    self.DUREE_CAUTION_I05) / 360)
                    
                    self.TEG_caution = round((cout_annualise / montant_net) * 
                                            (360 / self.DUREE_CAUTION_I05) * 100, 2)
                else:
                    self.TEG_caution = 0.0
            else:
                self.TEG_caution = 0.0
        except Exception:
            self.TEG_caution = 0.0
        
        super().save(*args, **kwargs)
        
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Caution"
        verbose_name_plural = "Cautions"
        ordering = ['-DATE_MISE_PLACE_I03']
    

class Effets_commerces(models.Model):
    """Modèle pour les effets de commerce"""
    
    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE, related_name='effets_commerces')
    fichier_import = models.ForeignKey(FichierImport, on_delete=models.SET_NULL, null=True, blank=True, related_name='effets')
    
    SIGLE_I01 = models.CharField(max_length=30, verbose_name="Sigle")
    CODE_BANQUE_I02 = models.CharField(max_length=8, verbose_name="Code banque")
    DATE_MISE_PLACE_I03 = models.DateField(verbose_name="Date mise en place")
    DATE_ECHEANCE_I04 = models.DateField(verbose_name="Date échéance")
    DUREE_EFFET_I05 = models.IntegerField(verbose_name="Durée (jours)")
    BENEFICAIRE_I06 = models.CharField(max_length=125, verbose_name="Bénéficiaire")
    CATEGORIE_BENEF_I07 = models.CharField(max_length=30, verbose_name="Catégorie")
    LIEU_RESIDENCE_I08 = models.CharField(max_length=50, verbose_name="Lieu résidence")
    SECT_ACT_I09 = models.CharField(max_length=75, verbose_name="Secteur activité")
    TAUX_NOMINAL_I10 = models.FloatField(verbose_name="Taux (%)", default=0.0)
    MONTANT_EFFET_I11 = models.IntegerField(verbose_name="Montant")
    MONTANT_FRAIS_DOSSIERS_I12 = models.IntegerField(verbose_name="FraiS de dossiers", default=0)
    MONTANT_COMMISSION_I13 = models.IntegerField(verbose_name="Commissions", default=0) 
    AUTRES_FRA_I14 = models.IntegerField(verbose_name="Frais annexes", default=0)
    TEG_I15 = models.FloatField(
        verbose_name="TEG (%)",
        default=0.0,  
        blank=True,    
        null=True      
    )
    TEG_effet = models.FloatField(verbose_name="Taux effectif global des effets de commerce (%)", default=0.0, null=True, blank=True)
    
    
    def save(self, *args, **kwargs):
    # Normalisation du taux nominal
        if self.TAUX_NOMINAL_I10 and self.TAUX_NOMINAL_I10 > 1:
            self.TAUX_NOMINAL_I10 /= 100
        
        # Normalisation du TEG
        if self.TEG_I15 and self.TEG_I15 > 1:
            self.TEG_I15 /= 100
        
        try:
            if (self.MONTANT_EFFET_I11 and self.MONTANT_EFFET_I11 != 0 and
                self.DUREE_EFFET_I05 and self.DUREE_EFFET_I05 != 0):
                
                montant_net = (self.MONTANT_EFFET_I11 - 
                            (self.MONTANT_COMMISSION_I13 or 0) - 
                            (self.AUTRES_FRA_I14 or 0))
                
                if montant_net != 0:
                    cout_interets = ((self.TAUX_NOMINAL_I10 * 
                                    self.MONTANT_EFFET_I11 * 
                                    self.DUREE_EFFET_I05) / 360)
                    
                    self.TEG_effet = round(((cout_interets / montant_net) * 
                                        (360 / self.DUREE_EFFET_I05)) * 100, 2)
                else:
                    self.TEG_effet = 0.0
            else:
                self.TEG_effet = 0.0
        except Exception:
            self.TEG_effet = 0.0
        
        super().save(*args, **kwargs)
        
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Effet de commerce"
        verbose_name_plural = "Effets de commerce"
        ordering = ['-DATE_MISE_PLACE_I03']
    

class Spot(models.Model):
    """Modèle pour des crédits spot"""
   
    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE, related_name='spots')
    fichier_import = models.ForeignKey(FichierImport, on_delete=models.SET_NULL, null=True, blank=True, related_name='spot_files')
    
    ETABLISSEMENT_I01 = models.CharField(max_length=30, verbose_name="Établissement")
    CODE_ETAB_I02 = models.CharField(max_length=8, verbose_name="Code établissement")
    DATE_MEP_I03 = models.DateField(verbose_name="Date de mise en place")
    CHA_ORI_I04 = models.CharField(max_length=50, verbose_name="Chargé d'origine", blank=True)
    NATURE_PRET_I05 = models.CharField(max_length=75, verbose_name="Nature du prêt")
    BENEFICIAIRE_I06 = models.CharField(max_length=125, verbose_name="Bénéficiaire")
    CATEGORIE_BENEF_I07 = models.CharField(max_length=30, verbose_name="Catégorie bénéficiaire")
    LIEU_RESIDENCE_I08 = models.CharField(max_length=75, verbose_name="Lieu de résidence")
    SECT_ACT_I09 = models.CharField(max_length=50, verbose_name="Secteur d'activité")
    MONTANT_CHAF_I10 = models.FloatField(verbose_name="Montant CA", null=True, blank=True)
    EFFECTIF_I11 = models.IntegerField(verbose_name="Effectif", null=True, blank=True)
    PROFESSION_I12 = models.CharField(max_length=60, verbose_name="Profession")
    MONTANT_PRET_I13 = models.FloatField(verbose_name="Montant du prêt")
    DUREE_I14 = models.IntegerField(verbose_name="Durée (mois)")
    DUREE_DIFFERRE_I15 = models.IntegerField(verbose_name="Durée différé (mois)", default=0)
    FREQ_REMB_I16 = models.CharField(max_length=20, verbose_name="Fréquence remboursement")
    TAUX_NOMINAL_I17 = models.FloatField(verbose_name="Taux nominal (%)")
    FRAIS_DOSSIER_I18 = models.FloatField(verbose_name="Frais de dossier", default=0)
    MODALITEPAIEMENT_ASS_I19 = models.CharField(max_length=100, verbose_name="Modalité de paiement", blank=True)
    MONTANTASSURANCE_I20 = models.FloatField(verbose_name="Montant assurance", default=0)
    FRAIS_ANNEXE_I21 = models.FloatField(verbose_name="Frais annexes", default=0)
    MODEREMBOURSEMENT_I22 = models.CharField(max_length=30, verbose_name="Mode remboursement")
    MONTANT_ECHEANCE_I23 = models.FloatField(verbose_name="Montant échéance")
    MODE_DEBLOCAGE_I24 = models.CharField(max_length=50, verbose_name="Mode déblocage")
    SITUATION_CREANCE_I25 = models.CharField(max_length=20, verbose_name="Situation créance")
    TEG_I26 = models.FloatField(verbose_name="TEG (%)", default=0.0, null=True, blank=True)
    TEG_spot = models.FloatField(verbose_name="Taux effectif global spot (%)", default=0.0, null=True, blank=True)
    
    
    def save(self, *args, **kwargs):
    # Normalisation du taux nominal
        if self.TAUX_NOMINAL_I17 and self.TAUX_NOMINAL_I17 > 1:
            self.TAUX_NOMINAL_I17 /= 100
        
        # Normalisation du TEG
        if self.TEG_I26 and self.TEG_I26 > 1:
            self.TEG_I26 /= 100
        
        try:
            if (self.MONTANT_PRET_I13 and self.MONTANT_PRET_I13 != 0 and 
                self.DUREE_I14 and self.DUREE_I14 != 0 and 
                self.MONTANT_ECHEANCE_I23 is not None):
                
                taux_periodique = ((self.MONTANT_ECHEANCE_I23 / 
                                self.MONTANT_PRET_I13 - 1) * 12) / self.DUREE_I14
                
                charges = ((self.FRAIS_DOSSIER_I18 or 0) + 
                        (self.MONTANTASSURANCE_I20 or 0) + 
                        (self.FRAIS_ANNEXE_I21 or 0))
                
                ratio_charges = charges / self.MONTANT_PRET_I13
                
                self.TEG_spot = round((taux_periodique + ratio_charges) * 100, 2)
            else:
                self.TEG_spot = 0.0
        except Exception:
            self.TEG_spot = 0.0
        
        super().save(*args, **kwargs)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Spot"
        verbose_name_plural = "Spots"
        ordering = ['-DATE_MEP_I03']

# ==========================================
# MODÈLE POUR LES TOKENS D'INSCRIPTION
# ==========================================

class TokenInscription(models.Model):
    """Modèle pour gérer les liens d'inscription temporaires avec expiration pour TOUS les rôles"""
    
    ROLE_CHOICES = [
        ('ACNEF', 'Administrateur CNEF'),
        ('UCNEF', 'Utilisateur CNEF'),
        ('AEF', 'Administrateur Établissement Financier'),
        ('UEF', 'Utilisateur Établissement Financier'),
    ]
    
    # Token unique
    token = models.CharField(max_length=100, unique=True, db_index=True)
    
    # Informations de l'établissement et de l'utilisateur
    etablissement = models.ForeignKey(
        'Etablissement', 
        on_delete=models.CASCADE,
        related_name='tokens_inscription',
        null=True,  # Nullable pour ACNEF et UCNEF
        blank=True
    )
    email_destinataire = models.EmailField(
        max_length=255,
        verbose_name="Email du destinataire",
        help_text="Email de la personne qui recevra le lien d'inscription"
    )
    nom_user = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="Nom de l'utilisateur",
        help_text="Optionnel : Nom prédéfini de l'utilisateur"
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name="Rôle")
    
    # Gestion de l'expiration
    date_creation = models.DateTimeField(auto_now_add=True)
    date_expiration = models.DateTimeField()
    
    # Traçabilité
    utilise = models.BooleanField(default=False)
    date_utilisation = models.DateTimeField(null=True, blank=True)
    utilisateur_cree = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='token_utilise'
    )
    cree_par = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tokens_crees'
    )
    
    class Meta:
        verbose_name = "Token d'inscription"
        verbose_name_plural = "Tokens d'inscription"
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['utilise']),
            models.Index(fields=['-date_creation']),
        ]
    
    def __str__(self):
        if self.etablissement:
            return f"Token {self.get_role_display()} pour {self.etablissement.Nom_etablissement}"
        return f"Token {self.get_role_display()} - {self.email_destinataire}"
    
    def save(self, *args, **kwargs):
        # Générer un token unique si ce n'est pas déjà fait
        if not self.token:
            self.token = self.generer_token_unique()
        
        # Définir la date d'expiration (48 heures par défaut)
        if not self.date_expiration:
            self.date_expiration = timezone.now() + timedelta(hours=42)
        
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validation pour s'assurer que l'établissement est correctement assigné selon le rôle"""
        super().clean()
        
        # AEF et UEF DOIVENT avoir un établissement
        if self.role in ['AEF', 'UEF'] and not self.etablissement:
            raise ValidationError({
                'etablissement': "Un établissement est obligatoire pour les tokens AEF et UEF"
            })
        
        # ACNEF et UCNEF NE DOIVENT PAS avoir d'établissement
        if self.role in ['ACNEF', 'UCNEF'] and self.etablissement:
            raise ValidationError({
                'etablissement': "Les tokens ACNEF et UCNEF ne doivent pas être associés à un établissement"
            })
    
    @staticmethod
    def generer_token_unique():
        """Génère un token unique et sécurisé de 64 caractères"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(64))
    
    def est_valide(self):
        """Vérifie si le token est toujours valide (non utilisé et non expiré)"""
        return (
            not self.utilise and
            timezone.now() < self.date_expiration
        )
    
    def est_expire(self):
        """Vérifie si le token a expiré"""
        return timezone.now() >= self.date_expiration
    
    def marquer_comme_utilise(self, utilisateur):
        """Marque le token comme utilisé après création du compte"""
        self.utilise = True
        self.date_utilisation = timezone.now()
        self.utilisateur_cree = utilisateur
        self.save()
    
    def generer_lien_inscription(self):
        """
        Génère le lien d'inscription complet selon le rôle
        Utilise SITE_URL défini dans settings.py
        """
        from django.conf import settings
        
        # Récupérer l'URL de base depuis settings
        base_url = f"{settings.SITE_URL}/inscription"
        
        # Générer le lien selon le rôle
        if self.role == 'ACNEF':
            return f"{base_url}/acnef/?token={self.token}"
        
        elif self.role == 'UCNEF':
            return f"{base_url}/ucnef/?token={self.token}"
        
        elif self.role == 'AEF':
            if self.etablissement:
                return f"{base_url}/aef/{self.etablissement.code_etablissement}/?token={self.token}"
            return f"{base_url}/aef/?token={self.token}"
        
        else:  # UEF
            if self.etablissement:
                if self.nom_user:
                    return f"{base_url}/uef/{self.etablissement.code_etablissement}/{self.nom_user}/?token={self.token}"
                return f"{base_url}/uef/{self.etablissement.code_etablissement}/?token={self.token}"
            return f"{base_url}/uef/?token={self.token}"
    
    def temps_restant(self):
        """Retourne le temps restant avant expiration"""
        if self.est_expire():
            return timedelta(0)
        return self.date_expiration - timezone.now()
    
    def temps_restant_minutes(self):
        """Retourne le temps restant en minutes"""
        temps = self.temps_restant()
        return int(temps.total_seconds() / 60)
    
    def peut_etre_utilise(self):
        """Vérifie si le token peut être utilisé (valide et non expiré)"""
        return self.est_valide()


# ==========================================
# MODÈLE POUR LA JOURNALISATION
# ==========================================

class ActionUtilisateur(models.Model):
    """Modèle pour enregistrer toutes les actions des utilisateurs (audit trail)"""
    
    TYPE_ACTION_CHOICES = [
        ('CONNEXION', 'Connexion'),
        ('DECONNEXION', 'Déconnexion'),
        ('UPLOAD_FICHIER', 'Upload de fichier'),
        ('VALIDATION_FICHIER', 'Validation de fichier'),
        ('REJET_FICHIER', 'Rejet de fichier'),
        ('TELECHARGEMENT_FICHIER_ORIGINAL', 'Téléchargement de fichier original'),
        ('CREATION_UTILISATEUR', 'Création d\'utilisateur'),
        ('MODIFICATION_UTILISATEUR', 'Modification d\'utilisateur'),
        ('SUPPRESSION_FICHIER', 'Suppression de fichier'),
        ('SUPPRESSION_ETABLISSEMENT', 'Suppression d\'établissement'),
        ('CREATION_ETABLISSEMENT', 'Création d\'établissement'),
        ('MODIFICATION_ETABLISSEMENT', 'Modification d\'établissement'),
        ('GENERER_COMMUNIQUE_PRESSE', 'Génération du communiqué de presse'),
        ('GENERATION_LIEN', 'Génération de lien d\'inscription'),
        ('UTILISATION_TOKEN', 'Utilisation d\'un token d\'inscription'),
        ('REINITIALISATION_MOT_DE_PASSE', 'Réinitialisation de mot de passe'),
        ('RENVOI_EMAIL', 'Renvoi email de validation'),
        ('AUTRE', 'Autre action'),
    ]
    
    # Informations de l'action
    utilisateur = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='actions_effectuees'
    )
    type_action = models.CharField(max_length=50, choices=TYPE_ACTION_CHOICES)
    description = models.TextField(verbose_name="Description de l'action")
    
    # Contexte
    etablissement = models.ForeignKey(
        'Etablissement',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actions_liees'
    )
    adresse_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    
    # Données supplémentaires (JSON)
    donnees_supplementaires = models.JSONField(null=True, blank=True)
    
    # Horodatage
    date_action = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        verbose_name = "Action utilisateur"
        verbose_name_plural = "Actions utilisateurs"
        ordering = ['-date_action']
        indexes = [
            models.Index(fields=['-date_action']),
            models.Index(fields=['type_action']),
            models.Index(fields=['utilisateur', '-date_action']),
        ]
    
    def __str__(self):
        if self.utilisateur:
            return f"{self.get_type_action_display()} par {self.utilisateur} le {self.date_action.strftime('%d/%m/%Y %H:%M')}"
        return f"{self.get_type_action_display()} le {self.date_action.strftime('%d/%m/%Y %H:%M')}"
    
    @classmethod
    def enregistrer_action(cls, utilisateur, type_action, description, etablissement=None, request=None, donnees_supplementaires=None):
        """Méthode utilitaire pour enregistrer une action facilement"""
        adresse_ip = None
        user_agent = None
        
        if request:
            # Récupérer l'IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                adresse_ip = x_forwarded_for.split(',')[0]
            else:
                adresse_ip = request.META.get('REMOTE_ADDR')
            
            # Récupérer le User-Agent
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
        
        return cls.objects.create(
            utilisateur=utilisateur,
            type_action=type_action,
            description=description,
            etablissement=etablissement,
            adresse_ip=adresse_ip,
            user_agent=user_agent,
            donnees_supplementaires=donnees_supplementaires
        )

# ==========================================
# MODÈLE HISTORIQUE EMAIL
# ==========================================

class HistoriqueEmail(models.Model):
    """Modèle pour enregistrer l'historique de tous les emails envoyés"""
    
    TYPE_EMAIL_CHOICES = [
        ('INVITATION', 'Invitation'),
        ('VALIDATION', 'Validation de fichier'),
        ('REJET', 'Rejet de fichier'),
        ('NOTIFICATION_ACNEF', 'Notification ACNEF'),
    ]
    
    STATUT_CHOICES = [
        ('ENVOYE', 'Envoyé avec succès'),
        ('ECHEC', 'Échec d\'envoi'),
    ]
    
    # Type et destinataire
    type_email = models.CharField(
        max_length=50, 
        choices=TYPE_EMAIL_CHOICES,
        verbose_name="Type d'email"
    )
    destinataire_email = models.EmailField(
        max_length=255,
        verbose_name="Email du destinataire"
    )
    destinataire_nom = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Nom du destinataire"
    )
    
    # Contenu de l'email
    objet = models.CharField(
        max_length=255,
        verbose_name="Objet de l'email"
    )
    contenu_html = models.TextField(
        verbose_name="Contenu HTML de l'email"
    )
    contenu_texte = models.TextField(
        blank=True,
        null=True,
        verbose_name="Contenu texte (fallback)"
    )
    
    # Statut d'envoi
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='ENVOYE',
        verbose_name="Statut d'envoi"
    )
    erreur_message = models.TextField(
        blank=True,
        null=True,
        verbose_name="Message d'erreur (si échec)"
    )
    
    # Contexte
    utilisateur_envoyeur = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='emails_envoyes',
        verbose_name="Envoyé par"
    )
    etablissement = models.ForeignKey(
        'Etablissement',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='emails_lies',
        verbose_name="Établissement concerné"
    )
    
    # Liens vers les objets concernés
    token_lie = models.ForeignKey(
        'TokenInscription',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='emails_envoyes',
        verbose_name="Token d'inscription lié"
    )
    fichier_lie = models.ForeignKey(
        'FichierImport',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='emails_envoyes',
        verbose_name="Fichier lié"
    )
    
    # Horodatage
    date_envoi = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'envoi"
    )
    
    class Meta:
        verbose_name = "Historique Email"
        verbose_name_plural = "Historique Emails"
        ordering = ['-date_envoi']
        indexes = [
            models.Index(fields=['-date_envoi']),
            models.Index(fields=['type_email']),
            models.Index(fields=['statut']),
            models.Index(fields=['destinataire_email']),
        ]
    
    def __str__(self):
        return f"{self.get_type_email_display()} → {self.destinataire_email} ({self.date_envoi.strftime('%d/%m/%Y %H:%M')})"
    
    def peut_renvoyer(self):
        """Vérifie si l'email peut être renvoyé"""
        # On peut toujours renvoyer un email
        return True
    