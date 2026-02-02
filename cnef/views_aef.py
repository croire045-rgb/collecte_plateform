# ==========================================
# VUES SPÉCIFIQUES POUR L'INTERFACE AEF
# ==========================================
"""
Ce fichier contient les vues spécifiques pour l'interface AEF
qui ne sont pas encore dans le fichier views.py principal
"""

import logging
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.utils import timezone

# Import des modèles
from .models import User, FichierImport, ActionUtilisateur

logger = logging.getLogger(__name__)

# ==========================================
# TESTS DE PERMISSIONS
# ==========================================

def is_aef(user):
    """Vérifie si l'utilisateur est AEF"""
    return user.is_authenticated and hasattr(user, 'role') and user.role == 'AEF'


# ==========================================
# GESTION DES UTILISATEURS UEF
# ==========================================

@login_required
@user_passes_test(is_aef)
@require_http_methods(["POST"])
def aef_activer_utilisateur_uef(request, user_id):
    """
    API pour activer un utilisateur UEF
    """
    try:
        # Récupérer l'utilisateur UEF
        utilisateur_uef = get_object_or_404(
            User,
            id=user_id,
            role='UEF',
            etablissement=request.user.etablissement
        )
        
        # Vérifier que l'utilisateur n'est pas déjà actif
        if utilisateur_uef.is_active:
            return JsonResponse({
                'success': False,
                'message': 'Cet utilisateur est déjà actif.'
            }, status=400)
        
        # Activer l'utilisateur
        utilisateur_uef.is_active = True
        utilisateur_uef.save()
        
        # Enregistrer l'action dans le journal
        ActionUtilisateur.enregistrer_action(
            utilisateur=request.user,
            type_action='MODIFICATION_UTILISATEUR',
            description=f"Activation de l'utilisateur UEF : {utilisateur_uef.get_full_name()} ({utilisateur_uef.email})",
            etablissement=request.user.etablissement,
            request=request
        )
        
        logger.info(f"AEF {request.user.email} a activé l'utilisateur {utilisateur_uef.email}")
        
        return JsonResponse({
            'success': True,
            'message': f'Utilisateur {utilisateur_uef.get_full_name()} activé avec succès.',
            'utilisateur': {
                'id': utilisateur_uef.id,
                'nom': utilisateur_uef.nom,
                'prenom': utilisateur_uef.prenom,
                'email': utilisateur_uef.email,
                'is_active': utilisateur_uef.is_active
            }
        })
        
    except User.DoesNotExist:
        logger.warning(f"Tentative d'activation d'un utilisateur inexistant (ID: {user_id})")
        return JsonResponse({
            'success': False,
            'message': 'Utilisateur non trouvé ou vous n\'avez pas les permissions nécessaires.'
        }, status=404)
        
    except Exception as e:
        logger.error(f"Erreur lors de l'activation de l'utilisateur {user_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Une erreur est survenue lors de l\'activation de l\'utilisateur.'
        }, status=500)


@login_required
@user_passes_test(is_aef)
@require_http_methods(["POST"])
def aef_desactiver_utilisateur_uef(request, user_id):
    """
    API pour désactiver un utilisateur UEF
    """
    try:
        # Récupérer l'utilisateur UEF
        utilisateur_uef = get_object_or_404(
            User,
            id=user_id,
            role='UEF',
            etablissement=request.user.etablissement
        )
        
        # Vérifier que l'utilisateur n'est pas déjà inactif
        if not utilisateur_uef.is_active:
            return JsonResponse({
                'success': False,
                'message': 'Cet utilisateur est déjà désactivé.'
            }, status=400)
        
        # Désactiver l'utilisateur
        utilisateur_uef.is_active = False
        utilisateur_uef.save()
        
        # Enregistrer l'action dans le journal
        ActionUtilisateur.enregistrer_action(
            utilisateur=request.user,
            type_action='MODIFICATION_UTILISATEUR',
            description=f"Désactivation de l'utilisateur UEF : {utilisateur_uef.get_full_name()} ({utilisateur_uef.email})",
            etablissement=request.user.etablissement,
            request=request
        )
        
        logger.info(f"AEF {request.user.email} a désactivé l'utilisateur {utilisateur_uef.email}")
        
        return JsonResponse({
            'success': True,
            'message': f'Utilisateur {utilisateur_uef.get_full_name()} désactivé avec succès.',
            'utilisateur': {
                'id': utilisateur_uef.id,
                'nom': utilisateur_uef.nom,
                'prenom': utilisateur_uef.prenom,
                'email': utilisateur_uef.email,
                'is_active': utilisateur_uef.is_active
            }
        })
        
    except User.DoesNotExist:
        logger.warning(f"Tentative de désactivation d'un utilisateur inexistant (ID: {user_id})")
        return JsonResponse({
            'success': False,
            'message': 'Utilisateur non trouvé ou vous n\'avez pas les permissions nécessaires.'
        }, status=404)
        
    except Exception as e:
        logger.error(f"Erreur lors de la désactivation de l'utilisateur {user_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Une erreur est survenue lors de la désactivation de l\'utilisateur.'
        }, status=500)


# ==========================================
# GESTION DES SOUMISSIONS
# ==========================================

@login_required
@user_passes_test(is_aef)
@require_http_methods(["POST"])
def aef_supprimer_soumission(request, fichier_id):
    """
    API pour supprimer une soumission (seulement si elle est EN_COURS)
    """
    try:
        # Récupérer le fichier
        fichier = get_object_or_404(
            FichierImport,
            id=fichier_id,
            etablissement_cnef=request.user.etablissement
        )
        
        # Vérifier que le fichier est bien EN_COURS (pas encore validé/rejeté)
        if fichier.statut != 'EN_COURS':
            statut_display = dict(FichierImport.STATUS_CHOICES).get(fichier.statut, fichier.statut)
            return JsonResponse({
                'success': False,
                'message': f'Impossible de supprimer cette soumission. Statut actuel : {statut_display}. Seules les soumissions "En cours" peuvent être supprimées.'
            }, status=400)
        
        # Enregistrer les informations avant suppression (pour le log)
        nom_fichier = fichier.nom_fichier
        date_import = fichier.date_import
        
        # Supprimer le fichier et toutes les données associées
        with transaction.atomic():
            # Les données liées (crédits, découverts, etc.) seront supprimées automatiquement
            # grâce aux relations ForeignKey avec on_delete
            fichier.delete()
            
            # Enregistrer l'action dans le journal
            ActionUtilisateur.enregistrer_action(
                utilisateur=request.user,
                type_action='SUPPRESSION_FICHIER',
                description=f"Suppression de la soumission : {nom_fichier} (importé le {date_import.strftime('%d/%m/%Y %H:%M')})",
                etablissement=request.user.etablissement,
                request=request
            )
        
        logger.info(f"AEF {request.user.email} a supprimé la soumission {nom_fichier} (ID: {fichier_id})")
        
        return JsonResponse({
            'success': True,
            'message': f'La soumission "{nom_fichier}" a été supprimée avec succès.'
        })
        
    except FichierImport.DoesNotExist:
        logger.warning(f"Tentative de suppression d'une soumission inexistante (ID: {fichier_id})")
        return JsonResponse({
            'success': False,
            'message': 'Soumission non trouvée ou vous n\'avez pas les permissions nécessaires.'
        }, status=404)
        
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de la soumission {fichier_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Une erreur est survenue lors de la suppression de la soumission.'
        }, status=500)