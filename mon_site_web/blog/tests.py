from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import Article, Categorie, Tag, Commentaire, Profil, Like, Bookmark

class ModelTests(TestCase):
    def setUp(self):
        """Configuration initiale pour les tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.categorie = Categorie.objects.create(
            nom='Test Catégorie',
            description='Description de test'
        )
        self.tag = Tag.objects.create(nom='test-tag')
        
    def test_profil_creation(self):
        """Test de création automatique du profil utilisateur"""
        self.assertTrue(hasattr(self.user, 'profil'))
        self.assertEqual(self.user.profil.role, 'utilisateur')
        
    def test_article_creation(self):
        """Test de création d'article"""
        article = Article.objects.create(
            titre='Article de test',
            contenu='Contenu de test',
            user_auteur=self.user,
            categorie=self.categorie
        )
        self.assertEqual(article.titre, 'Article de test')
        self.assertTrue(article.slug)
        self.assertEqual(article.nombre_vues, 0)
        
    def test_article_increment_vues(self):
        """Test d'incrémentation des vues"""
        article = Article.objects.create(
            titre='Article de test',
            contenu='Contenu de test',
            user_auteur=self.user
        )
        initial_vues = article.nombre_vues
        article.incrementer_vues()
        self.assertEqual(article.nombre_vues, initial_vues + 1)
        
    def test_commentaire_creation(self):
        """Test de création de commentaire"""
        article = Article.objects.create(
            titre='Article de test',
            contenu='Contenu de test',
            user_auteur=self.user
        )
        commentaire = Commentaire.objects.create(
            article=article,
            user_auteur=self.user,
            contenu='Commentaire de test'
        )
        self.assertEqual(commentaire.article, article)
        self.assertEqual(commentaire.user_auteur, self.user)
        self.assertTrue(commentaire.est_approuve)
        
    def test_like_functionality(self):
        """Test de fonctionnalité de like"""
        article = Article.objects.create(
            titre='Article de test',
            contenu='Contenu de test',
            user_auteur=self.user
        )
        like = Like.objects.create(user=self.user, article=article)
        self.assertEqual(like.user, self.user)
        self.assertEqual(like.article, article)
        self.assertEqual(article.likes.count(), 1)
        
    def test_bookmark_functionality(self):
        """Test de fonctionnalité de bookmark"""
        article = Article.objects.create(
            titre='Article de test',
            contenu='Contenu de test',
            user_auteur=self.user
        )
        bookmark = Bookmark.objects.create(
            user=self.user, 
            article=article,
            note_personnelle='Note de test'
        )
        self.assertEqual(bookmark.user, self.user)
        self.assertEqual(bookmark.article, article)
        self.assertEqual(bookmark.note_personnelle, 'Note de test')

class ViewTests(TestCase):
    def setUp(self):
        """Configuration initiale pour les tests de vues"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.article = Article.objects.create(
            titre='Article de test',
            contenu='Contenu de test',
            user_auteur=self.user,
            est_publie=True
        )
        
    def test_home_view(self):
        """Test de la vue d'accueil"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Article de test')
        
    def test_article_detail_view(self):
        """Test de la vue détail d'article"""
        response = self.client.get(reverse('detail_article', args=[self.article.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.titre)
        
    def test_articles_list_view(self):
        """Test de la liste d'articles"""
        response = self.client.get(reverse('articles'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.titre)
        
    def test_login_required_views(self):
        """Test des vues nécessitant une connexion"""
        # Test sans connexion
        response = self.client.get(reverse('profil'))
        self.assertEqual(response.status_code, 302)  # Redirection vers login
        
        # Test avec connexion
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profil'))
        self.assertEqual(response.status_code, 200)
        
    def test_toggle_like_view(self):
        """Test de la vue toggle like"""
        self.client.login(username='testuser', password='testpass123')
        
        # Premier like
        response = self.client.post(reverse('toggle_like', args=[self.article.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.article.likes.count(), 1)
        
        # Unlike
        response = self.client.post(reverse('toggle_like', args=[self.article.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.article.likes.count(), 0)
        
    def test_toggle_bookmark_view(self):
        """Test de la vue toggle bookmark"""
        self.client.login(username='testuser', password='testpass123')
        
        # Premier bookmark
        response = self.client.post(reverse('toggle_bookmark', args=[self.article.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.article.bookmarks.count(), 1)
        
        # Retirer bookmark
        response = self.client.post(reverse('toggle_bookmark', args=[self.article.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.article.bookmarks.count(), 0)

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        
    def test_user_registration(self):
        """Test d'inscription utilisateur"""
        response = self.client.post(reverse('inscription'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'utilisateur'
        })
        self.assertEqual(response.status_code, 302)  # Redirection après inscription
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
    def test_user_login(self):
        """Test de connexion utilisateur"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        response = self.client.post(reverse('connexion'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirection après connexion

class PermissionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='normaluser',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            username='adminuser',
            password='testpass123'
        )
        self.admin_user.profil.role = 'administrateur'
        self.admin_user.profil.save()
        
        self.article = Article.objects.create(
            titre='Article de test',
            contenu='Contenu de test',
            user_auteur=self.user
        )
        
    def test_user_permissions(self):
        """Test des permissions utilisateur"""
        # L'utilisateur peut créer des articles
        self.assertTrue(self.user.profil.peut_creer_article())
        
        # L'utilisateur peut modifier ses propres articles
        self.assertTrue(self.user.profil.peut_modifier_article(self.article))
        
        # L'utilisateur ne peut pas modérer
        self.assertFalse(self.user.profil.peut_moderer())
        
    def test_admin_permissions(self):
        """Test des permissions administrateur"""
        # L'admin peut tout faire
        self.assertTrue(self.admin_user.profil.peut_creer_article())
        self.assertTrue(self.admin_user.profil.peut_modifier_article(self.article))
        self.assertTrue(self.admin_user.profil.peut_moderer())
        self.assertTrue(self.admin_user.profil.est_admin())
