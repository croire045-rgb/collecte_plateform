from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from .models import (
    Etablissement, User, FichierImport, Credit_Amortissables, 
    Decouverts, Affacturage, Cautions, Effets_commerces, Spot,
    TokenInscription, ActionUtilisateur
)


# ==========================================
# ADMIN PERSONNALISÉS
# ==========================================

class EtablissementAdmin(admin.ModelAdmin):
    """Admin pour le modèle Etablissement"""
    
    list_display = [
        'Nom_etablissement', 'code_etablissement', 'type_etablissement', 
        'categorie_emf', 'is_active', 'date_creation', 'nombre_utilisateurs'
    ]
    
    list_filter = [
        'type_etablissement', 'categorie_emf', 'is_active', 'date_creation'
    ]
    
    search_fields = [
        'Nom_etablissement', 'code_etablissement'
    ]
    
    readonly_fields = ['date_creation', 'date_modification']
    
    fieldsets = (
        ('Informations Générales', {
            'fields': (
                'Nom_etablissement', 'code_etablissement', 'type_etablissement',
                'categorie_emf', 'is_active'
            )
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    def nombre_utilisateurs(self, obj):
        return obj.utilisateurs.count()
    nombre_utilisateurs.short_description = "Nb utilisateurs"


class UserAdmin(BaseUserAdmin):
    """Admin personnalisé pour le modèle User"""
    
    list_display = [
        'email', 'nom', 'prenom', 'role', 'etablissement_link', 
        'is_active', 'date_joined', 'derniere_connexion'
    ]
    
    list_filter = [
        'role', 'is_active', 'is_staff', 'etablissement', 'date_joined'
    ]
    
    search_fields = [
        'email', 'nom', 'prenom', 'etablissement__Nom_etablissement'
    ]
    
    readonly_fields = [
        'date_joined', 'date_modification', 'derniere_connexion', 'last_login'
    ]
    
    fieldsets = (
        ('Informations Personnelles', {
            'fields': ('email', 'nom', 'prenom', 'telephone')
        }),
        ('Rôle et Établissement', {
            'fields': ('role', 'etablissement', 'cree_par')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
        ('Dates Importantes', {
            'fields': (
                'date_joined', 'date_modification', 
                'last_login', 'derniere_connexion'
            ),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'nom', 'prenom', 'role', 'etablissement',
                'password1', 'password2', 'is_active', 'is_staff'
            ),
        }),
    )
    
    ordering = ['-date_joined']
    
    def etablissement_link(self, obj):
        if obj.etablissement:
            url = reverse('admin:models_etablissement_change', args=[obj.etablissement.id])
            return format_html('<a href="{}">{}</a>', url, obj.etablissement.Nom_etablissement)
        return "Aucun"
    etablissement_link.short_description = "Établissement"

class FichierImportAdmin(admin.ModelAdmin):
    """Admin pour le modèle FichierImport"""
    
    list_display = [
        'nom_fichier', 
        'etablissement_cnef_link',
        'uploader_par_link',
        'date_import', 
        'statut', 
        'total_lignes_importees', 
        'valide_par_link', 
        'date_validation'
    ]
    
    list_filter = [
        'statut', 
        'date_import', 
        'etablissement_cnef',
        'valide_par'
    ]
    
    search_fields = [
        'nom_fichier', 
        'etablissement_cnef__Nom_etablissement',
        'uploader_par__email', 
        'valide_par__email'
    ]
    
    readonly_fields = [
        'date_import', 'nb_credits_importes', 'nb_decouverts_importes',
        'nb_affacturages_importes', 'nb_cautions_importes', 
        'nb_effets_importes', 'nb_spots_importes', 'total_lignes_importees'
    ]
    
    fieldsets = (
        ('Informations Fichier', {
            'fields': (
                'nom_fichier', 'fichier', 'etablissement_cnef', 'uploader_par'
            )
        }),
        ('Statut et Validation', {
            'fields': (
                'statut', 'valide_par', 'date_validation', 
                'commentaire_validation'
            )
        }),
        ('Statistiques Import', {
            'fields': (
                'nb_credits_importes', 'nb_decouverts_importes',
                'nb_affacturages_importes', 'nb_cautions_importes',
                'nb_effets_importes', 'nb_spots_importes',
                'total_lignes_importees'
            ),
            'classes': ('collapse',)
        }),
        ('Détails Techniques', {
            'fields': ('erreurs', 'details'),
            'classes': ('collapse',)
        }),
    )
    
    def etablissement_cnef_link(self, obj):
        if obj.etablissement_cnef:
            url = reverse('admin:cnef_etablissement_change', args=[obj.etablissement_cnef.id])
            return format_html('<a href="{}">{}</a>', url, obj.etablissement_cnef.Nom_etablissement)
        return "Aucun"
    etablissement_cnef_link.short_description = "Établissement"
    
    def uploader_par_link(self, obj):
        if obj.uploader_par:
            url = reverse('admin:cnef_user_change', args=[obj.uploader_par.id])
            return format_html('<a href="{}">{}</a>', url, obj.uploader_par.get_full_name())
        return "Aucun"
    uploader_par_link.short_description = "Uploadé par"
    
    def valide_par_link(self, obj):
        if obj.valide_par:
            url = reverse('admin:cnef_user_change', args=[obj.valide_par.id])
            return format_html('<a href="{}">{}</a>', url, obj.valide_par.get_full_name())
        return "Non validé"
    valide_par_link.short_description = "Validé par"
    
    def total_lignes_importees(self, obj):
        return obj.total_lignes_importees
    total_lignes_importees.short_description = "Total lignes"
    
    # Actions personnalisées
    actions = ['marquer_comme_valide', 'marquer_comme_rejete']
    
    def marquer_comme_valide(self, request, queryset):
        updated = queryset.update(statut='REUSSI', valide_par=request.user, date_validation=timezone.now())
        self.message_user(request, f"{updated} fichier(s) marqué(s) comme validé(s).")
    marquer_comme_valide.short_description = "Marquer comme validé"
    
    def marquer_comme_rejete(self, request, queryset):
        updated = queryset.update(statut='REJETE')
        self.message_user(request, f"{updated} fichier(s) marqué(s) comme rejeté(s).")
    marquer_comme_rejete.short_description = "Marquer comme rejeté"
    
    
@admin.register(Credit_Amortissables)
class CreditAmortissablesAdmin(admin.ModelAdmin):
    list_display = [
        'ETABLISSEMENT_I01',
        'CODE_ETAB_I02',
        'DATE_MEP_I03',
        'CHA_ORI_I04',
        'NATURE_PRET_I05',
        'BENEFICIAIRE_I06',
        'CATEGORIE_BENEF_I07',
        'LIEU_RESIDENCE_I08',
        'SECT_ACT_I09',
        'MONTANT_CHAF_I10',
        'EFFECTIF_I11',
        'PROFESSION_I12',
        'MONTANT_PRET_I13',
        'DUREE_I14',
        'MATURITE',
        'DUREE_DIFFERRE_I15',
        'FREQ_REMB_I16',
        'TAUX_NOMINAL_I17',
        'FRAIS_DOSSIER_I18',
        'MODALITEPAIEMENT_ASS_I19',
        'MONTANTASSURANCE_I20',
        'FRAIS_ANNEXE_I21',
        'MODEREMBOURSEMENT_I22',
        'MONTANT_ECHEANCE_I23',
        'MODE_DEBLOCAGE_I24',
        'SITUATION_CREANCE_I25',
        'TEG_I26',
        'fichier_import'
    ]
    list_filter = [
        'etablissement',
        'DATE_MEP_I03',
        'NATURE_PRET_I05',
        'SITUATION_CREANCE_I25',
        'MATURITE',
    ]
    search_fields = [
        'BENEFICIAIRE_I06',
        'CODE_ETAB_I02',
        'PROFESSION_I12'
    ]
    date_hierarchy = 'DATE_MEP_I03'
    
    actions = ['supprimer_credits']
    
    fieldsets = (
        ('Identification', {
            'fields': (
                'etablissement',
                'fichier_import',
                'ETABLISSEMENT_I01',
                'CODE_ETAB_I02'
            )
        }),
        ('Bénéficiaire', {
            'fields': (
                'BENEFICIAIRE_I06',
                'CATEGORIE_BENEF_I07',
                'LIEU_RESIDENCE_I08',
                'PROFESSION_I12',
                'SECT_ACT_I09'
            )
        }),
        ('Caractéristiques du crédit', {
            'fields': (
                'DATE_MEP_I03',
                'NATURE_PRET_I05',
                'MONTANT_PRET_I13',
                'DUREE_I14',
                'MATURITE', 
                'DUREE_DIFFERRE_I15',
                'TAUX_NOMINAL_I17',
                'TEG_I26'
            )
        }),
        ('Modalités de remboursement', {
            'fields': (
                'FREQ_REMB_I16',
                'MODEREMBOURSEMENT_I22',
                'MONTANT_ECHEANCE_I23',
                'MODE_DEBLOCAGE_I24'
            )
        }),
        ('Frais', {
            'fields': (
                'FRAIS_DOSSIER_I18',
                'MONTANTASSURANCE_I20',
                'FRAIS_ANNEXE_I21'
            )
        }),
        ('Autres', {
            'fields': (
                'SITUATION_CREANCE_I25',
                'CHA_ORI_I04'
            )
        })
    )
    
    
    readonly_fields = ['MATURITE']
    
    def supprimer_credits(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(
            request,
            f"{count} crédit(s) amortissable(s) supprimé(s) avec succès",
            messages.SUCCESS
        )
    supprimer_credits.short_description = " Supprimer les crédits sélectionnés"

@admin.register(Decouverts)
class DecouvertsAdmin(admin.ModelAdmin):
    list_display = [
        'etablissement',
        'SIGLE_I01',
        'CODE_BANQUE_I02',
        'DATE_MISE_PLACE_I03',
        'BENEFICAIRE_I04',
        'CATEGORIE_BENEF_I05',
        'LIEU_RESIDENCE_I06',
        'SECT_ACT_I07',
        'MONTANT_DECOUVERT_I08',
        'CUMUL_TIRAGES_DEC_I09',
        'TAUX_NOMINAL_I10',
        'FRAIS_DOSSIERS_ET_COMM_I11',
        'COUTS_ASSURANCE_I12',
        'FRAIS_ANNEXES_I13',
        'AGIOS_I14',
        'NOMBRE_DEBITEURS_I15',
        'SITUATION_CREANCE_I16',
        'TEG_I17',
    ]
    list_filter = ['etablissement', 'DATE_MISE_PLACE_I03', 'SITUATION_CREANCE_I16']
    search_fields = ['BENEFICAIRE_I06', 'CODE_BANQUE_I02']
    date_hierarchy = 'DATE_MISE_PLACE_I03'
    
    actions = ['supprimer_decouverts']
    
    def supprimer_decouverts(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(
            request,
            f"{count} découvert(s) supprimé(s) avec succès",
            messages.SUCCESS
        )
    supprimer_decouverts.short_description = "🗑️ Supprimer les découverts sélectionnés"

@admin.register(Affacturage)
class AffacturageAdmin(admin.ModelAdmin):
    list_display = [
        'etablissement',
        'SIGLE_I01',
        'CODE_BANQUE_I02',
        'DATE_MISE_PLACE_I03',
        'DATE_ECHEANCE_I04',
        'DUREE_AFFACTURAGE_I05',
        'BENEFICAIRE_I06',
        'CATEGORIE_BENEF_I07',
        'LIEU_RESIDENCE_I08',
        'SECT_ACT_I09',
        'MONTANT_CREANCE_I10',
        'MONTANT_COM_AFFACTURAGE_I11',
        'MONTANT_COMM_FINANCEMENT_I12',
        'MONTANT_FRAIS_ANNEXES_I13',
        'TEG_I14',
    ]
    list_filter = ['etablissement', 'DATE_MISE_PLACE_I03']
    search_fields = ['BENEFICAIRE_I06', 'CODE_BANQUE_I02']
    date_hierarchy = 'DATE_MISE_PLACE_I03'
    
    actions = ['supprimer_affacturages']
    
    def supprimer_affacturages(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(
            request,
            f"{count} affacturage(s) supprimé(s) avec succès",
            messages.SUCCESS
        )
    supprimer_affacturages.short_description = "🗑️ Supprimer les affacturages sélectionnés"

@admin.register(Cautions)
class CautionsAdmin(admin.ModelAdmin):
    list_display = [
        'etablissement',
        'SIGLE_I01',
        'CODE_BANQUE_I02',
        'DATE_MISE_PLACE_I03',
        'DATE_ECHEANCE_I04',
        'DUREE_CAUTION_I05',
        'BENEFICAIRE_I06',
        'CATEGORIE_BENEF_I07',
        'LIEU_RESIDENCE_I08',
        'SECT_ACT_I09',
        'MONTANT_CAUTION_I10',
        'TAUX_CAUTION_I11',
        'MONTANT_FRAIS_COMM_I12',
        'MONTANT_FRAIS_ANNEXES_I13',
        'TEG_I14',
    ]
    list_filter = ['etablissement', 'DATE_MISE_PLACE_I03']
    search_fields = ['BENEFICAIRE_I06', 'CODE_BANQUE_I02']
    date_hierarchy = 'DATE_MISE_PLACE_I03'
    
    actions = ['supprimer_cautions']
    
    def supprimer_cautions(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(
            request,
            f"{count} caution(s) supprimé(s) avec succès",
            messages.SUCCESS
        )
    supprimer_cautions.short_description = "🗑️ Supprimer les cautions sélectionnés"

class SpotAdmin(admin.ModelAdmin):
    list_display = [
        'ETABLISSEMENT_I01',
        'CODE_ETAB_I02',
        'DATE_MEP_I03',
        'CHA_ORI_I04',
        'NATURE_PRET_I05',
        'BENEFICIAIRE_I06',
        'CATEGORIE_BENEF_I07',
        'LIEU_RESIDENCE_I08',
        'SECT_ACT_I09',
        'MONTANT_CHAF_I10',
        'EFFECTIF_I11',
        'PROFESSION_I12',
        'MONTANT_PRET_I13',
        'DUREE_I14',
        'DUREE_DIFFERRE_I15',
        'FREQ_REMB_I16',
        'TAUX_NOMINAL_I17',
        'FRAIS_DOSSIER_I18',
        'MODALITEPAIEMENT_ASS_I19',
        'MONTANTASSURANCE_I20',
        'FRAIS_ANNEXE_I21',
        'MODEREMBOURSEMENT_I22',
        'MONTANT_ECHEANCE_I23',
        'MODE_DEBLOCAGE_I24',
        'SITUATION_CREANCE_I25',
        'TEG_I26',
        'fichier_import'
    ]
    list_filter = [
        'etablissement',
        'DATE_MEP_I03',
        'NATURE_PRET_I05',
        'SITUATION_CREANCE_I25'
    ]
    search_fields = [
        'BENEFICIAIRE_I06',
        'CODE_ETAB_I02',
        'PROFESSION_I12'
    ]
    date_hierarchy = 'DATE_MEP_I03'
    
    actions = ['spots']
    
    fieldsets = (
        ('Identification', {
            'fields': (
                'etablissement',
                'fichier_import',
                'ETABLISSEMENT_I01',
                'CODE_ETAB_I02'
            )
        }),
        ('Bénéficiaire', {
            'fields': (
                'BENEFICIAIRE_I06',
                'CATEGORIE_BENEF_I07',
                'LIEU_RESIDENCE_I08',
                'PROFESSION_I12',
                'SECT_ACT_I09'
            )
        }),
        ('Caractéristiques du crédit', {
            'fields': (
                'DATE_MEP_I03',
                'NATURE_PRET_I05',
                'MONTANT_PRET_I13',
                'DUREE_I14',
                'DUREE_DIFFERRE_I15',
                'TAUX_NOMINAL_I17',
                'TEG_I26'
            )
        }),
        ('Modalités de remboursement', {
            'fields': (
                'FREQ_REMB_I16',
                'MODEREMBOURSEMENT_I22',
                'MONTANT_ECHEANCE_I23',
                'MODE_DEBLOCAGE_I24'
            )
        }),
        ('Frais', {
            'fields': (
                'FRAIS_DOSSIER_I18',
                'MONTANTASSURANCE_I20',
                'FRAIS_ANNEXE_I21'
            )
        }),
        ('Autres', {
            'fields': (
                'SITUATION_CREANCE_I25',
                'CHA_ORI_I04'
            )
        })
    )
    
    def spots(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(
            request,
            f"{count} Spot supprimé avec succès",
            messages.SUCCESS
        )
    spots.short_description = "🗑️ Supprimer les spots"


@admin.register(Effets_commerces)
class EffetsCommercesAdmin(admin.ModelAdmin):
    list_display = [
        'etablissement',
        'SIGLE_I01',
        'CODE_BANQUE_I02',
        'DATE_MISE_PLACE_I03',
        'DATE_ECHEANCE_I04',
        'DUREE_EFFET_I05',
        'BENEFICAIRE_I06',
        'CATEGORIE_BENEF_I07',
        'LIEU_RESIDENCE_I08',
        'SECT_ACT_I09',
        'TAUX_NOMINAL_I10',
        'MONTANT_EFFET_I11',
        'MONTANT_FRAIS_DOSSIERS_I12',
        'MONTANT_COMMISSION_I13',
        'AUTRES_FRA_I14',
        'TEG_I15',
    ]
    list_filter = ['etablissement', 'DATE_MISE_PLACE_I03']
    search_fields = ['BENEFICAIRE_I06', 'CODE_BANQUE_I02']
    date_hierarchy = 'DATE_MISE_PLACE_I03'
    
    actions = ['supprimer_effets']
    
    def supprimer_effets(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(
            request,
            f"{count} effet(s) de commerce supprimé(s) avec succès",
            messages.SUCCESS
        )
    supprimer_effets.short_description = "🗑️ Supprimer les effets sélectionnés"