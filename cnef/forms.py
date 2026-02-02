from django import forms
from django.contrib.auth.forms import AuthenticationForm


class ConnexionUniverselleForm(AuthenticationForm):
    """
    Formulaire de connexion universel pour tous les rôles
    Hérite directement de AuthenticationForm qui gère déjà l'authentification
    """
    username = forms.EmailField(
        label="Adresse e-mail",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'votre-email@exemple.com',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre mot de passe'
        })
    )
    
    error_messages = {
        'invalid_login': "Email ou mot de passe incorrect.",
        'inactive': "Ce compte est inactif.",
    }