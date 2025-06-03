#!/usr/bin/env python
import os
import django
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mon_site_web.settings')
django.setup()

from django.core.mail import send_mail

def test_email():
    try:
        result = send_mail(
            'Test Email',
            'Ceci est un email de test.',
            settings.DEFAULT_FROM_EMAIL,
            ['test@example.com'],
            fail_silently=False,
        )
        print(f"Email envoyé avec succès ! Résultat: {result}")
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {e}")
        return False

if __name__ == "__main__":
    test_email()