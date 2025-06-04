# 🌟 Blog Académique Universitaire

Un blog moderne développé avec Django, conçu pour partager des connaissances académiques et créer une communauté d'apprentissage.

## 🚀 Fonctionnalités

### ✨ Fonctionnalités principales
- **Gestion d'articles** : Création, édition, publication et brouillons
- **Système de catégories et tags** : Organisation du contenu
- **Commentaires modérés** : Interaction communautaire
- **Likes et favoris** : Engagement des utilisateurs
- **Profils utilisateurs** : Gestion des auteurs et lecteurs
- **Analytics** : Suivi des performances des articles
- **Multilingue** : Support français/anglais

### 🔐 Système d'authentification
- Inscription et connexion sécurisées
- Réinitialisation de mot de passe par email
- Gestion des rôles (Utilisateur/Administrateur)
- Profils personnalisables avec avatar

### 📊 Interface d'administration
- Panel d'administration Django personnalisé
- Modération des commentaires
- Gestion des utilisateurs et contenus
- Statistiques détaillées

## 🛠️ Technologies utilisées

- **Backend** : Django 5.x, Python 3.11+
- **Base de données** : PostgreSQL
- **Frontend** : HTML5, CSS3, Tailwind CSS, JavaScript
- **Images** : Pillow pour le traitement d'images
- **Email** : Configuration SMTP (Mailtrap pour dev)
- **Internationalisation** : Django i18n

## 📋 Prérequis

- Python 3.11 ou supérieur
- PostgreSQL
- Git

## 🚀 Installation

### 1. Cloner le projet
```bash
git clone <url-du-repo>
cd mon_site_web
```

### 2. Créer un environnement virtuel
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configuration de l'environnement
Copiez le fichier `.env.example` vers `.env` et configurez vos variables :
```bash
cp .env.example .env
```

Modifiez le fichier `.env` avec vos paramètres :
```env
# Base de données PostgreSQL
DB_NAME=votre_nom_de_base
DB_USER=votre_utilisateur
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5432

# Clé secrète Django
SECRET_KEY=votre_cle_secrete_unique

# Configuration email (optionnel)
EMAIL_HOST=smtp.exemple.com
EMAIL_HOST_USER=votre_email
EMAIL_HOST_PASSWORD=votre_mot_de_passe
EMAIL_PORT=587
```

### 5. Configurer la base de données
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Créer un superutilisateur
```bash
python manage.py createsuperuser
```

### 7. Collecter les fichiers statiques (production)
```bash
python manage.py collectstatic
```

### 8. Lancer le serveur de développement
```bash
python manage.py runserver
```

Le site sera accessible à l'adresse : http://127.0.0.1:8000/

## 🧪 Tests

Lancer les tests unitaires :
```bash
python manage.py test
```

Avec couverture de code :
```bash
coverage run --source='.' manage.py test
coverage report
coverage html  # Génère un rapport HTML
```

## 📁 Structure du projet

```
mon_site_web/
├── blog/                   # App principale
│   ├── models.py          # Modèles (Article, Commentaire, etc.)
│   ├── views.py           # Vues et logique métier
│   ├── forms.py           # Formulaires Django
│   ├── urls.py            # URLs de l'application
│   ├── admin.py           # Configuration admin Django
│   ├── tests.py           # Tests unitaires
│   └── templates/         # Templates HTML
├── locale/                # Fichiers de traduction
├── media/                 # Fichiers uploadés
├── logs/                  # Logs de l'application
├── mon_site_web/         # Configuration Django
│   ├── settings.py       # Configuration principale
│   └── urls.py           # URLs racine
├── requirements.txt      # Dépendances Python
├── .env.example         # Exemple de configuration
└── manage.py            # Script de gestion Django
```

## 🎯 Utilisation

### Pour les auteurs
1. Créez un compte ou connectez-vous
2. Accédez à votre profil pour écrire un article
3. Organisez vos articles avec des catégories et tags
4. Publiez ou sauvegardez en brouillon

### Pour les lecteurs
1. Parcourez les articles par catégorie ou recherche
2. Likez et commentez les articles
3. Ajoutez des articles à vos favoris
4. Suivez vos auteurs préférés

### Pour les administrateurs
1. Accédez au panel d'administration (`/admin/`)
2. Modérez les commentaires
3. Gérez les utilisateurs et contenus
4. Consultez les analytics

## 🌐 Déploiement

### Variables d'environnement pour la production
```env
DEBUG=False
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com
```

### Configuration recommandée
- Serveur web : Nginx
- WSGI : Gunicorn
- Base de données : PostgreSQL
- Stockage statique : AWS S3 ou similaire

## 🤝 Contribution

1. Fork le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -am 'Ajouter nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créez une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👥 Auteurs

- **Votre Nom** - *Développement initial* - [VotreGitHub](https://github.com/votre-username)

## 🆘 Support

Si vous avez des questions ou rencontrez des problèmes :
- Ouvrez une issue sur GitHub
- Consultez la documentation Django
- Vérifiez les logs dans le dossier `logs/`

## 📈 Roadmap

- [ ] API REST pour mobile
- [ ] Système de notification en temps réel
- [ ] Édition collaborative d'articles
- [ ] Intégration réseaux sociaux
- [ ] Mode hors ligne PWA