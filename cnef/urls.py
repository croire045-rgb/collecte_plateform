from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from cnef import views, views_aef
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf.urls.static import static

# ============================================================
# FONCTIONS DE TEST DES RÔLES
# ============================================================
def is_chef(user):
    return user.is_staff or user.is_superuser

def is_acnef(user):
    return user.is_authenticated and user.role == 'ACNEF'

def is_aef(user):
    return user.is_authenticated and user.role == 'AEF'


# ============================================================
# URLPATTERNS
# ============================================================
urlpatterns = [
    # ------------------------------------------------------------
    # AUTHENTIFICATION
    # ------------------------------------------------------------
    path('', views.ConnexionUniverselleView.as_view(), name='connexion'),
    path('connexion/', views.ConnexionUniverselleView.as_view(), name='connexion'),
    path('deconnexion/', views.DeconnexionView.as_view(), name='deconnexion'),

    # ------------------------------------------------------------
    # TABLEAU DE BORD UTILISATEUR
    # ------------------------------------------------------------
    path('tableau-de-bord/', views.TableauDeBordView.as_view(), name='tableau_de_bord'),
    path('upload-fichier/', views.upload_fichier_utilisateur, name='upload_fichier'),
    path('api/historique/', views.api_historique_etablissement, name='get_historique'),

    # ------------------------------------------------------------
    # INTERFACE CHEF
    # ------------------------------------------------------------
    path('chef/', views.interface_chef, name='interface_chef'),
    path('chef/detail/<int:fichier_id>/', views.detail_soumission, name='detail_soumission'),
    path('chef/valider/<int:fichier_id>/', views.valider_soumission, name='valider_soumission'),
    path('chef/rejeter/<int:fichier_id>/', views.rejeter_soumission, name='rejeter_soumission'),
    path('chef/stats/', views.get_stats_ajax, name='get_stats'),
    path('chef/bases-donnees/<str:model_type>/', views.visualiser_base_donnees, name='visualiser_base_donnees'),
    path('chef/api/fichiers/', login_required((views.FichiersListAPIView.as_view())), name='get_fichiers'),
    path('chef/api/etablissements/', login_required(user_passes_test(is_chef)(views.EtablissementsListAPIView.as_view())), name='get_etablissements'),
    path('chef/supprimer-fichier/<int:fichier_id>/', login_required(user_passes_test(is_chef)(views.FichierDeleteAPIView.as_view())), name='supprimer_fichier'),
    path('chef/supprimer-etablissement/<int:etablissement_id>/', login_required(user_passes_test(is_chef)(views.EtablissementDeleteAPIView.as_view())), name='supprimer_etablissement'),
    path('chef/soumission/<int:fichier_id>/teg/', views.visualisation_teg, name='visualisation_teg'),
    path('chef/api/supprimer-fichier/<int:fichier_id>/', login_required(user_passes_test(is_chef)(views.supprimer_fichier_api)), name='supprimer_fichier_api'),
    path('chef/api/supprimer-etablissement/<int:etablissement_id>/', login_required(user_passes_test(is_chef)(views.supprimer_etablissement_api)), name='supprimer_etablissement_api'),
    path('chef/telecharger-fichier/<int:fichier_id>/', login_required(user_passes_test(is_chef)(views.telecharger_fichier_original)), name='telecharger_fichier'),
    path('chef/communique-presse/', login_required((views.generer_communique_presse)), name='communique_presse'),

    path('chef/historique-emails/', login_required(user_passes_test(is_chef)(views.historique_emails)), name='historique_emails'),
    path('chef/api/renvoyer-email/<int:email_id>/', login_required(user_passes_test(is_chef)(views.renvoyer_email_api)), name='renvoyer_email'),

    # ------------------------------------------------------------
    # API GESTION DES ÉTABLISSEMENTS CNEF (NOUVEAU)
    # ------------------------------------------------------------
    path('chef/api/etablissements/creer/', login_required(user_passes_test(is_acnef)(views.creer_etablissement)), name='creer_etablissement'),
    path('chef/api/etablissements/liste/', login_required(user_passes_test(is_acnef)(views.lister_etablissements)), name='lister_etablissements'),
    path('chef/api/etablissements/<int:etablissement_id>/details/', login_required(user_passes_test(is_acnef)(views.details_etablissement)), name='details_etablissement'),
    path('chef/api/etablissements/<int:etablissement_id>/modifier/', login_required(user_passes_test(is_acnef)(views.modifier_etablissement)), name='modifier_etablissement'),
    path('chef/api/etablissements/<int:etablissement_id>/supprimer/', login_required(user_passes_test(is_acnef)(views.supprimer_etablissement)), name='supprimer_etablissement'),
    path('chef/api/etablissements/<int:etablissement_id>/toggle-status/', login_required(user_passes_test(is_acnef)(views.toggle_etablissement_status)), name='toggle_etablissement_status'),
    path('chef/api/etablissements/select/', views.charger_etablissements_select, name='charger_etablissements_select'),
    
    # ------------------------------------------------------------
    # PAGES SUPPLÉMENTAIRES
    # ------------------------------------------------------------
    path('details-supplementaires/', views.details_supplementaires, name='details_supplementaires'),

    # ------------------------------------------------------------
    # API GESTION DES UTILISATEURS (ACNEF)
    # ------------------------------------------------------------
    path('chef/api/utilisateurs/', login_required(user_passes_test(is_chef)(views.api_utilisateurs)), name='api_utilisateurs'),
    path('chef/api/utilisateurs/<int:utilisateur_id>/', login_required(user_passes_test(is_chef)(views.api_utilisateur_detail)), name='api_utilisateur_detail'),
    path('chef/api/generer-lien-inscription/', login_required(user_passes_test(is_chef)(views.generer_lien_inscription)), name='generer_lien_inscription'),
    path('chef/api/journalisation/', login_required(user_passes_test(is_chef)(views.api_journalisation)), name='api_journalisation'),
    path('chef/api/journalisation/export-csv/', login_required(user_passes_test(is_chef)(views.exporter_journalisation_csv)), name='exporter_journalisation_csv'),
    path('chef/api/invitations/generer/', login_required(user_passes_test(is_acnef)(views.generer_invitation_acnef)), name='generer_invitation_acnef'),

    path('chef/api/invitations-attente/', views.lister_invitations_en_attente, name='chef_api_invitations_attente'),
    path('chef/api/invitations/revoquer/<int:invitation_id>/', views.revoquer_invitation, name='chef_api_revoquer_invitation'),

    path('chef/api/invitations/liste/', login_required(user_passes_test(is_chef)(views.lister_invitations_en_attente)), name='chef_lister_invitations'),
    path('chef/api/invitations/<int:token_id>/revoquer/', login_required(user_passes_test(is_chef)(views.revoquer_invitation)), name='chef_revoquer_invitation'),
    path('chef/api/utilisateurs/<int:user_id>/bannir/', login_required(user_passes_test(is_chef)(views.bannir_utilisateur)), name='bannir_utilisateur'),
    path('chef/api/journalisation/compter/', views.api_compter_journalisation, name='api_compter_journalisation'),
    path('chef/api/journalisation/supprimer/', views.api_supprimer_journalisation, name='api_supprimer_journalisation'),
    
    # ==========================================
    # URLS CORRESPONDANTES
    # ==========================================
    path('inscription/acnef/', views.inscription_acnef_get, name='inscription_acnef'),
    path('inscription/ucnef/', views.inscription_ucnef_get, name='inscription_ucnef'),
    path('inscription/aef/<str:code_etablissement>/', views.inscription_aef_get, name='inscription_aef'),
    path('inscription/uef/<str:code_etablissement>/', views.inscription_uef_get, name='inscription_uef'),
    path('inscription/uef/<str:code_etablissement>/<str:nom_user>/', views.inscription_uef_get, name='inscription_uef_named'),

    # ============================================================
    # INTERFACE AEF (Administrateur Établissement Financier)
    # ============================================================
    path('aef/', login_required(user_passes_test(is_aef)(views.interface_aef)), name='interface_aef'),
    path('aef/api/dashboard/', views.aef_api_dashboard, name='aef_api_dashboard'),
    path('aef/api/historique/', views.aef_api_historique, name='aef_api_historique'),
    path('aef/upload-fichier/', views.aef_upload_fichier, name='aef_upload_fichier'),
    path('aef/api/utilisateurs-uef/', views.aef_api_utilisateurs_uef, name='aef_api_utilisateurs_uef'),
    path('aef/api/invitations-attente/', views.aef_api_invitations_attente, name='aef_api_invitations_attente'),
    path('aef/api/generer-invitation-uef/', views.aef_api_generer_invitation_uef, name='aef_api_generer_invitation_uef'),
    path('aef/api/revoquer-invitation/<int:invitation_id>/', views.aef_api_revoquer_invitation, name='aef_api_revoquer_invitation'),
    path('aef/api/modifier-profil/', views.aef_api_modifier_profil, name='aef_api_modifier_profil'),
    path('aef/soumission/<int:fichier_id>/', views.aef_detail_soumission, name='aef_detail_soumission'),
    path('aef/soumission/<int:fichier_id>/teg/', login_required(user_passes_test(is_aef)(views.visualisation_teg_aef)), name='visualisation_teg_aef'),
    path('aef/soumission/<int:fichier_id>/telecharger-rapport-teg/', login_required(user_passes_test(is_aef)(views.telecharger_rapport_teg_aef)), name='telecharger_rapport_teg_aef'),
    path('aef/api/journalisation/', views.aef_api_journalisation, name='aef_api_journalisation'),
    path('aef/api/journalisation/export-csv/', views.aef_exporter_journalisation_csv, name='aef_exporter_journalisation_csv'),
    
    # Gestion des utilisateurs UEF
    path('aef/api/utilisateur-uef/<int:user_id>/activer/', views_aef.aef_activer_utilisateur_uef, name='aef_activer_utilisateur_uef'),
    path('aef/api/utilisateur-uef/<int:user_id>/desactiver/', views_aef.aef_desactiver_utilisateur_uef, name='aef_desactiver_utilisateur_uef'),
    
    # Gestion des soumissions
    path('aef/api/soumission/<int:fichier_id>/supprimer/', views_aef.aef_supprimer_soumission, name='aef_supprimer_soumission'),
    
    # ------------------------------------------------------------
    # RÉINITIALISATION DU MOT DE PASSE
    # ------------------------------------------------------------
    path('saisie-mail/', views.saisie_mail_view, name='saisie_mail'),
    path('code-validation/', views.code_validation_view, name='code_validation'),
    path('code-validation-ajax/', views.code_validation_ajax, name='code_validation_ajax'),
    path('confirmation/', views.confirmation_view, name='confirmation'),
    
    re_path(r'^.*$', views.custom_404_view, name='custom_404'),
]

# ============================================================
# GESTION DES FICHIERS STATIQUES (DÉVELOPPEMENT)
# ============================================================
if settings.DEBUG:
    # Servir les fichiers statiques (CSS, JS, images)
    if hasattr(settings, 'STATICFILES_DIRS') and settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    else:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Servir les fichiers média (uploads)
    if hasattr(settings, 'MEDIA_URL') and hasattr(settings, 'MEDIA_ROOT'):
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ============================================================
# CATCH-ALL 404 (DOIT ÊTRE ABSOLUMENT EN DERNIER !)
# ============================================================
urlpatterns += [
    
]