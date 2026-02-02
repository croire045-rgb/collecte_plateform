# ==========================================
# IMPORTS COMPLETS AU DÉBUT DU FICHIER
# ==========================================
import logging
import json
import pandas as pd
import csv
from datetime import datetime, timedelta

# Django imports de base
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, TemplateView, ListView, DeleteView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound, HttpResponseServerError
from django.contrib import messages
from django.utils import timezone
from django.db.models import Max, Count, Sum, Avg, Q
from django.core.cache import cache
from django.views.defaults import page_not_found, server_error
from django.db import transaction
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

# Imports des modèles et formulaires
#from .forms import EtablissementRegistrationForm, EtablissementLoginForm
from .models import (
    FichierImport, Etablissement, Credit_Amortissables, Decouverts, 
    Affacturage, Cautions, Effets_commerces, Spot, TokenInscription, 
    ActionUtilisateur, Etablissement, User
)

from .utils import (
    traiter_fichier_excel, 
    extraire_et_calculer_teg, 
    generer_statistiques_teg,
)

def is_chef(user):
    return user.is_staff or user.is_superuser

def is_acnef(user):
    return user.is_authenticated and user.role == 'ACNEF'

def is_aef(user):
    return user.is_authenticated and user.role == 'AEF'

logger = logging.getLogger(__name__)

# ==========================================
# 1. BANNIR UN UTILISATEUR
# ==========================================
@login_required
@user_passes_test(is_chef)
@require_http_methods(["POST"])
def bannir_utilisateur(request, user_id):
    try:
        utilisateur = get_object_or_404(User, id=user_id)
        if utilisateur.id == request.user.id:
            return JsonResponse({'success': False, 'message': 'Vous ne pouvez pas vous bannir vous-même'}, status=400)
        if utilisateur.is_superuser:
            return JsonResponse({'success': False, 'message': 'Impossible de bannir un super administrateur'}, status=403)
        if not utilisateur.is_active:
            return JsonResponse({'success': False, 'message': 'Cet utilisateur est déjà banni'}, status=400)
        
        nom_complet = utilisateur.get_full_name()
        utilisateur.is_active = False
        utilisateur.save()
        
        ActionUtilisateur.enregistrer_action(
            utilisateur=request.user, type_action='MODIFICATION_UTILISATEUR',
            description=f"Bannissement de l'utilisateur {nom_complet}",
            etablissement=utilisateur.etablissement, request=request
        )
        return JsonResponse({'success': True, 'message': f'Utilisateur {nom_complet} banni'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erreur : {str(e)}'}, status=500)

@login_required
@user_passes_test(is_chef)
@require_http_methods(["POST"])
def supprimer_journaux(request):
    try:
        import json
        from datetime import datetime
        from django.utils import timezone
        
        data = json.loads(request.body)
        mode = data.get('mode')
        date_debut_str = data.get('date_debut')
        date_fin_str = data.get('date_fin')
        
        if not mode or not date_debut_str:
            return JsonResponse({'success': False, 'message': 'Paramètres manquants'}, status=400)
        
        date_debut = timezone.make_aware(datetime.fromisoformat(date_debut_str))
        
        if mode == 'intervalle':
            if not date_fin_str:
                return JsonResponse({'success': False, 'message': 'Date fin requise'}, status=400)
            date_fin = timezone.make_aware(datetime.fromisoformat(date_fin_str))
            queryset = ActionUtilisateur.objects.filter(date_action__gte=date_debut, date_action__lte=date_fin)
        else:
            queryset = ActionUtilisateur.objects.filter(date_action__lt=date_debut)
        
        nombre = queryset.count()
        if nombre == 0:
            return JsonResponse({'success': False, 'message': 'Aucune entrée'}, status=400)
        
        ActionUtilisateur.enregistrer_action(utilisateur=request.user, type_action='AUTRE',
            description=f"Suppression de {nombre} journaux", etablissement=None, request=request)
        queryset.delete()
        
        return JsonResponse({'success': True, 'nombre_lignes': nombre})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
@user_passes_test(is_chef)
@require_http_methods(["POST"])
def compter_journaux_a_supprimer(request):
    try:
        import json
        from datetime import datetime
        from django.utils import timezone
        
        data = json.loads(request.body)
        mode = data.get('mode')
        date_debut_str = data.get('date_debut')
        date_fin_str = data.get('date_fin')
        
        date_debut = timezone.make_aware(datetime.fromisoformat(date_debut_str))
        
        if mode == 'intervalle':
            date_fin = timezone.make_aware(datetime.fromisoformat(date_fin_str))
            queryset = ActionUtilisateur.objects.filter(date_action__gte=date_debut, date_action__lte=date_fin)
        else:
            queryset = ActionUtilisateur.objects.filter(date_action__lt=date_debut)
        
        return JsonResponse({'success': True, 'nombre': queryset.count()})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)