#!/usr/bin/env python
"""
Script de test pour vérifier la configuration des APIs OpenAI et Gemini
"""
import os
import sys
import django
from pathlib import Path

# Ajouter le répertoire du projet au path
sys.path.append('/Users/gregoryburgnies/Documents/code/isitech/python_dm_ia/mon_site_web')

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mon_site_web.settings')
django.setup()

import requests
from django.conf import settings

def test_openai_api():
    """Test de la clé API OpenAI"""
    print("=== Test de l'API OpenAI ===")
    
    api_key = getattr(settings, 'OPENAI_API_KEY', None)
    if not api_key:
        print("❌ Clé API OpenAI non configurée")
        return False
    
    print(f"✅ Clé API trouvée: {api_key[:20]}...")
    
    # Test simple avec l'endpoint models
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test de l'authentification avec l'endpoint models
        response = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Authentification OpenAI réussie")
            models = response.json()
            dalle_models = [m for m in models['data'] if 'dall-e' in m['id']]
            print(f"✅ Modèles DALL-E disponibles: {[m['id'] for m in dalle_models]}")
            return True
        else:
            print(f"❌ Erreur d'authentification: {response.status_code}")
            print(f"Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        return False

def test_dalle_simple():
    """Test simple de génération d'image DALL-E"""
    print("\n=== Test simple DALL-E ===")
    
    api_key = getattr(settings, 'OPENAI_API_KEY', None)
    if not api_key:
        print("❌ Clé API OpenAI non configurée")
        return False
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Requête simple pour DALL-E
    data = {
        "prompt": "A simple blue circle on white background",
        "n": 1,
        "size": "256x256"  # Taille minimale pour éviter les erreurs
    }
    
    try:
        print("Envoi d'une requête de test à DALL-E...")
        response = requests.post(
            "https://api.openai.com/v1/images/generations", 
            headers=headers, 
            json=data, 
            timeout=30
        )
        
        print(f"Code de statut: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Génération d'image réussie!")
            print(f"URL de l'image: {result['data'][0]['url']}")
            return True
        else:
            print(f"❌ Erreur DALL-E: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Détails: {error_data}")
            except:
                print(f"Réponse brute: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test DALL-E: {str(e)}")
        return False

def test_gemini_api():
    """Test de la clé API Gemini"""
    print("\n=== Test de l'API Gemini ===")
    
    try:
        from blog.services import GeminiService
        
        gemini = GeminiService()
        
        if not gemini.is_available():
            print("❌ Service Gemini non disponible")
            return False
        
        print("✅ Service Gemini configuré")
        
        # Test des modèles disponibles
        models = gemini.get_available_models()
        print(f"Modèles disponibles: {models}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test Gemini: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Test des APIs d'IA\n")
    
    openai_ok = test_openai_api()
    dalle_ok = test_dalle_simple()
    gemini_ok = test_gemini_api()
    
    print("\n=== Résumé ===")
    print(f"OpenAI API: {'✅' if openai_ok else '❌'}")
    print(f"DALL-E: {'✅' if dalle_ok else '❌'}")
    print(f"Gemini: {'✅' if gemini_ok else '❌'}")
    
    if not (openai_ok and dalle_ok):
        print("\n⚠️ Des problèmes ont été détectés avec les APIs.")
        print("Vérifiez vos clés API dans le fichier .env")