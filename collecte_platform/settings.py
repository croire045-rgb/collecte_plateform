"""
Django settings for collecte_platform project - PRODUCTION VERSION
Version corrigée - Sans erreurs de logs et templates

Ce fichier contient toutes les configurations nécessaires pour faire tourner
l'application Django en développement et en production de manière sécurisée.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ==============================================================================
# CHARGEMENT DES VARIABLES D'ENVIRONNEMENT
# ==============================================================================
# Charger les variables depuis le fichier .env
# Cela permet de ne pas mettre les infos sensibles dans le code
load_dotenv()

# ==============================================================================
# CHEMINS DE BASE
# ==============================================================================
# BASE_DIR : Chemin racine du projet (là où se trouve manage.py)
# .parent.parent remonte de 2 niveaux depuis ce fichier settings.py
# Exemple : /home/user/projet/collecte_platform/
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# PARAMÈTRES DE SÉCURITÉ
# ==============================================================================

# SECRET_KEY : Clé secrète pour le chiffrement de Django (sessions, CSRF, etc.)
# OBLIGATOIRE et doit être unique et secrète en production
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    # Empêche le démarrage si la SECRET_KEY n'est pas définie
    raise ValueError("SECRET_KEY must be set in environment variables")

# DEBUG : Mode débogage
# True = Affiche les erreurs détaillées (SEULEMENT EN DÉVELOPPEMENT)
# False = Masque les erreurs (OBLIGATOIRE EN PRODUCTION)
# Par défaut False pour éviter les accidents
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# ALLOWED_HOSTS : Liste des domaines autorisés à accéder à l'application
# Empêche les attaques par Host Header
# Exemple : ['cnef.cg', 'www.cnef.cg', '127.0.0.1']
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['']:
    # Empêche le démarrage si ALLOWED_HOSTS n'est pas défini en production
    raise ValueError("ALLOWED_HOSTS must be set in production")

# ==============================================================================
# HANDLERS D'ERREURS PERSONNALISÉS
# ==============================================================================
# Ces handlers définissent quelle vue afficher pour chaque type d'erreur
handler404 = 'cnef.views.custom_404_view'        # Page non trouvée
handler500 = 'cnef.views.custom_500_view'        # Erreur serveur
handler403 = 'cnef.views.custom_permission_denied_view'  # Accès refusé
handler400 = 'cnef.views.custom_bad_request_view'        # Mauvaise requête

# ==============================================================================
# SÉCURITÉ MIDDLEWARE & HTTPS
# ==============================================================================

# SECURE_SSL_REDIRECT : Force la redirection HTTP → HTTPS
# À activer UNIQUEMENT après avoir configuré le certificat SSL
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False').lower() == 'true'

# SESSION_COOKIE_SECURE : Les cookies de session ne sont envoyés que via HTTPS
# Empêche l'interception des cookies sur des connexions non sécurisées
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'

# CSRF_COOKIE_SECURE : Le cookie CSRF n'est envoyé que via HTTPS
# Protection contre les attaques CSRF sur connexions non sécurisées
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'False').lower() == 'true'

# SECURE_BROWSER_XSS_FILTER : Active le filtre XSS du navigateur
# Protection contre les attaques Cross-Site Scripting
SECURE_BROWSER_XSS_FILTER = True

# SECURE_CONTENT_TYPE_NOSNIFF : Empêche le navigateur de deviner le type MIME
# Évite les attaques par confusion de type de fichier
SECURE_CONTENT_TYPE_NOSNIFF = True

# X_FRAME_OPTIONS : Empêche l'affichage du site dans une iframe
# Protection contre le clickjacking
# 'DENY' = jamais dans une iframe
# 'SAMEORIGIN' = uniquement dans une iframe du même domaine
X_FRAME_OPTIONS = 'DENY'

# ==============================================================================
# HSTS (HTTP Strict Transport Security)
# ==============================================================================
# HSTS force le navigateur à toujours utiliser HTTPS pendant une durée définie
# À activer UNIQUEMENT si HTTPS est configuré
if SECURE_SSL_REDIRECT:
    # Durée (en secondes) pendant laquelle le navigateur se souvient d'utiliser HTTPS
    # 31536000 = 1 an
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))
    
    # Applique HSTS aussi aux sous-domaines (ex: api.cnef.cg)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    
    # Permet l'inscription dans la liste de préchargement HSTS des navigateurs
    # Attention : difficile à annuler une fois fait !
    SECURE_HSTS_PRELOAD = True
else:
    # Pas de HSTS si HTTPS n'est pas activé
    SECURE_HSTS_SECONDS = 0

# ==============================================================================
# PROTECTION CSRF (Cross-Site Request Forgery)
# ==============================================================================
# CSRF_COOKIE_HTTPONLY : Le cookie CSRF n'est pas accessible en JavaScript
# Empêche le vol du token CSRF via XSS
CSRF_COOKIE_HTTPONLY = True

# CSRF_USE_SESSIONS : Stocke le token CSRF dans la session au lieu d'un cookie
# False = utilise un cookie dédié (recommandé)
CSRF_USE_SESSIONS = False

# CSRF_COOKIE_SAMESITE : Contrôle l'envoi du cookie sur les requêtes cross-site
# 'Strict' = cookie envoyé uniquement pour les requêtes du même site
# 'Lax' = cookie envoyé pour les requêtes GET cross-site
# 'None' = cookie toujours envoyé (nécessite Secure=True)
CSRF_COOKIE_SAMESITE = 'Strict'

# ==============================================================================
# CONFIGURATION DES SESSIONS
# ==============================================================================
# SESSION_COOKIE_AGE : Durée de vie d'une session en secondes
# 1209600 = 2 semaines (14 jours)
SESSION_COOKIE_AGE = int(os.getenv('SESSION_COOKIE_AGE', '1209600'))

# SESSION_SAVE_EVERY_REQUEST : Sauvegarde la session à chaque requête
# True = renouvelle la durée de vie à chaque action
# False = la session expire après SESSION_COOKIE_AGE même si l'utilisateur est actif
SESSION_SAVE_EVERY_REQUEST = True

# SESSION_EXPIRE_AT_BROWSER_CLOSE : La session expire à la fermeture du navigateur
# False = la session persiste selon SESSION_COOKIE_AGE
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# SESSION_COOKIE_HTTPONLY : Le cookie de session n'est pas accessible en JavaScript
# Protection contre le vol de session via XSS
SESSION_COOKIE_HTTPONLY = True

# SESSION_COOKIE_SAMESITE : Contrôle l'envoi du cookie de session
# 'Lax' = permet la navigation cross-site (liens externes)
# 'Strict' = plus strict mais peut casser certaines fonctionnalités
SESSION_COOKIE_SAMESITE = 'Lax'

# ==============================================================================
# AUTHENTIFICATION
# ==============================================================================
# AUTH_USER_MODEL : Modèle utilisateur personnalisé
# Au lieu du User par défaut de Django, on utilise notre propre modèle
AUTH_USER_MODEL = 'cnef.User'

# LOGIN_URL : URL vers laquelle rediriger les utilisateurs non connectés
# Correspond au name='connexion' dans urls.py
LOGIN_URL = 'connexion'

# LOGIN_REDIRECT_URL : URL de redirection après connexion réussie
LOGIN_REDIRECT_URL = 'tableau_de_bord'

# LOGOUT_REDIRECT_URL : URL de redirection après déconnexion
LOGOUT_REDIRECT_URL = 'connexion'

# ==============================================================================
# VALIDATEURS DE MOT DE PASSE
# ==============================================================================
# Ces validateurs vérifient la robustesse des mots de passe
AUTH_PASSWORD_VALIDATORS = [
    {
        # Vérifie que le mot de passe n'est pas trop similaire aux infos de l'utilisateur
        # (nom, email, etc.)
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        # Vérifie la longueur minimale du mot de passe
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,  # Minimum 8 caractères
        }
    },
    {
        # Vérifie que le mot de passe n'est pas dans une liste de mots de passe communs
        # (123456, password, etc.)
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        # Vérifie que le mot de passe n'est pas entièrement numérique
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ==============================================================================
# APPLICATIONS INSTALLÉES
# ==============================================================================
# Liste de toutes les applications Django utilisées
INSTALLED_APPS = [
    # Applications Django natives (admin, auth, etc.)
    'django.contrib.admin',          # Interface d'administration
    'django.contrib.auth',           # Système d'authentification
    'django.contrib.contenttypes',   # Gestion des types de contenu
    'django.contrib.sessions',       # Gestion des sessions
    'django.contrib.messages',       # Framework de messages
    'django.contrib.staticfiles',    # Gestion des fichiers statiques (CSS, JS, images)
    
    # Notre application personnalisée
    'cnef',                          # Application principale du projet
]

# ==============================================================================
# MIDDLEWARE
# ==============================================================================
# Les middlewares sont des couches qui traitent les requêtes/réponses
# L'ORDRE EST IMPORTANT !
MIDDLEWARE = [
    # SecurityMiddleware : Applique diverses protections de sécurité
    'django.middleware.security.SecurityMiddleware',
    
    # SessionMiddleware : Gère les sessions utilisateur
    # DOIT être avant AuthenticationMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    # CommonMiddleware : Fonctionnalités communes (URL trailing slash, etc.)
    'django.middleware.common.CommonMiddleware',
    
    # CsrfViewMiddleware : Protection contre les attaques CSRF
    # DOIT être après SessionMiddleware
    'django.middleware.csrf.CsrfViewMiddleware',
    
    # AuthenticationMiddleware : Associe l'utilisateur à chaque requête
    # DOIT être après SessionMiddleware
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    
    # MessageMiddleware : Gère les messages temporaires (succès, erreurs, etc.)
    # DOIT être après SessionMiddleware
    'django.contrib.messages.middleware.MessageMiddleware',
    
    # XFrameOptionsMiddleware : Protection contre le clickjacking
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # BrokenLinkEmailsMiddleware : Envoie un email aux admins pour les liens cassés (404)
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    
    # Notre middleware personnalisé pour gérer les interruptions de session
    'cnef.middleware.SessionInterruptionMiddleware',
]

# ==============================================================================
# CONFIGURATION DES URLs
# ==============================================================================
# Fichier principal de configuration des URLs
ROOT_URLCONF = 'collecte_platform.urls'

# ==============================================================================
# TEMPLATES - CORRIGÉ POUR ÉVITER L'ERREUR app_dirs/loaders
# ==============================================================================
# Configuration du moteur de templates Django

# Configuration différente selon le mode DEBUG
if DEBUG:
    # ===========================================================================
    # MODE DÉVELOPPEMENT : Configuration simple et rapide
    # ===========================================================================
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],  # Pas de dossiers templates supplémentaires
            
            # APP_DIRS=True : Django cherche automatiquement les templates dans
            # le dossier templates/ de chaque application
            'APP_DIRS': True,
            
            'OPTIONS': {
                # Context processors : ajoutent des variables automatiquement
                # dans tous les templates
                'context_processors': [
                    'django.template.context_processors.request',  # Objet request
                    'django.contrib.auth.context_processors.auth', # user, perms
                    'django.contrib.messages.context_processors.messages', # messages
                ],
            },
        },
    ]
else:
    # ===========================================================================
    # MODE PRODUCTION : Configuration avec cache pour les performances
    # ===========================================================================
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            
            # APP_DIRS=False : IMPORTANT quand on utilise des loaders personnalisés
            # Django ne permet pas d'avoir APP_DIRS=True ET loaders en même temps
            'APP_DIRS': False,
            
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
                # Loaders : définissent comment Django charge les templates
                'loaders': [
                    # cached.Loader : met en cache les templates compilés
                    # Améliore grandement les performances en évitant de recompiler
                    # les templates à chaque requête
                    ('django.template.loaders.cached.Loader', [
                        # filesystem.Loader : cherche dans DIRS
                        'django.template.loaders.filesystem.Loader',
                        # app_directories.Loader : cherche dans le dossier templates/
                        # de chaque application
                        'django.template.loaders.app_directories.Loader',
                    ]),
                ],
            },
        },
    ]

# ==============================================================================
# APPLICATION WSGI
# ==============================================================================
# Point d'entrée WSGI pour le serveur web (Gunicorn, uWSGI, etc.)
WSGI_APPLICATION = 'collecte_platform.wsgi.application'

# ==============================================================================
# CONFIGURATION DE LA BASE DE DONNÉES
# ==============================================================================
DATABASES = {
    'default': {
        # Engine : Type de base de données (MySQL dans notre cas)
        'ENGINE': 'django.db.backends.mysql',
        
        # Nom de la base de données
        'NAME': os.getenv('DB_NAME'),
        
        # Utilisateur MySQL
        'USER': os.getenv('DB_USER'),
        
        # Mot de passe MySQL
        'PASSWORD': os.getenv('DB_PASSWORD'),
        
        # Hôte où se trouve MySQL
        # 'localhost' ou '127.0.0.1' pour un serveur local
        # Adresse IP pour un serveur distant
        'HOST': os.getenv('DB_HOST', 'localhost'),
        
        # Port MySQL (3306 par défaut)
        'PORT': os.getenv('DB_PORT', '3306'),
        
        'OPTIONS': {
            # Charset : encodage des caractères
            # utf8mb4 supporte tous les caractères Unicode incluant les emojis
            'charset': 'utf8mb4',
            
            # Commandes SQL exécutées à chaque connexion
            'init_command': (
                # Mode strict : erreurs au lieu de warnings pour les problèmes SQL
                "SET sql_mode='STRICT_TRANS_TABLES';"
                # Force l'utilisation de utf8mb4
                "SET NAMES utf8mb4;"
                "SET CHARACTER SET utf8mb4;"
                # Options pour les quotes dans les requêtes
                "SET SESSION sql_quote_show_create = 1;"
                "SET SESSION quote_show_create = 1;"
            ),
        },
        
        # CONN_MAX_AGE : Durée de vie maximale d'une connexion (en secondes)
        # 600 = 10 minutes
        # 0 = ferme la connexion après chaque requête (non recommandé)
        # None = connexion persistante (peut saturer MySQL)
        'CONN_MAX_AGE': int(os.getenv('DB_CONN_MAX_AGE', '600')),
    }
}

# ==============================================================================
# CONFIGURATION DU CACHE (Redis)
# ==============================================================================
# Redis est utilisé pour mettre en cache les données fréquemment accédées
# Cela améliore considérablement les performances

# Récupération des paramètres Redis depuis .env
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')

# Construction de l'URL de connexion Redis
if REDIS_PASSWORD:
    # Avec authentification : redis://:password@host:port/database
    REDIS_URL = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/1'
else:
    # Sans authentification : redis://host:port/database
    REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/1'

CACHES = {
    'default': {
        # Backend : Moteur de cache (Redis ici)
        'BACKEND': 'django_redis.cache.RedisCache',
        
        # URL de connexion à Redis
        # /1 = base de données Redis numéro 1 (Redis a 16 DB : 0-15)
        'LOCATION': REDIS_URL,
        
        'OPTIONS': {
            # Client Redis à utiliser
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            
            # Configuration du pool de connexions
            'CONNECTION_POOL_KWARGS': {
                # Nombre maximum de connexions simultanées
                'max_connections': 50,
                # Réessayer automatiquement si timeout
                'retry_on_timeout': True,
            },
            
            # Timeout pour établir la connexion (5 secondes)
            'SOCKET_CONNECT_TIMEOUT': 5,
            
            # Timeout pour les opérations (5 secondes)
            'SOCKET_TIMEOUT': 5,
        }
    }
}

# ==============================================================================
# CONFIGURATION DE CELERY
# ==============================================================================
# Celery est utilisé pour les tâches asynchrones (emails, rapports, etc.)

# CELERY_BROKER_URL : URL du broker de messages (Redis)
# Le broker gère la file d'attente des tâches
# /0 = base de données Redis numéro 0
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', f'redis://{REDIS_HOST}:{REDIS_PORT}/0')

# CELERY_RESULT_BACKEND : Où stocker les résultats des tâches
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', f'redis://{REDIS_HOST}:{REDIS_PORT}/0')

# CELERY_ACCEPT_CONTENT : Formats de sérialisation acceptés
# 'json' est le plus sûr et portable
CELERY_ACCEPT_CONTENT = ['json']

# Format de sérialisation pour les tâches
CELERY_TASK_SERIALIZER = 'json'

# Format de sérialisation pour les résultats
CELERY_RESULT_SERIALIZER = 'json'

# Fuseau horaire pour Celery (doit correspondre à TIME_ZONE)
CELERY_TIMEZONE = 'Africa/Douala'

# Enregistrer le démarrage des tâches dans les résultats
CELERY_TASK_TRACK_STARTED = True

# Temps maximum d'exécution d'une tâche (en secondes)
# 30 * 60 = 30 minutes
# Après ce délai, la tâche est automatiquement terminée
CELERY_TASK_TIME_LIMIT = 30 * 60

# ==============================================================================
# FICHIERS STATIQUES & MÉDIA
# ==============================================================================

# STATIC_URL : URL de base pour accéder aux fichiers statiques
# Exemple : http://cnef.cg/static/css/style.css
STATIC_URL = '/static/'

# STATIC_ROOT : Dossier où collecter tous les fichiers statiques en production
# Utilisé par la commande : python manage.py collectstatic
# Nginx ou Apache servira les fichiers depuis ce dossier
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# STATICFILES_DIRS : Dossiers supplémentaires contenant des fichiers statiques
# En développement seulement (en production tout va dans STATIC_ROOT)
if DEBUG:
    STATICFILES_DIRS = [
        # Dossier static/ à la racine du projet
        os.path.join(BASE_DIR, 'static'),
    ]

# MEDIA_URL : URL de base pour accéder aux fichiers uploadés par les utilisateurs
# Exemple : http://cnef.cg/media/photos/photo.jpg
MEDIA_URL = '/media/'

# MEDIA_ROOT : Dossier où stocker les fichiers uploadés
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ==============================================================================
# URL DU SITE
# ==============================================================================
# URL complète du site (utilisée dans les emails, liens absolus, etc.)
SITE_URL = os.getenv('SITE_URL', 'https://www.cnef.cg')

# ==============================================================================
# CONFIGURATION EMAIL
# ==============================================================================
# Configuration pour l'envoi d'emails (notifications, réinitialisation mot de passe, etc.)

# EMAIL_BACKEND : Moteur d'envoi d'emails
# smtp.EmailBackend = envoie via un serveur SMTP (Gmail, SendGrid, etc.)
# console.EmailBackend = affiche les emails dans la console (développement)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Serveur SMTP (Gmail dans notre cas)
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')

# Port SMTP
# 587 = TLS (recommandé)
# 465 = SSL
# 25 = Non sécurisé (à éviter)
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))

# EMAIL_USE_TLS : Utiliser TLS (Transport Layer Security)
# True = connexion sécurisée (recommandé avec port 587)
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'

# Adresse email d'envoi (doit être valide sur le serveur SMTP)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')

# Mot de passe ou "mot de passe d'application" pour Gmail
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# Adresse "From" par défaut pour tous les emails
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', f'Comité National Economique et Financier <{EMAIL_HOST_USER}>')

# Adresse email de l'administrateur
EMAIL_ADMIN = os.getenv('EMAIL_ADMIN', EMAIL_HOST_USER)

# ==============================================================================
# ADMINISTRATEURS
# ==============================================================================
# Liste des administrateurs qui reçoivent les emails d'erreur 500
ADMINS = [
    ('Admin', os.getenv('ADMIN_EMAIL', EMAIL_HOST_USER)),
]

# MANAGERS : Reçoivent les notifications de liens cassés (404)
# Par défaut, même liste que ADMINS
MANAGERS = ADMINS

# ==============================================================================
# CONFIGURATION DES LOGS - CORRIGÉ
# ==============================================================================
# Le système de logging enregistre les événements de l'application

# Créer le dossier logs s'il n'existe pas
# exist_ok=True évite une erreur si le dossier existe déjà
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

LOGGING = {
    # Version du format de configuration (toujours 1)
    'version': 1,
    
    # False = conserve les loggers existants de Django
    'disable_existing_loggers': False,
    
    # ==========================================================================
    # FORMATTERS : Définissent le format des messages de log
    # ==========================================================================
    'formatters': {
        'verbose': {
            # Format détaillé avec toutes les infos
            # {levelname} = DEBUG, INFO, WARNING, ERROR, CRITICAL
            # {asctime} = Date et heure
            # {module} = Module Python (ex: views)
            # {process:d} = ID du processus
            # {thread:d} = ID du thread
            # {message} = Message du log
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',  # Style de formatage (alternatives : '%' ou '$')
        },
        'simple': {
            # Format simple pour la console
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    
    # ==========================================================================
    # FILTERS : Filtrent les messages de log selon des conditions
    # ==========================================================================
    'filters': {
        # N'enregistre que si DEBUG=False (production)
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        # N'enregistre que si DEBUG=True (développement)
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    
    # ==========================================================================
    # HANDLERS : Définissent où envoyer les messages de log
    # ==========================================================================
    'handlers': {
        # Handler console : affiche les logs dans le terminal
        'console': {
            'level': 'INFO',  # Niveau minimum : INFO et supérieur
            'class': 'logging.StreamHandler',  # Sortie standard (terminal)
            'formatter': 'simple'  # Utilise le format simple
        },
        
        # Handler fichier pour les erreurs
        'file_error': {
            'level': 'ERROR',  # Uniquement les erreurs et critiques
            'class': 'logging.handlers.RotatingFileHandler',  # Rotation automatique
            'filename': os.path.join(LOGS_DIR, 'error.log'),  # Chemin du fichier
            'maxBytes': 1024 * 1024 * 10,  # Taille max : 10 MB
            'backupCount': 10,  # Garde 10 anciens fichiers (error.log.1, .2, etc.)
            'formatter': 'verbose',  # Format détaillé
        },
        
        # Handler fichier pour les logs généraux
        'file_general': {
            'level': 'INFO',  # INFO et supérieur
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'general.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        
        # Handler email : envoie les erreurs aux admins par email
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],  # Seulement en production
            'formatter': 'verbose'
        },
    },
    
    # ==========================================================================
    # LOGGERS : Définissent quels messages logger et où les envoyer
    # ==========================================================================
    'loggers': {
        # Logger Django : tous les logs de Django
        'django': {
            'handlers': ['console', 'file_general'],  # Console + fichier
            'level': 'INFO',
            'propagate': False,  # N'envoie pas aux loggers parents
        },
        
        # Logger django.request : logs des requêtes HTTP
        'django.request': {
            'handlers': ['file_error', 'mail_admins'],  # Fichier + email
            'level': 'ERROR',  # Uniquement les erreurs (500)
            'propagate': False,
        },
        
        # Logger de notre application cnef
        'cnef': {
            'handlers': ['console', 'file_general', 'file_error'],
            'level': 'INFO',
            'propagate': False,
        },
        
        # Logger pour les modèles
        'app.models': {
            'handlers': ['file_error'],
            'level': 'ERROR',
            'propagate': True,  # Envoie aussi aux loggers parents
        },
    },
    
    # ==========================================================================
    # ROOT LOGGER : Logger par défaut pour tout ce qui n'a pas de logger spécifique
    # ==========================================================================
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# ==============================================================================
# CONFIGURATION DES MESSAGES
# ==============================================================================
# Django Messages Framework : messages temporaires (succès, erreurs, etc.)
from django.contrib.messages import constants as messages

# Mapping des niveaux Django vers les classes CSS Bootstrap
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',      # Classe CSS : alert-debug
    messages.INFO: 'info',        # Classe CSS : alert-info
    messages.SUCCESS: 'success',  # Classe CSS : alert-success
    messages.WARNING: 'warning',  # Classe CSS : alert-warning
    messages.ERROR: 'danger',     # Classe CSS : alert-danger (Bootstrap)
}

# ==============================================================================
# INTERNATIONALISATION
# ==============================================================================

# LANGUAGE_CODE : Langue par défaut de l'application
# 'fr' = Français
# 'en' = Anglais
LANGUAGE_CODE = 'fr'

# TIME_ZONE : Fuseau horaire
# 'Africa/Douala' = GMT+1 (Afrique centrale)
# 'UTC' = Temps universel coordonné
TIME_ZONE = 'Africa/Douala'

# USE_I18N : Activer le système de traduction
# False = pas de traduction multilingue
# True = active les traductions (nécessite les fichiers .po/.mo)
USE_I18N = False

# USE_TZ : Utiliser des dates/heures avec fuseau horaire
# True = stocke en UTC, affiche dans TIME_ZONE
# False = stocke et affiche dans TIME_ZONE (peut causer des problèmes)
USE_TZ = True

# ==============================================================================
# TYPE DE CLÉ PRIMAIRE PAR DÉFAUT
# ==============================================================================
# Type de champ pour les clés primaires auto-générées (id)
# BigAutoField = entier sur 64 bits (de -9223372036854775808 à 9223372036854775807)
# AutoField = entier sur 32 bits (de -2147483648 à 2147483647)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================================
# PARAMÈTRES D'UPLOAD DE FICHIERS
# ==============================================================================

# FILE_UPLOAD_MAX_MEMORY_SIZE : Taille maximale en mémoire avant écriture sur disque
# 5242880 = 5 MB
# Les fichiers plus petits sont stockés en mémoire (plus rapide)
# Les fichiers plus gros sont écrits temporairement sur disque
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880

# DATA_UPLOAD_MAX_MEMORY_SIZE : Taille maximale des données POST
# 5242880 = 5 MB
# Empêche les attaques par saturation de mémoire
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880

# ==============================================================================
# PARAMÈTRES DE SÉCURITÉ ADDITIONNELS
# ==============================================================================

# SECURE_CONTENT_TYPE_NOSNIFF : Empêche le navigateur de deviner le type MIME
# Exemple : un fichier .txt ne sera jamais interprété comme HTML
SECURE_CONTENT_TYPE_NOSNIFF = True

# X_FRAME_OPTIONS : Protection contre le clickjacking
# 'DENY' = le site ne peut jamais être dans une iframe
# 'SAMEORIGIN' = le site peut être dans une iframe du même domaine
X_FRAME_OPTIONS = 'DENY'

# ==============================================================================
# CONFIGURATION PROXY (Nginx, Apache)
# ==============================================================================
# Ces paramètres sont nécessaires si Django est derrière un reverse proxy

# USE_X_FORWARDED_HOST : Utiliser l'en-tête X-Forwarded-Host du proxy
# True = Django utilise le nom de domaine du proxy, pas son propre hostname
USE_X_FORWARDED_HOST = os.getenv('USE_X_FORWARDED_HOST', 'False').lower() == 'true'

# USE_X_FORWARDED_PORT : Utiliser l'en-tête X-Forwarded-Port du proxy
# True = Django utilise le port du proxy (80/443), pas son propre port (8000)
USE_X_FORWARDED_PORT = os.getenv('USE_X_FORWARDED_PORT', 'False').lower() == 'true'

# SECURE_PROXY_SSL_HEADER : Fait confiance au proxy pour HTTPS
# Active uniquement si SSL est configuré sur le proxy
if SECURE_SSL_REDIRECT:
    # Tuple (header, value) : Django considère la connexion comme HTTPS
    # si l'en-tête HTTP_X_FORWARDED_PROTO vaut 'https'
    # Cet en-tête est ajouté par Nginx/Apache quand la connexion client est HTTPS
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ==============================================================================
# FIN DE LA CONFIGURATION
# ==============================================================================
# Ce fichier contient maintenant toutes les configurations nécessaires
# pour faire tourner l'application en développement et en production
# de manière sécurisée et performante.
