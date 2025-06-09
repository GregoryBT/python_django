# 🌟 Blog Académique Universitaire

Une plateforme de blog moderne développée avec Django, conçue pour la communauté académique et universitaire. Cette application offre un système complet de gestion d'articles avec authentification, modération et fonctionnalités sociales.

## 📋 Table des matières

- [🚀 Fonctionnalités](#-fonctionnalités)
- [🛠️ Technologies utilisées](#️-technologies-utilisées)
- [📦 Installation](#-installation)
- [⚙️ Configuration](#️-configuration)
- [🗄️ Base de données](#️-base-de-données)
- [📧 Configuration email](#-configuration-email)
- [🤖 APIs d'IA (optionnel)](#-apis-dia-optionnel)
- [🚀 Lancement de l'application](#-lancement-de-lapplication)
- [🎯 Utilisation](#-utilisation)
- [🔐 Système de rôles](#-système-de-rôles)
- [🗺️ Routes disponibles](#️-routes-disponibles)
- [📊 Tests](#-tests)
- [🌍 Internationalisation](#-internationalisation)
- [🐳 Docker (optionnel)](#-docker-optionnel)
- [📝 Licence](#-licence)

## 🚀 Fonctionnalités

### ✨ Fonctionnalités principales
- **Gestion d'articles** : Création, édition, publication et brouillons
- **Système de catégories et tags** : Organisation du contenu
- **Commentaires modérés** : Interaction communautaire avec système de signalement
- **Likes et favoris** : Engagement des utilisateurs
- **Profils utilisateurs** : Gestion des auteurs et lecteurs avec avatars
- **Analytics** : Suivi des performances des articles et statistiques
- **Multilingue** : Support français, anglais et espagnol
- **Mode sombre** : Interface adaptative jour/nuit
- **Recherche avancée** : Filtrage par catégorie, auteur, tags
- **Génération d'images IA** : Intégration DALL-E pour illustrations
- **Assistant d'écriture IA** : Aide à la rédaction avec Google Gemini

### 🔐 Système d'authentification
- Inscription et connexion sécurisées
- Réinitialisation de mot de passe par email
- Gestion des rôles (Utilisateur/Administrateur)
- Profils personnalisables avec bio et site web
- Tracking des connexions

### 📊 Interface d'administration
- Panel d'administration Django personnalisé
- Modération des commentaires et signalements
- Gestion des utilisateurs et contenus
- Statistiques détaillées et analytics
- Gestion des catégories et tags

### 🎨 Interface utilisateur
- Design responsive (mobile, tablette, desktop)
- Interface moderne avec TailwindCSS
- Animations fluides et transitions
- Support complet du mode sombre
- Navigation intuitive

## 🛠️ Technologies utilisées

- **Backend** : Django 5.2+
- **Base de données** : PostgreSQL
- **Frontend** : HTML5, CSS3, JavaScript, TailwindCSS
- **Images** : Pillow pour traitement d'images
- **Email** : SMTP avec support Mailtrap
- **IA** : OpenAI DALL-E, Google Gemini
- **Internationalisation** : Django i18n
- **Tests** : Django Test Framework

## 📦 Installation

### Prérequis

- Python 3.8+
- PostgreSQL 12+
- pip (gestionnaire de paquets Python)
- Git

### 1. Cloner le projet

```bash
git clone <url-du-repository>
cd mon_site_web
```

### 2. Créer un environnement virtuel

```bash
# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement virtuel
# Sur macOS/Linux :
source venv/bin/activate

# Sur Windows :
venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### 1. Variables d'environnement

Créez un fichier `.env` à la racine du projet :

```env
# Configuration Django
SECRET_KEY=votre_clé_secrète_très_longue_et_complexe
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Configuration de la base de données PostgreSQL
DB_NAME=blog_db
DB_USER=blog_user
DB_PASSWORD=votre_mot_de_passe_db
DB_HOST=localhost
DB_PORT=5432

# Configuration Email (Mailtrap pour développement)
EMAIL_HOST=sandbox.smtp.mailtrap.io
EMAIL_HOST_USER=votre_username_mailtrap
EMAIL_HOST_PASSWORD=votre_password_mailtrap
EMAIL_PORT=2525

# APIs d'IA (optionnel)
GEMINI_API_KEY=votre_clé_google_gemini
OPENAI_API_KEY=votre_clé_openai
```

### 2. Générer une clé secrète Django

```python
# Dans un terminal Python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

## 🗄️ Base de données

### 1. Installation PostgreSQL

#### Sur macOS (avec Homebrew) :
```bash
brew install postgresql
brew services start postgresql
```

#### Sur Ubuntu/Debian :
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 2. Création de la base de données

```bash
# Se connecter à PostgreSQL
sudo -u postgres psql

# Créer la base de données et l'utilisateur
CREATE DATABASE blog_db;
CREATE USER blog_user WITH PASSWORD 'votre_mot_de_passe_db';
GRANT ALL PRIVILEGES ON DATABASE blog_db TO blog_user;
ALTER USER blog_user CREATEDB;
\q
```

### 3. Migrations Django

```bash
# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser
```

## 📧 Configuration email

### Option 1 : Mailtrap (développement - recommandé)

1. Créez un compte sur [Mailtrap.io](https://mailtrap.io)
2. Récupérez vos identifiants SMTP
3. Ajoutez-les dans votre fichier `.env`

### Option 2 : Gmail (production)

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-application
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

## 🤖 APIs d'IA (optionnel)

### Google Gemini (génération de contenu)

1. Allez sur [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Créez une clé API
3. Ajoutez `GEMINI_API_KEY=votre_clé` dans `.env`

### OpenAI DALL-E (génération d'images)

1. Créez un compte sur [OpenAI](https://platform.openai.com)
2. Générez une clé API
3. Ajoutez `OPENAI_API_KEY=votre_clé` dans `.env`

## 🚀 Lancement de l'application

### 1. Démarrer le serveur de développement

```bash
# Activer l'environnement virtuel
source venv/bin/activate  # ou venv\Scripts\activate sur Windows

# Lancer le serveur
python manage.py runserver
```

### 2. Accéder à l'application

- **Site principal** : http://127.0.0.1:8000/
- **Interface admin** : http://127.0.0.1:8000/admin/

### 3. Première utilisation

1. Connectez-vous à l'interface admin avec le superutilisateur
2. Créez quelques catégories d'articles
3. Ajoutez des tags
4. Créez votre premier article

## 🎯 Utilisation

### Pour les lecteurs
1. Parcourez les articles par catégorie
2. Utilisez la recherche avancée
3. Likez et commentez les articles
4. Ajoutez des articles à vos favoris
5. Consultez les profils des auteurs

### Pour les auteurs
1. Créez un compte ou connectez-vous
2. Complétez votre profil avec bio et avatar
3. Rédigez des articles avec l'éditeur intégré
4. Organisez vos articles avec catégories et tags
5. Publiez ou sauvegardez en brouillon
6. Suivez les statistiques de vos articles

### Pour les administrateurs
1. Accédez au panel d'administration (`/admin/`)
2. Modérez les commentaires et signalements
3. Gérez les utilisateurs et leurs rôles
4. Consultez les analytics détaillées
5. Administrez les catégories et tags

## 🔐 Système de rôles

### Utilisateur (par défaut)
- ✅ Lire tous les articles publiés
- ✅ Commenter (modération requise)
- ✅ Liker et sauvegarder en favoris
- ✅ Créer et gérer ses propres articles
- ✅ Modifier son profil

### Administrateur
- ✅ Toutes les permissions utilisateur
- ✅ Accès à l'interface d'administration
- ✅ Modération des commentaires
- ✅ Gestion des utilisateurs
- ✅ Suppression de tout contenu
- ✅ Accès aux statistiques complètes

## 🗺️ Routes disponibles

### 🏠 Pages principales
| Route | Nom | Description | Méthode | Authentification |
|-------|-----|-------------|---------|------------------|
| `/` | `home` | Page d'accueil avec articles récents | GET | Non |
| `/admin/` | Django Admin | Interface d'administration | GET/POST | Admin |
| `/articles/` | `articles` | Liste de tous les articles publiés | GET | Non |
| `/categories/` | `categories` | Liste des catégories | GET | Non |
| `/auteurs/` | `auteurs` | Liste des auteurs | GET | Non |
| `/a-propos/` | `a_propos` | Page à propos | GET | Non |

### 🔐 Authentification
| Route | Nom | Description | Méthode | Authentification |
|-------|-----|-------------|---------|------------------|
| `/inscription/` | `inscription` | Formulaire d'inscription | GET/POST | Non |
| `/connexion/` | `connexion` | Formulaire de connexion | GET/POST | Non |
| `/deconnexion/` | `deconnexion` | Déconnexion utilisateur | POST | Oui |
| `/profil/` | `profil` | Profil utilisateur connecté | GET/POST | Oui |
| `/utilisateur/<username>/` | `profil_public` | Profil public d'un utilisateur | GET | Non |

### 🔑 Gestion des mots de passe
| Route | Nom | Description | Méthode | Authentification |
|-------|-----|-------------|---------|------------------|
| `/mot-de-passe-oublie/` | `mot_de_passe_oublie` | Demande de réinitialisation | GET/POST | Non |
| `/mot-de-passe-oublie/envoye/` | `mot_de_passe_oublie_envoye` | Confirmation envoi email | GET | Non |
| `/reset/<uidb64>/<token>/` | `nouveau_mot_de_passe` | Nouveau mot de passe | GET/POST | Non |
| `/mot-de-passe-reinitialise/` | `mot_de_passe_reinitialise` | Confirmation réinitialisation | GET | Non |

### 📝 Gestion des articles
| Route | Nom | Description | Méthode | Authentification |
|-------|-----|-------------|---------|------------------|
| `/ajouter/` | `ajouter_article` | Créer un nouvel article | GET/POST | Oui |
| `/article/<int:article_id>/` | `detail_article` | Détail d'un article | GET/POST | Non |
| `/article/<int:article_id>/modifier/` | `modifier_article` | Modifier un article | GET/POST | Oui (Auteur) |
| `/article/<int:article_id>/supprimer/` | `supprimer_article` | Supprimer un article | POST | Oui (Auteur) |
| `/mes-articles/` | `mes_articles` | Articles de l'utilisateur | GET | Oui |

### 👥 Modération
| Route | Nom | Description | Méthode | Authentification |
|-------|-----|-------------|---------|------------------|
| `/moderation/` | `moderation` | Panel de modération | GET | Admin |
| `/moderation/approuver/<int:commentaire_id>/` | `approuver_commentaire` | Approuver un commentaire | POST | Admin |
| `/moderation/supprimer/<int:commentaire_id>/` | `supprimer_commentaire` | Supprimer un commentaire | POST | Admin |
| `/moderation/signalements/` | `gerer_signalements` | Gérer les signalements | GET | Admin |
| `/moderation/signalement/<int:signalement_id>/traiter/` | `traiter_signalement` | Traiter un signalement | POST | Admin |

### 📊 Analytics
| Route | Nom | Description | Méthode | Authentification |
|-------|-----|-------------|---------|------------------|
| `/analytics/` | `analytics` | Statistiques et analytics | GET | Admin |

### ❤️ Interactions sociales
| Route | Nom | Description | Méthode | Authentification |
|-------|-----|-------------|---------|------------------|
| `/article/<int:article_id>/like/` | `toggle_like` | Liker/Unliker un article | POST | Oui |
| `/article/<int:article_id>/bookmark/` | `toggle_bookmark` | Sauvegarder en favoris | POST | Oui |
| `/commentaire/<int:commentaire_id>/like/` | `toggle_like_commentaire` | Liker un commentaire | POST | Oui |
| `/mes-favoris/` | `mes_favoris` | Articles favoris | GET | Oui |
| `/mes-likes/` | `mes_likes` | Articles likés | GET | Oui |

### 🚨 Signalements
| Route | Nom | Description | Méthode | Authentification |
|-------|-----|-------------|---------|------------------|
| `/commentaire/<int:commentaire_id>/signaler/` | `signaler_commentaire` | Signaler un commentaire | POST | Oui |

### 🤖 Intelligence Artificielle
| Route | Nom | Description | Méthode | Authentification |
|-------|-----|-------------|---------|------------------|
| `/generer-avec-gemini/` | `generer_avec_gemini` | Génération de contenu IA | POST | Oui |
| `/image-temporaire/<path:temp_path>/` | `recuperer_image_temporaire` | Récupérer image temporaire | GET | Oui |

### 🏷️ Gestion des tags
| Route | Nom | Description | Méthode | Authentification |
|-------|-----|-------------|---------|------------------|
| `/creer-tag/` | `creer_tag` | Créer un nouveau tag | POST | Oui |
| `/creer-tags/` | `creer_tags` | Créer plusieurs tags | POST | Oui |

### 🌍 Internationalisation
| Route | Nom | Description | Méthode | Authentification |
|-------|-----|-------------|---------|------------------|
| `/i18n/setlang/` | Django i18n | Changer la langue | POST | Non |

### 📁 Fichiers médias (développement)
| Route | Description | Méthode | Authentification |
|-------|-------------|---------|------------------|
| `/media/<path:path>` | Servir les fichiers médias | GET | Non |

### 🔧 Paramètres des URLs

#### Paramètres dynamiques
- `<int:article_id>` : ID de l'article (nombre entier)
- `<int:commentaire_id>` : ID du commentaire (nombre entier)
- `<int:signalement_id>` : ID du signalement (nombre entier)
- `<str:username>` : Nom d'utilisateur (chaîne)
- `<uidb64>` : ID utilisateur encodé en base64
- `<token>` : Token de réinitialisation de mot de passe
- `<path:temp_path>` : Chemin vers fichier temporaire
- `<path:path>` : Chemin vers fichier média

#### Préfixes de langue
Les routes principales supportent les préfixes de langue :
- `/` : Français (par défaut)
- `/en/` : Anglais
- `/es/` : Espagnol

**Exemple :** `/en/articles/` pour la liste des articles en anglais

## 📊 Tests

### Lancer tous les tests

```bash
# Tests complets
python manage.py test

# Tests avec coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Génère un rapport HTML
```

### Tests spécifiques

```bash
# Tests d'une app spécifique
python manage.py test blog

# Test d'une classe spécifique
python manage.py test blog.tests.ModelTests

# Test avec verbosité
python manage.py test --verbosity=2
```

### Tester les APIs

```bash
# Test des APIs d'IA
python test_dalle.py
python test_email.py
python test_apis.py
```

## 🌍 Internationalisation

### Langues supportées
- 🇫🇷 Français (par défaut)
- 🇬🇧 Anglais
- 🇪🇸 Espagnol

### Générer les fichiers de traduction

```bash
# Extraire les chaînes à traduire
python manage.py makemessages -l en
python manage.py makemessages -l es

# Compiler les traductions
python manage.py compilemessages
```

### Ajouter une nouvelle langue

1. Ajoutez la langue dans `settings.py` :
```python
LANGUAGES = [
    ('fr', 'Français'),
    ('en', 'Anglais'),
    ('es', 'Español'),
    ('de', 'Deutsch'),  # Nouvelle langue
]
```

2. Créez les fichiers de traduction :
```bash
python manage.py makemessages -l de
```

## 🔧 Maintenance

### Logs

Les logs sont stockés dans `logs/django.log`. Pour les surveiller :

```bash
# Surveiller les logs en temps réel
tail -f logs/django.log

## 🚨 Dépannage

### Problèmes courants

#### 1. Erreur de base de données
```bash
# Vérifier que PostgreSQL fonctionne
sudo systemctl status postgresql

# Tester la connexion
psql -U blog_user -h localhost -d blog_db
```

#### 2. Erreur de migrations
```bash
# Réinitialiser les migrations (ATTENTION : perte de données)
rm blog/migrations/0*.py
python manage.py makemigrations blog
python manage.py migrate
```

#### 3. Problèmes de permissions de fichiers
```bash
# Donner les bonnes permissions au dossier media
chmod -R 755 media/
chown -R www-data:www-data media/  # En production
```

#### 4. Erreur 500 en production
```bash
# Vérifier les logs
tail -n 50 logs/django.log

# Vérifier la configuration
python manage.py check --deploy
```

## 📞 Support

### Ressources utiles

- [Documentation Django](https://docs.djangoproject.com/)
- [Documentation PostgreSQL](https://www.postgresql.org/docs/)
- [TailwindCSS](https://tailwindcss.com/docs)

### Structure du projet

```
mon_site_web/
├── blog/                   # App principale
│   ├── models.py          # Modèles de données
│   ├── views.py           # Vues et logique métier
│   ├── forms.py           # Formulaires
│   ├── admin.py           # Interface d'administration
│   ├── urls.py            # URLs de l'app
│   ├── tests.py           # Tests unitaires
│   ├── templates/         # Templates HTML
│   └── migrations/        # Migrations de base de données
├── mon_site_web/          # Configuration du projet
│   ├── settings.py        # Paramètres Django
│   ├── urls.py            # URLs principales
│   └── wsgi.py            # Configuration WSGI
├── media/                 # Fichiers uploadés
├── logs/                  # Logs de l'application
├── locale/                # Fichiers de traduction
├── requirements.txt       # Dépendances Python
└── manage.py             # Script de gestion Django
```

**🎉 Votre blog est prêt à l'adresse : http://127.0.0.1:8000/**