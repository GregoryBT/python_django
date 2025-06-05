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

## 🐳 Docker (optionnel)

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=True
    depends_on:
      - db
    volumes:
      - .:/app

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: blog_db
      POSTGRES_USER: blog_user
      POSTGRES_PASSWORD: blog_password
    volumes:
      - postgres_data:/var/lib/postgresql/data/

volumes:
  postgres_data:
```

### Lancement avec Docker

```bash
# Construire et lancer
docker-compose up --build

# En arrière-plan
docker-compose up -d

# Migrations dans le conteneur
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## 🔧 Maintenance

### Sauvegarde de la base de données

```bash
# Sauvegarde
pg_dump -U blog_user -h localhost blog_db > backup_$(date +%Y%m%d).sql

# Restauration
psql -U blog_user -h localhost blog_db < backup_20231215.sql
```

### Nettoyage des fichiers media

```bash
# Supprimer les fichiers orphelins
python manage.py shell
>>> from blog.models import Article
>>> # Script de nettoyage des images non utilisées
```

### Logs

Les logs sont stockés dans `logs/django.log`. Pour les surveiller :

```bash
# Surveiller les logs en temps réel
tail -f logs/django.log

# Rotation des logs (recommandé en production)
logrotate -f /path/to/logrotate.conf
```

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

## 📈 Performance

### Optimisations recommandées

1. **Cache Redis** (production) :
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

2. **Compression des statiques** :
```bash
pip install django-compressor
```

3. **CDN pour les médias** (production) :
```python
# Configuration AWS S3
AWS_ACCESS_KEY_ID = 'your-access-key'
AWS_SECRET_ACCESS_KEY = 'your-secret-key'
AWS_STORAGE_BUCKET_NAME = 'your-bucket-name'
```

## 🔒 Sécurité

### Checklist de sécurité production

- [ ] `DEBUG = False`
- [ ] Clé secrète complexe et unique
- [ ] HTTPS configuré
- [ ] Base de données sécurisée
- [ ] Mots de passe forts
- [ ] Sauvegardes régulières
- [ ] Logs de sécurité activés
- [ ] Mises à jour régulières

### Configuration HTTPS

```python
# Dans settings.py pour la production
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
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

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## 🚀 Démarrage rapide

```bash
# 1. Cloner et setup
git clone <repo>
cd mon_site_web
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configuration
cp .env.example .env
# Éditer .env avec vos paramètres

# 3. Base de données
python manage.py migrate
python manage.py createsuperuser

# 4. Lancement
python manage.py runserver
```

**🎉 Votre blog est prêt à l'adresse : http://127.0.0.1:8000/**

---

*Développé avec ❤️ pour la communauté académique*