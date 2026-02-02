"""
Module pour l'envoi d'emails dans la plateforme CNEF
"""

from django.db.models import Q
import random
import string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

def obtenir_url_logo():
    """Retourne l'URL complète du logo Congo"""
    return f"{settings.SITE_URL}/static/image/Congo.png"

def envoyer_email_invitation(token, envoyeur):
    """Envoie un email d'invitation avec le lien d'inscription"""
    try:
        from .models import HistoriqueEmail
        
        email_destinataire = token.email_destinataire
        lien_inscription = token.generer_lien_inscription()
        
        context = {
            'role': token.get_role_display(),
            'etablissement': token.etablissement.Nom_etablissement if token.etablissement else None,
            'lien': lien_inscription,
            'expiration': token.date_expiration.strftime('%d/%m/%Y à %H:%M'),
            'envoyeur_nom': envoyeur.get_full_name(),
            'envoyeur_role': envoyeur.get_role_display(),
            'logo_url': obtenir_url_logo(),
        }
        
        if token.etablissement:
            sujet = f"Invitation {token.get_role_display()} - {token.etablissement.Nom_etablissement}"
        else:
            sujet = f"Invitation {token.get_role_display()} - CNEF"
        
        html_content = generer_html_invitation(context)
        text_content = f"""
Bonjour,

Vous avez été invité(e) à rejoindre la Plateforme de Collecte du CNEF en tant que {context['role']}.

{f"Établissement : {context['etablissement']}" if context['etablissement'] else ""}

Pour créer votre compte, cliquez sur le lien ci-dessous :
{lien_inscription}

⚠️ Ce lien expire le {context['expiration']}

Invité par : {context['envoyeur_nom']} ({context['envoyeur_role']})

Cordialement,
CNEF - Comité National Économique et Financier
République du Congo
        """.strip()
        
        email = EmailMultiAlternatives(
            subject=sujet,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email_destinataire],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        HistoriqueEmail.objects.create(
            type_email='INVITATION',
            destinataire_email=email_destinataire,
            objet=sujet,
            contenu_html=html_content,
            contenu_texte=text_content,
            statut='ENVOYE',
            utilisateur_envoyeur=envoyeur,
            etablissement=token.etablissement,
            token_lie=token
        )
        
        logger.info(f"Email d'invitation envoyé à {email_destinataire} par {envoyeur.email}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email d'invitation à {email_destinataire}: {str(e)}")
        
        try:
            from .models import HistoriqueEmail
            HistoriqueEmail.objects.create(
                type_email='INVITATION',
                destinataire_email=email_destinataire,
                objet=sujet if 'sujet' in locals() else "Invitation CNEF",
                contenu_html=html_content if 'html_content' in locals() else "",
                contenu_texte=text_content if 'text_content' in locals() else "",
                statut='ECHEC',
                erreur_message=str(e),
                utilisateur_envoyeur=envoyeur,
                etablissement=token.etablissement if token.etablissement else None,
                token_lie=token
            )
        except:
            pass
        
        return False

def envoyer_email_validation(fichier):
    """Envoie un email de validation au AEF et UEF de l'établissement"""
    from .models import HistoriqueEmail, User
    
    resultat = {'aef': False, 'uef': False}
    
    try:
        aef = User.objects.filter(
            etablissement=fichier.etablissement_cnef,
            role='AEF',
            is_active=True
        ).first()
    except:
        aef = None
    
    uef = fichier.uploader_par
    
    context = {
        'fichier_nom': fichier.fichier.name.split('/')[-1],
        'etablissement': fichier.etablissement_cnef.Nom_etablissement,
        'date_validation': fichier.date_validation.strftime('%d/%m/%Y à %H:%M') if fichier.date_validation else timezone.now().strftime('%d/%m/%Y à %H:%M'),
        'nombre_lignes': fichier.total_lignes_importees,
        'logo_url': obtenir_url_logo(),
    }
    
    sujet = f"✅ Fichier validé - {fichier.etablissement_cnef.Nom_etablissement}"
    html_content = generer_html_validation(context)
    text_content = f"""
Bonjour,

Bonne nouvelle ! Votre fichier a été validé avec succès.

📁 Fichier : {context['fichier_nom']}
🏦 Établissement : {context['etablissement']}
📅 Date de validation : {context['date_validation']}
📊 Lignes traitées : {context['nombre_lignes']}

Vos données ont été prises en compte.

Cordialement,
CNEF - Comité National Économique et Financier
    """.strip()
    
    if aef and aef.email:
        try:
            email_aef = EmailMultiAlternatives(
                subject=sujet,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[aef.email],
            )
            email_aef.attach_alternative(html_content, "text/html")
            email_aef.send(fail_silently=False)
            
            HistoriqueEmail.objects.create(
                type_email='VALIDATION',
                destinataire_email=aef.email,
                destinataire_nom=aef.get_full_name(),
                objet=sujet,
                contenu_html=html_content,
                contenu_texte=text_content,
                statut='ENVOYE',
                etablissement=fichier.etablissement_cnef,
                fichier_lie=fichier
            )
            
            resultat['aef'] = True
            logger.info(f"Email de validation envoyé à AEF {aef.email}")
            
        except Exception as e:
            logger.error(f"Erreur envoi email validation à AEF {aef.email}: {str(e)}")
            HistoriqueEmail.objects.create(
                type_email='VALIDATION',
                destinataire_email=aef.email,
                destinataire_nom=aef.get_full_name(),
                objet=sujet,
                contenu_html=html_content,
                contenu_texte=text_content,
                statut='ECHEC',
                erreur_message=str(e),
                etablissement=fichier.etablissement_cnef,
                fichier_lie=fichier
            )
    
    if uef and uef.email and uef.role == 'UEF':
        try:
            email_uef = EmailMultiAlternatives(
                subject=sujet,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[uef.email],
            )
            email_uef.attach_alternative(html_content, "text/html")
            email_uef.send(fail_silently=False)
            
            HistoriqueEmail.objects.create(
                type_email='VALIDATION',
                destinataire_email=uef.email,
                destinataire_nom=uef.get_full_name(),
                objet=sujet,
                contenu_html=html_content,
                contenu_texte=text_content,
                statut='ENVOYE',
                etablissement=fichier.etablissement_cnef,
                fichier_lie=fichier
            )
            
            resultat['uef'] = True
            logger.info(f"Email de validation envoyé à UEF {uef.email}")
            
        except Exception as e:
            logger.error(f"Erreur envoi email validation à UEF {uef.email}: {str(e)}")
            HistoriqueEmail.objects.create(
                type_email='VALIDATION',
                destinataire_email=uef.email,
                destinataire_nom=uef.get_full_name(),
                objet=sujet,
                contenu_html=html_content,
                contenu_texte=text_content,
                statut='ECHEC',
                erreur_message=str(e),
                etablissement=fichier.etablissement_cnef,
                fichier_lie=fichier
            )
    
    return resultat

def envoyer_email_rejet(fichier, motif_rejet):
    """Envoie un email de rejet au AEF et UEF de l'établissement"""
    from .models import HistoriqueEmail, User
    
    resultat = {'aef': False, 'uef': False}
    
    try:
        aef = User.objects.filter(
            etablissement=fichier.etablissement_cnef,
            role='AEF',
            is_active=True
        ).first()
    except:
        aef = None
    
    uef = fichier.uploader_par
    
    context = {
        'fichier_nom': fichier.fichier.name.split('/')[-1],
        'etablissement': fichier.etablissement_cnef.Nom_etablissement,
        'date_rejet': fichier.date_validation.strftime('%d/%m/%Y à %H:%M') if fichier.date_validation else timezone.now().strftime('%d/%m/%Y à %H:%M'),
        'motif': motif_rejet,
        'logo_url': obtenir_url_logo(),
    }
    
    sujet = f"❌ Fichier rejeté - {fichier.etablissement_cnef.Nom_etablissement}"
    html_content = generer_html_rejet(context)
    text_content = f"""
Bonjour,

Votre fichier a été rejeté.

📁 Fichier : {context['fichier_nom']}
🏦 Établissement : {context['etablissement']}
📅 Date de rejet : {context['date_rejet']}

📝 Motif du rejet :
{motif_rejet}

Veuillez corriger les problèmes mentionnés et soumettre à nouveau votre fichier.

Cordialement,
CNEF - Comité National Économique et Financier
    """.strip()
    
    if aef and aef.email:
        try:
            email_aef = EmailMultiAlternatives(
                subject=sujet,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[aef.email],
            )
            email_aef.attach_alternative(html_content, "text/html")
            email_aef.send(fail_silently=False)
            
            HistoriqueEmail.objects.create(
                type_email='REJET',
                destinataire_email=aef.email,
                destinataire_nom=aef.get_full_name(),
                objet=sujet,
                contenu_html=html_content,
                contenu_texte=text_content,
                statut='ENVOYE',
                etablissement=fichier.etablissement_cnef,
                fichier_lie=fichier
            )
            
            resultat['aef'] = True
            logger.info(f"Email de rejet envoyé à AEF {aef.email}")
            
        except Exception as e:
            logger.error(f"Erreur envoi email rejet à AEF: {str(e)}")
            HistoriqueEmail.objects.create(
                type_email='REJET',
                destinataire_email=aef.email,
                destinataire_nom=aef.get_full_name(),
                objet=sujet,
                contenu_html=html_content,
                contenu_texte=text_content,
                statut='ECHEC',
                erreur_message=str(e),
                etablissement=fichier.etablissement_cnef,
                fichier_lie=fichier
            )
    
    if uef and uef.email and uef.role == 'UEF':
        try:
            email_uef = EmailMultiAlternatives(
                subject=sujet,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[uef.email],
            )
            email_uef.attach_alternative(html_content, "text/html")
            email_uef.send(fail_silently=False)
            
            HistoriqueEmail.objects.create(
                type_email='REJET',
                destinataire_email=uef.email,
                destinataire_nom=uef.get_full_name(),
                objet=sujet,
                contenu_html=html_content,
                contenu_texte=text_content,
                statut='ENVOYE',
                etablissement=fichier.etablissement_cnef,
                fichier_lie=fichier
            )
            
            resultat['uef'] = True
            logger.info(f"Email de rejet envoyé à UEF {uef.email}")
            
        except Exception as e:
            logger.error(f"Erreur envoi email rejet à UEF: {str(e)}")
            HistoriqueEmail.objects.create(
                type_email='REJET',
                destinataire_email=uef.email,
                destinataire_nom=uef.get_full_name(),
                objet=sujet,
                contenu_html=html_content,
                contenu_texte=text_content,
                statut='ECHEC',
                erreur_message=str(e),
                etablissement=fichier.etablissement_cnef,
                fichier_lie=fichier
            )
    
    return resultat

def envoyer_email_notification_acnef(fichier):
    """
    Envoie un email à tous les ACNEF/UCNEF actifs quand un nouveau fichier est soumis
    
    Args:
        fichier (FichierImport): Instance du fichier soumis
        
    Returns:
        int: Nombre d'emails envoyés avec succès
        
    Gère automatiquement :
    - Les utilisateurs avec rôle ACNEF ou UCNEF actifs
    - L'historique d'envoi (succès ou échec)
    - Les erreurs d'envoi par destinataire
    """
    from .models import HistoriqueEmail, User
    from django.core.mail import EmailMultiAlternatives
    from django.conf import settings
    import logging
    
    logger = logging.getLogger(__name__)
    
    # ==========================================
    # VALIDATIONS PRÉALABLES
    # ==========================================
    
    # Vérifier que le fichier a un établissement
    if not fichier.etablissement_cnef:
        logger.error(f"Fichier #{fichier.id} n'a pas d'établissement associé")
        return 0
    
    # Vérifier que l'établissement est actif
    if not fichier.etablissement_cnef.is_active:
        logger.warning(f"L'établissement {fichier.etablissement_cnef.Nom_etablissement} est inactif - notification annulée")
        return 0
    
    # ==========================================
    # RÉCUPÉRATION DES DESTINATAIRES (ACNEF + UCNEF)
    # ==========================================
    
    acnefs = User.objects.filter(
        Q(role='ACNEF') | Q(role='UCNEF'),
        is_active=True
    ).select_related('etablissement')
    
    if not acnefs.exists():
        logger.warning("Aucun ACNEF/UCNEF actif trouvé pour envoyer la notification")
        return 0
    
    logger.info(f"Envoi de notification à {acnefs.count()} ACNEF/UCNEF pour le fichier #{fichier.id}")
    
    # ==========================================
    # PRÉPARATION DU CONTENU DE L'EMAIL
    # ==========================================
    
    # Extraire le nom du fichier (sans le chemin complet)
    fichier_nom = fichier.fichier.name.split('/')[-1] if fichier.fichier else "Fichier sans nom"
    
    # Gérer le cas où uploader_par est None
    if fichier.uploader_par:
        soumis_par = fichier.uploader_par.get_full_name()
        role_uploadeur = fichier.uploader_par.get_role_display()
    else:
        soumis_par = "Utilisateur inconnu"
        role_uploadeur = "Rôle inconnu"
    
    # Préparer le contexte pour les templates
    context = {
        'fichier_nom': fichier_nom,
        'etablissement': fichier.etablissement_cnef.Nom_etablissement,
        'soumis_par': soumis_par,
        'role_uploadeur': role_uploadeur,
        'date_soumission': fichier.date_import.strftime('%d/%m/%Y à %H:%M'),
        'logo_url': obtenir_url_logo(),
    }
    
    # Sujet de l'email
    sujet = f"🔔 Nouveau fichier en attente - {fichier.etablissement_cnef.Nom_etablissement}"
    
    # Génération du contenu HTML
    html_content = generer_html_notification_acnef(context)
    
    # Version texte (fallback pour clients email qui ne supportent pas le HTML)
    text_content = f"""
Bonjour,

Un nouveau fichier est en attente de validation sur la Plateforme CNEF.

📁 Fichier : {context['fichier_nom']}
🏦 Établissement : {context['etablissement']}
👤 Soumis par : {context['soumis_par']}
📅 Date de soumission : {context['date_soumission']}

Veuillez vous connecter à la plateforme pour valider ou rejeter ce fichier.

Cordialement,
CNEF - Plateforme de Collecte
République du Congo
    """.strip()
    
    # ==========================================
    # ENVOI DES EMAILS À CHAQUE ACNEF/UCNEF
    # ==========================================
    
    count_success = 0
    count_echec = 0
    
    for acnef in acnefs:
        try:
            # Vérifier que l'utilisateur a une adresse email valide
            if not acnef.email:
                logger.warning(f"L'utilisateur {acnef.get_full_name()} n'a pas d'adresse email - notification ignorée")
                continue
            
            # Créer l'email avec version HTML et texte
            email_notif = EmailMultiAlternatives(
                subject=sujet,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[acnef.email],
            )
            
            # Attacher la version HTML
            email_notif.attach_alternative(html_content, "text/html")
            
            # Envoyer l'email
            email_notif.send(fail_silently=False)
            
            # ==========================================
            # ENREGISTREMENT DANS L'HISTORIQUE (SUCCÈS)
            # ==========================================
            HistoriqueEmail.objects.create(
                type_email='NOTIFICATION_ACNEF',
                destinataire_email=acnef.email,
                destinataire_nom=acnef.get_full_name(),
                objet=sujet,
                contenu_html=html_content,
                contenu_texte=text_content,
                statut='ENVOYE',
                utilisateur_envoyeur=fichier.uploader_par,  # Peut être None, c'est OK
                etablissement=fichier.etablissement_cnef,
                fichier_lie=fichier
            )
            
            count_success += 1
            logger.info(f"✅ Notification envoyée avec succès à {acnef.email} ({acnef.get_full_name()})")
            
        except Exception as e:
            # ==========================================
            # GESTION DES ERREURS D'ENVOI
            # ==========================================
            count_echec += 1
            logger.error(f"❌ Erreur lors de l'envoi de la notification à {acnef.email}: {str(e)}")
            
            # Enregistrer l'échec dans l'historique
            try:
                HistoriqueEmail.objects.create(
                    type_email='NOTIFICATION_ACNEF',
                    destinataire_email=acnef.email,
                    destinataire_nom=acnef.get_full_name(),
                    objet=sujet,
                    contenu_html=html_content,
                    contenu_texte=text_content,
                    statut='ECHEC',
                    erreur_message=str(e)[:500],  # Limiter la taille du message d'erreur
                    utilisateur_envoyeur=fichier.uploader_par,
                    etablissement=fichier.etablissement_cnef,
                    fichier_lie=fichier
                )
            except Exception as hist_error:
                logger.error(f"⚠️ Impossible d'enregistrer l'échec dans l'historique: {str(hist_error)}")
    
    # ==========================================
    # RAPPORT FINAL
    # ==========================================
    logger.info(f"""
    📊 Rapport d'envoi pour le fichier #{fichier.id}:
    - ✅ Succès : {count_success}/{acnefs.count()}
    - ❌ Échecs : {count_echec}/{acnefs.count()}
    - 🏦 Établissement : {fichier.etablissement_cnef.Nom_etablissement}
    """)
    
    return count_success

def renvoyer_email(historique_email):
    """Renvoie un email depuis l'historique"""
    try:
        email = EmailMultiAlternatives(
            subject=historique_email.objet,
            body=historique_email.contenu_texte or "",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[historique_email.destinataire_email],
        )
        
        if historique_email.contenu_html:
            email.attach_alternative(historique_email.contenu_html, "text/html")
        
        email.send(fail_silently=False)
        
        from .models import HistoriqueEmail
        HistoriqueEmail.objects.create(
            type_email=historique_email.type_email,
            destinataire_email=historique_email.destinataire_email,
            destinataire_nom=historique_email.destinataire_nom,
            objet=f"[RENVOI] {historique_email.objet}",
            contenu_html=historique_email.contenu_html,
            contenu_texte=historique_email.contenu_texte,
            statut='ENVOYE',
            utilisateur_envoyeur=historique_email.utilisateur_envoyeur,
            etablissement=historique_email.etablissement,
            token_lie=historique_email.token_lie,
            fichier_lie=historique_email.fichier_lie
        )
        
        logger.info(f"Email renvoyé à {historique_email.destinataire_email}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors du renvoi d'email: {str(e)}")
        
        from .models import HistoriqueEmail
        HistoriqueEmail.objects.create(
            type_email=historique_email.type_email,
            destinataire_email=historique_email.destinataire_email,
            destinataire_nom=historique_email.destinataire_nom,
            objet=f"[RENVOI] {historique_email.objet}",
            contenu_html=historique_email.contenu_html,
            contenu_texte=historique_email.contenu_texte,
            statut='ECHEC',
            erreur_message=str(e),
            utilisateur_envoyeur=historique_email.utilisateur_envoyeur,
            etablissement=historique_email.etablissement,
            token_lie=historique_email.token_lie,
            fichier_lie=historique_email.fichier_lie
        )
        
        return False

# ==========================================
# TEMPLATES HTML DES EMAILS
# ==========================================

def generer_html_invitation(context):
    """Génère le HTML pour l'email d'invitation"""
    
    html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 20px 0;">
                <table role="presentation" style="width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <tr>
                        <td style="background: linear-gradient(135deg, #0d6efd 0%, #0d6efddd 100%); padding: 30px; text-align: center;">
                            <img src="{context['logo_url']}" alt="Logo Congo" style="max-width: 80px; height: auto; margin-bottom: 15px;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 26px; font-weight: bold;">CNEF</h1>
                            <p style="margin: 5px 0 0 0; color: #ffffff; font-size: 14px; opacity: 0.9;">Comité National Économique et Financier</p>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 40px 30px;">
                            <h2 style="margin: 0 0 20px 0; color: #333333; font-size: 24px;">Vous êtes invité(e) ! 🎉</h2>
                            <p style="margin: 0 0 15px 0; color: #666666; font-size: 16px; line-height: 1.6;">Bonjour,</p>
                            <p style="margin: 0 0 15px 0; color: #666666; font-size: 16px; line-height: 1.6;">Vous avez été invité(e) à rejoindre la <strong>Plateforme de Collecte du CNEF</strong> en tant que :</p>
                            <div style="background-color: #e7f3ff; border-left: 4px solid #0d6efd; padding: 15px; margin: 20px 0; border-radius: 4px;">
                                <p style="margin: 0; color: #0d6efd; font-size: 18px; font-weight: bold;">{context['role']}</p>
                                {f'<p style="margin: 5px 0 0 0; color: #666666; font-size: 14px;">🏦 {context["etablissement"]}</p>' if context['etablissement'] else ''}
                            </div>
                            <p style="margin: 20px 0 10px 0; color: #666666; font-size: 14px;">👤 Invité par : <strong>{context['envoyeur_nom']}</strong> ({context['envoyeur_role']})</p>
                            <p style="margin: 20px 0 15px 0; color: #666666; font-size: 16px; line-height: 1.6;">Pour créer votre compte, cliquez sur le bouton ci-dessous :</p>
                            <table role="presentation" style="margin: 30px 0;">
                                <tr>
                                    <td style="text-align: center;">
                                        <a href="{context['lien']}" style="display: inline-block; background-color: #0d6efd; color: #ffffff; text-decoration: none; padding: 15px 40px; border-radius: 6px; font-size: 18px; font-weight: bold;">Créer mon compte</a>
                                    </td>
                                </tr>
                            </table>
                            <p style="margin: 20px 0 10px 0; color: #666666; font-size: 14px;">Ou copiez ce lien dans votre navigateur :</p>
                            <p style="margin: 0; color: #0d6efd; font-size: 12px; word-break: break-all; background-color: #f8f9fa; padding: 10px; border-radius: 4px;">{context['lien']}</p>
                            <div style="background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 6px; padding: 15px; margin: 25px 0;">
                                <p style="margin: 0; color: #856404; font-size: 14px;"><strong>Attention :</strong> Ce lien expire le <strong>{context['expiration']}</strong></p>
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td style="background-color: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #e9ecef;">
                            <p style="margin: 0 0 5px 0; color: #666666; font-size: 13px;"><strong>CNEF - Plateforme de Collecte</strong></p>
                            <p style="margin: 0; color: #999999; font-size: 12px;">République du Congo</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
    """
    return html


def generer_html_validation(context):
    """Génère le HTML pour l'email de validation"""
    
    html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0;">
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 20px 0;">
                <table role="presentation" style="width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <tr>
                        <td style="background: linear-gradient(135deg, #198754 0%, #198754dd 100%); padding: 30px; text-align: center;">
                            <img src="{context['logo_url']}" alt="Logo Congo" style="max-width: 80px; height: auto; margin-bottom: 15px;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 26px; font-weight: bold;">CNEF</h1>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 40px 30px;">
                            <h2 style="margin: 0 0 20px 0; color: #198754; font-size: 24px;">Fichier Validé ! ✅</h2>
                            <p style="margin: 0 0 15px 0; color: #666666; font-size: 16px; line-height: 1.6;">Bonjour,</p>
                            <p style="margin: 0 0 20px 0; color: #666666; font-size: 16px; line-height: 1.6;">Bonne nouvelle ! Votre fichier a été <strong>validé avec succès</strong>.</p>
                            <div style="background-color: #d1e7dd; border-left: 4px solid #198754; padding: 15px; margin: 20px 0; border-radius: 4px;">
                                <p style="margin: 0 0 8px 0; color: #333; font-size: 14px;">📁 <strong>Fichier :</strong> {context['fichier_nom']}</p>
                                <p style="margin: 0 0 8px 0; color: #333; font-size: 14px;">🏦 <strong>Établissement :</strong> {context['etablissement']}</p>
                                <p style="margin: 0 0 8px 0; color: #333; font-size: 14px;">📅 <strong>Date de validation :</strong> {context['date_validation']}</p>
                                <p style="margin: 0; color: #333; font-size: 14px;">📊 <strong>Lignes traitées :</strong> {context['nombre_lignes']}</p>
                            </div>
                            <p style="margin: 20px 0 0 0; color: #666666; font-size: 16px; line-height: 1.6;">Vos données ont été <strong>prises en compte.</strong>.</p>
                        </td>
                    </tr>
                    <tr>
                        <td style="background-color: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #e9ecef;">
                            <p style="margin: 0 0 5px 0; color: #666666; font-size: 13px;"><strong>CNEF - Plateforme de Collecte</strong></p>
                            <p style="margin: 0; color: #999999; font-size: 12px;">République du Congo</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
    """
    return html


def generer_html_rejet(context):
    """Génère le HTML pour l'email de rejet"""
    
    html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0;">
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 20px 0;">
                <table role="presentation" style="width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <tr>
                        <td style="background: linear-gradient(135deg, #dc3545 0%, #dc3545dd 100%); padding: 30px; text-align: center;">
                            <img src="{context['logo_url']}" alt="Logo Congo" style="max-width: 80px; height: auto; margin-bottom: 15px;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 26px; font-weight: bold;">CNEF</h1>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 40px 30px;">
                            <h2 style="margin: 0 0 20px 0; color: #dc3545; font-size: 24px;">Fichier Rejeté</h2>
                            <p style="margin: 0 0 15px 0; color: #666666; font-size: 16px; line-height: 1.6;">Bonjour,</p>
                            <p style="margin: 0 0 20px 0; color: #666666; font-size: 16px; line-height: 1.6;">Votre fichier a été <strong>rejeté</strong>.</p>
                            <div style="background-color: #f8d7da; border-left: 4px solid #dc3545; padding: 15px; margin: 20px 0; border-radius: 4px;">
                                <p style="margin: 0 0 8px 0; color: #333; font-size: 14px;">📁 <strong>Fichier :</strong> {context['fichier_nom']}</p>
                                <p style="margin: 0 0 8px 0; color: #333; font-size: 14px;">🏦 <strong>Établissement :</strong> {context['etablissement']}</p>
                                <p style="margin: 0; color: #333; font-size: 14px;">📅 <strong>Date de rejet :</strong> {context['date_rejet']}</p>
                            </div>
                            <div style="background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 6px; padding: 15px; margin: 20px 0;">
                                <p style="margin: 0 0 10px 0; color: #856404; font-size: 15px; font-weight: bold;">📝 Motif du rejet :</p>
                                <p style="margin: 0; color: #856404; font-size: 14px; line-height: 1.6; white-space: pre-wrap;">{context['motif']}</p>
                            </div>
                            <p style="margin: 20px 0 0 0; color: #666666; font-size: 16px; line-height: 1.6;">Veuillez <strong>corriger les problèmes mentionnés</strong> et soumettre à nouveau votre fichier.</p>
                        </td>
                    </tr>
                    <tr>
                        <td style="background-color: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #e9ecef;">
                            <p style="margin: 0 0 5px 0; color: #666666; font-size: 13px;"><strong>CNEF - Plateforme de Collecte</strong></p>
                            <p style="margin: 0; color: #999999; font-size: 12px;">République du Congo</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
    """
    return html

def generer_html_notification_acnef(context):
    """
    Génère le HTML professionnel pour la notification
    
    Args:
        context (dict): Dictionnaire contenant :
            - fichier_nom (str)
            - etablissement (str)
            - soumis_par (str)
            - role_uploadeur (str)
            - date_soumission (str)
            - logo_url (str)
    
    Returns:
        str: HTML complet de l'email
    """
    
    html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 20px 0;">
                <table role="presentation" style="width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    
                    <!-- En-tête jaune/orange pour attirer l'attention -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%); padding: 30px; text-align: center;">
                            <img src="{context['logo_url']}" alt="Logo Congo" style="max-width: 80px; height: auto; margin-bottom: 15px;">
                            <h1 style="margin: 0; color: #333333; font-size: 26px; font-weight: bold;">CNEF</h1>
                            <p style="margin: 5px 0 0 0; color: #333333; font-size: 14px; opacity: 0.9;">
                                Comité National Économique et Financier
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Contenu principal -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <h2 style="margin: 0 0 20px 0; color: #333333; font-size: 24px; text-align: center;">
                                🔔 Nouveau fichier en attente
                            </h2>
                            
                            <p style="margin: 0 0 15px 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                Bonjour,
                            </p>
                            
                            <p style="margin: 0 0 20px 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                Un <strong>nouveau fichier</strong> a été soumis sur la plateforme et est en attente de validation.
                            </p>
                            
                            <!-- Encadré avec les détails du fichier -->
                            <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; margin: 25px 0; border-radius: 4px;">
                                <p style="margin: 0 0 12px 0; color: #333; font-size: 15px;">
                                    <strong>📁 Fichier :</strong> {context['fichier_nom']}
                                </p>
                                <p style="margin: 0 0 12px 0; color: #333; font-size: 15px;">
                                    <strong>🏦 Établissement :</strong> {context['etablissement']}
                                </p>
                                <p style="margin: 0 0 12px 0; color: #333; font-size: 15px;">
                                    <strong>👤 Soumis par :</strong> {context['soumis_par']} <span style="color: #666; font-size: 13px;">({context['role_uploadeur']})</span>
                                </p>
                                <p style="margin: 0; color: #333; font-size: 15px;">
                                    <strong>📅 Date de soumission :</strong> {context['date_soumission']}
                                </p>
                            </div>
                            
                            <!-- Appel à l'action -->
                            <div style="background-color: #e3f2fd; border-radius: 8px; padding: 20px; margin: 25px 0;">
                                <p style="margin: 0 0 10px 0; color: #1976d2; font-size: 15px; font-weight: bold;">
                                    📋 Action requise :
                                </p>
                                <p style="margin: 0; color: #1976d2; font-size: 14px; line-height: 1.6;">
                                    Veuillez vous connecter à la plateforme pour <strong>valider ou rejeter</strong> ce fichier.
                                </p>
                            </div>
                            
                            <p style="margin: 25px 0 0 0; color: #666666; font-size: 14px; line-height: 1.6;">
                                Cordialement,<br>
                                <strong>CNEF - Plateforme de Collecte</strong>
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #e9ecef;">
                            <p style="margin: 0 0 5px 0; color: #666666; font-size: 13px;">
                                <strong>CNEF - Plateforme de Collecte</strong>
                            </p>
                            <p style="margin: 0; color: #999999; font-size: 12px;">
                                République du Congo
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
    """
    
    return html
 
    
"""
Utilitaires pour l'envoi d'emails - Réinitialisation de mot de passe
"""

def generate_reset_code():
    """
    Génère un code de confirmation de 6 caractères : 5 chiffres + 1 lettre majuscule
    La lettre est placée aléatoirement dans le code (pas toujours à la fin)
    
    Exemples : 1A2345, 12B345, 123C45, 1234D5, 12345E
    """
    # Générer 5 chiffres
    digits = list(random.choices(string.digits, k=5))
    
    # Générer 1 lettre majuscule
    letter = random.choice(string.ascii_uppercase)
    
    # Choisir une position aléatoire pour insérer la lettre (0 à 5)
    position = random.randint(0, 5)
    
    # Insérer la lettre à la position choisie
    digits.insert(position, letter)
    
    # Joindre pour former le code final
    return ''.join(digits)


def send_reset_code_email(email, code):
    """
    Envoie le code de réinitialisation par email avec design HTML professionnel
    
    Args:
        email (str): Adresse email du destinataire
        code (str): Code de 6 caractères à envoyer
    
    Returns:
        bool: True si envoyé avec succès, False sinon
    """
    
    # Objet de l'email
    subject = 'Votre code de réinitialisation - CNEF'
    
    # Générer le contenu HTML
    html_content = generer_html_reset_password(code)
    
    # Version texte (fallback pour clients email sans HTML)
    text_content = f"""
Bonjour,

Vous avez demandé une réinitialisation de votre mot de passe sur la Plateforme de Collecte du CNEF.

Votre code de confirmation est : {code}

Ce code expire dans 15 minutes

📝 Pour continuer :
1. Retournez sur la page de réinitialisation
2. Saisissez ce code
3. Créez votre nouveau mot de passe

⚠️ IMPORTANT
Si vous n'avez pas demandé cette réinitialisation, ignorez cet email. 
Votre compte reste sécurisé.

Cordialement,
CNEF - Plateforme de Collecte
République du Congo
    """.strip()
    
    try:
        # Créer l'email avec version HTML et texte
        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        
        # Attacher la version HTML
        email_msg.attach_alternative(html_content, "text/html")
        
        # Envoyer
        email_msg.send(fail_silently=False)
        
        return True
        
    except Exception as e:
        print(f"Erreur envoi email de réinitialisation: {e}")
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erreur envoi email reset à {email}: {str(e)}")
        return False


def is_code_expired(sent_at):
    """
    Vérifie si le code a expiré (15 minutes)
    
    Args:
        sent_at (datetime): Date/heure d'envoi du code
    
    Returns:
        bool: True si expiré, False sinon
    """
    return timezone.now() > sent_at + timedelta(minutes=15)


def generer_html_reset_password(code):
    """
    Génère le HTML professionnel pour l'email de réinitialisation
    Design inspiré des emails d'invitation CNEF
    
    Args:
        code (str): Le code de 6 caractères
    
    Returns:
        str: HTML complet de l'email
    """
    
    # URL du logo (à adapter selon ta config)
    logo_url = f"{settings.SITE_URL}/static/image/Congo.png" if hasattr(settings, 'SITE_URL') else ""
    
    html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 20px 0;">
                <table role="presentation" style="width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    
                    <!-- En-tête bleu foncé -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #1a2634 0%, #2c3e50 100%); padding: 30px; text-align: center;">
                            <img src="{logo_url}" alt="Logo Congo" style="max-width: 80px; height: auto; margin-bottom: 15px;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 26px; font-weight: bold;">
                                CNEF
                            </h1>
                            <p style="margin: 5px 0 0 0; color: #efce13; font-size: 14px;">
                                Comité National Économique et Financier
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Contenu principal -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <h2 style="margin: 0 0 20px 0; color: #2c3e50; font-size: 24px; text-align: center;">
                                Réinitialisation de mot de passe
                            </h2>
                            
                            <p style="margin: 0 0 15px 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                Bonjour,
                            </p>
                            
                            <p style="margin: 0 0 25px 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                Vous avez demandé une réinitialisation de votre mot de passe sur la <strong>Plateforme de Collecte du CNEF</strong>.
                            </p>
                            
                            <!-- Encadré CODE - Orange/Jaune -->
                            <div style="background-color: #fff3cd; border: 2px solid #ffc107; border-radius: 12px; padding: 25px; margin: 30px 0; text-align: center;">
                                <p style="margin: 0 0 10px 0; color: #856404; font-size: 15px; font-weight: bold;">
                                    Votre code de confirmation :
                                </p>
                                <div style="background-color: #ffffff; border-radius: 8px; padding: 20px; margin: 15px 0;">
                                    <p style="margin: 0; font-size: 42px; font-weight: bold; color: #2c3e50; letter-spacing: 8px; font-family: 'Courier New', monospace;">
                                        🔑 {code} 🔑
                                    </p>
                                </div>
                                <p style="margin: 10px 0 0 0; color: #856404; font-size: 13px;">
                                    Copiez ce code pour continuer
                                </p>
                            </div>
                            
                            <!-- Alerte expiration -->
                            <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; border-radius: 6px; padding: 15px; margin: 25px 0;">
                                <p style="margin: 0; color: #856404; font-size: 14px;">
                                    <strong>Attention :</strong> Ce code expire dans <strong>15 minutes</strong>
                                </p>
                            </div>
                            
                            <!-- Instructions -->
                            <div style="background-color: #f8f9fa; border-radius: 8px; padding: 20px; margin: 25px 0;">
                                <p style="margin: 0 0 10px 0; color: #2c3e50; font-size: 15px; font-weight: bold;">
                                    📝 Pour continuer :
                                </p>
                                <ol style="margin: 0; padding-left: 20px; color: #666666; font-size: 14px; line-height: 1.8;">
                                    <li>Retournez sur la page de réinitialisation</li>
                                    <li>Saisissez ce code de 6 caractères</li>
                                    <li>Créez votre nouveau mot de passe</li>
                                </ol>
                            </div>
                            
                            <!-- Alerte sécurité -->
                            <div style="background-color: #fef2f2; border-left: 4px solid #ef4444; border-radius: 6px; padding: 15px; margin: 25px 0;">
                                <p style="margin: 0 0 8px 0; color: #991b1b; font-size: 14px; font-weight: bold;">
                                    ⚠️ IMPORTANT - Sécurité
                                </p>
                                <p style="margin: 0; color: #991b1b; font-size: 13px; line-height: 1.5;">
                                    Si vous n'avez <strong>pas demandé</strong> cette réinitialisation, ignorez cet email. 
                                    Votre compte reste sécurisé.
                                </p>
                            </div>
                            
                            <p style="margin: 25px 0 0 0; color: #666666; font-size: 14px; line-height: 1.6;">
                                Cordialement,<br>
                                <strong>CNEF - Plateforme de Collecte</strong>
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #e9ecef;">
                            <p style="margin: 0 0 5px 0; color: #666666; font-size: 13px;">
                                <strong>CNEF - Plateforme de Collecte</strong>
                            </p>
                            <p style="margin: 0; color: #999999; font-size: 12px;">
                                République du Congo
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
    """
    
    return html

