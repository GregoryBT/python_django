import json
import random
import re
import os
import requests
from django.conf import settings
from django.utils.text import slugify
from django.core.files.base import ContentFile
from .models import Categorie, Tag
import google.generativeai as genai


class DalleService:
    """Service pour interagir avec l'API DALL-E d'OpenAI"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', None)
        self.api_url = "https://api.openai.com/v1/images/generations"
    
    def is_available(self):
        """Vérifie si le service DALL-E est disponible"""
        return self.api_key is not None
    
    def generer_image(self, titre_article, description_prompt=None):
        """
        Génère une image avec DALL-E basée sur le titre de l'article
        
        Args:
            titre_article (str): Le titre de l'article
            description_prompt (str, optional): Description supplémentaire pour l'image
        
        Returns:
            tuple: (ContentFile, str) - Fichier image généré et nom du fichier temporaire
        """
        if not self.is_available():
            raise Exception("Service DALL-E non configuré")
        
        # Créer un prompt pour DALL-E basé sur le titre
        if description_prompt:
            prompt = f"Create a professional, clean and academic illustration for an article titled '{titre_article}'. {description_prompt}"
        else:
            prompt = f"Create a professional, clean and academic illustration for an article titled '{titre_article}'. The image should be relevant to the topic, modern, and suitable for a blog post."
        
        # Limiter la longueur du prompt (DALL-E a une limite de 1000 caractères)
        prompt = prompt[:1000]
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
            "quality": "standard",
            "response_format": "url"
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            image_url = result['data'][0]['url']
            
            # Télécharger l'image depuis l'URL
            image_response = requests.get(image_url, timeout=30)
            image_response.raise_for_status()
            
            # Créer un nom de fichier basé sur le titre
            filename = f"dalle_{slugify(titre_article)[:50]}.png"
            
            # Créer un ContentFile pour Django
            image_file = ContentFile(image_response.content, name=filename)
            
            # Sauvegarder temporairement l'image
            from django.core.files.storage import default_storage
            import uuid
            
            temp_filename = f"temp_dalle_{uuid.uuid4().hex[:8]}_{filename}"
            temp_path = default_storage.save(f"temp/{temp_filename}", image_file)
            
            return image_file, temp_path
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur lors de la requête vers DALL-E: {str(e)}")
        except KeyError as e:
            raise Exception(f"Format de réponse inattendu de DALL-E: {str(e)}")
        except Exception as e:
            raise Exception(f"Erreur lors de la génération d'image: {str(e)}")


class GeminiService:
    """Service pour interagir avec l'API Google Gemini"""
    
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            # Utiliser le modèle Gemini 1.5 Flash qui est actuellement supporté
            try:
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception:
                # Fallback vers d'autres modèles si gemini-1.5-flash n'est pas disponible
                try:
                    self.model = genai.GenerativeModel('gemini-1.5-pro')
                except Exception:
                    try:
                        self.model = genai.GenerativeModel('gemini-pro-latest')
                    except Exception:
                        self.model = None
        else:
            self.model = None
    
    def is_available(self):
        """Vérifie si le service Gemini est disponible"""
        return self.model is not None and settings.GEMINI_API_KEY
    
    def get_available_models(self):
        """Retourne la liste des modèles disponibles pour débogger"""
        if not settings.GEMINI_API_KEY:
            return []
        
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            models = genai.list_models()
            return [model.name for model in models if 'generateContent' in model.supported_generation_methods]
        except Exception as e:
            return [f"Erreur lors de la récupération des modèles: {str(e)}"]
    
    def generer_article(self, sujet):
        """
        Génère un article complet à partir d'un sujet
        
        Args:
            sujet (str): Le sujet de l'article à générer
            
        Returns:
            dict: Dictionnaire contenant titre, contenu, tags, et catégorie
        """
        if not self.is_available():
            raise Exception("Le service Gemini n'est pas configuré. Veuillez ajouter votre clé API GEMINI_API_KEY.")
        
        try:
            # Récupérer les catégories existantes pour les suggestions
            categories_existantes = list(Categorie.objects.values_list('nom', flat=True))
            categories_str = ", ".join(categories_existantes) if categories_existantes else "Technologie, Science, Culture, Société"
            
            # Prompt structuré pour générer l'article
            prompt = f"""
Tu es un rédacteur expert pour un blog académique universitaire. Génère un article complet et de qualité professionnelle sur le sujet suivant : "{sujet}"

IMPORTANT: Tu dois répondre UNIQUEMENT avec un objet JSON valide contenant exactement ces clés, sans aucun texte supplémentaire avant ou après :

{{
    "titre": "Un titre accrocheur et informatif (50-100 caractères)",
    "contenu": "Le contenu de l'article en HTML avec des balises appropriées (<h2>, <p>, <ul>, <li>, <strong>, <em>, etc.). Le contenu doit être substantiel (minimum 800 mots), bien structuré avec des sous-titres, et de qualité académique.",
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
    "categorie": "Une catégorie parmi celles-ci ou une nouvelle si nécessaire: {categories_str}"
}}

Exigences pour le contenu :
- Utilise un langage académique mais accessible
- Structure l'article avec des sous-titres (<h2>)
- Inclus des paragraphes bien développés
- Ajoute des listes quand approprié
- Utilise des balises HTML pour la mise en forme
- Minimum 800 mots de contenu substantiel
- Assure-toi que le contenu est factuel et bien recherché

Exigences pour les tags :
- Propose 5 tags pertinents et spécifiques
- Mélange de tags généraux et spécifiques
- En français, courts et descriptifs

Exemple de structure HTML pour le contenu :
<h2>Introduction</h2>
<p>Paragraphe d'introduction...</p>
<h2>Développement principal</h2>
<p>Contenu détaillé...</p>
<ul>
<li>Point important 1</li>
<li>Point important 2</li>
</ul>
<h2>Conclusion</h2>
<p>Conclusion synthétique...</p>
"""

            # Générer le contenu avec Gemini
            response = self.model.generate_content(prompt)
            
            if not response.text:
                raise Exception("Aucune réponse reçue de Gemini")
            
            # Nettoyer la réponse pour extraire uniquement le JSON
            response_text = response.text.strip()
            
            # Supprimer les balises de code markdown si présentes
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Parser le JSON
            try:
                article_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                # Si le parsing JSON échoue, essayer de nettoyer davantage
                response_text = re.sub(r'^[^{]*', '', response_text)  # Supprimer tout avant la première {
                response_text = re.sub(r'[^}]*$', '', response_text[::-1])[::-1]  # Supprimer tout après la dernière }
                try:
                    article_data = json.loads(response_text)
                except json.JSONDecodeError:
                    raise Exception(f"Impossible de parser la réponse JSON de Gemini: {str(e)}")
            
            # Valider les clés requises
            required_keys = ['titre', 'contenu', 'tags', 'categorie']
            for key in required_keys:
                if key not in article_data:
                    raise Exception(f"Clé manquante dans la réponse: {key}")
            
            # Traiter la catégorie
            categorie_nom = article_data['categorie']
            categorie = self._obtenir_ou_creer_categorie(categorie_nom)
            
            # Traiter les tags
            tags = self._traiter_tags(article_data['tags'])
            
            return {
                'titre': article_data['titre'][:200],  # Limiter à 200 caractères
                'contenu': article_data['contenu'],
                'tags': tags,
                'categorie': categorie,
                'sujet_original': sujet
            }
            
        except Exception as e:
            # En cas d'erreur, retourner un article de base
            return self._generer_article_fallback(sujet, str(e))
    
    def _obtenir_ou_creer_categorie(self, nom_categorie):
        """Obtient une catégorie existante ou en crée une nouvelle"""
        try:
            return Categorie.objects.get(nom__iexact=nom_categorie)
        except Categorie.DoesNotExist:
            # Créer une nouvelle catégorie avec une couleur aléatoire
            couleurs_disponibles = [
                '#ef4444', '#f97316', '#f59e0b', '#eab308', '#84cc16',
                '#22c55e', '#10b981', '#14b8a6', '#06b6d4', '#0ea5e9',
                '#3b82f6', '#6366f1', '#8b5cf6', '#a855f7', '#d946ef'
            ]
            return Categorie.objects.create(
                nom=nom_categorie,
                description=f"Catégorie pour les articles sur {nom_categorie.lower()}",
                couleur=random.choice(couleurs_disponibles)
            )
    
    def _traiter_tags(self, tags_list):
        """Traite la liste des tags et retourne les objets Tag"""
        tags_objets = []
        couleurs_disponibles = [
            '#ef4444', '#f97316', '#f59e0b', '#eab308', '#84cc16',
            '#22c55e', '#10b981', '#14b8a6', '#06b6d4', '#0ea5e9',
            '#3b82f6', '#6366f1', '#8b5cf6', '#a855f7', '#d946ef',
            '#ec4899', '#f43f5e', '#6b7280', '#374151', '#1f2937'
        ]
        
        for tag_nom in tags_list[:5]:  # Limiter à 5 tags maximum
            if isinstance(tag_nom, str) and len(tag_nom.strip()) > 0:
                tag_nom = tag_nom.strip()[:50]  # Limiter à 50 caractères
                tag, created = Tag.objects.get_or_create(
                    nom=tag_nom,
                    defaults={
                        'slug': slugify(tag_nom),
                        'couleur': random.choice(couleurs_disponibles)
                    }
                )
                tags_objets.append(tag)
        
        return tags_objets
    
    def _generer_article_fallback(self, sujet, erreur=""):
        """Génère un article de base en cas d'erreur avec Gemini"""
        return {
            'titre': f"Article sur {sujet}",
            'contenu': f"""
            <h2>Introduction</h2>
            <p>Cet article traite du sujet : <strong>{sujet}</strong>.</p>
            
            <h2>Développement</h2>
            <p>Le contenu de cet article sera développé ultérieurement. En attendant, voici quelques points clés à considérer :</p>
            <ul>
                <li>Recherche approfondie sur le sujet</li>
                <li>Analyse des différents aspects</li>
                <li>Présentation des conclusions</li>
            </ul>
            
            <h2>Conclusion</h2>
            <p>Ce sujet mérite une attention particulière et une étude plus approfondie.</p>
            
            {f'<p><em>Note : Erreur lors de la génération automatique : {erreur}</em></p>' if erreur else ''}
            """,
            'tags': [Tag.objects.get_or_create(nom="Général", defaults={'couleur': '#6b7280'})[0]],
            'categorie': Categorie.objects.get_or_create(
                nom="Général",
                defaults={'description': "Articles généraux", 'couleur': '#6b7280'}
            )[0],
            'sujet_original': sujet
        }