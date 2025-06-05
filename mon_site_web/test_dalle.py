#!/usr/bin/env python3
"""
Test simple pour DALL-E après les corrections
"""
import os
import sys
import django

# Configuration Django
sys.path.append('/Users/gregoryburgnies/Documents/code/isitech/python_dm_ia/mon_site_web')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mon_site_web.settings')
django.setup()

from blog.services import DalleService

def test_dalle():
    print("🧪 Test du service DALL-E corrigé")
    
    dalle = DalleService()
    print(f"DALL-E disponible: {dalle.is_available()}")
    
    if not dalle.is_available():
        print("❌ Service DALL-E non configuré")
        return
    
    try:
        print("🎨 Test de génération d'image...")
        image_file, temp_path = dalle.generer_image(
            "Intelligence artificielle et éducation", 
            "Modern educational technology illustration"
        )
        print(f"✅ Succès! Image générée et sauvegardée: {temp_path}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération: {str(e)}")

if __name__ == "__main__":
    test_dalle()