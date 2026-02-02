import logging
from django.contrib.sessions.exceptions import SessionInterrupted

class SessionInterruptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, SessionInterrupted):
            logger.warning(f"SessionInterrupted intercepté: {request.path}")
            # Rediriger vers une page d'erreur appropriée
            from django.shortcuts import render
            return render(request, 'inscription/inscription_token.html', {
                'token_valide': False,
                'error': 'Votre session a expiré. Veuillez réessayer.'
            }, status=400)