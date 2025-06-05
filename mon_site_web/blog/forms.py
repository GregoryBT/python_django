from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from .models import Article, Commentaire, Categorie, Tag, Profil, SignalementCommentaire

class InscriptionForm(UserCreationForm):
    """Formulaire d'inscription personnalisé"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Votre prénom'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Votre nom'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'votre@email.com'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mot de passe'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmer le mot de passe'})
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Mettre à jour le profil créé automatiquement par le signal
            # avec le rôle "utilisateur" par défaut
            profil = user.profil
            profil.role = 'utilisateur'
            profil.save()
        return user


class ConnexionForm(AuthenticationForm):
    """Formulaire de connexion personnalisé"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nom d\'utilisateur'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })


class ProfilForm(forms.ModelForm):
    """Formulaire pour modifier le profil utilisateur"""
    # Champs utilisateur (informations de base)
    first_name = forms.CharField(
        max_length=30, 
        required=False, 
        label="Prénom",
        widget=forms.TextInput(attrs={
            'class': 'form-control w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white',
            'placeholder': 'Votre prénom'
        })
    )
    last_name = forms.CharField(
        max_length=30, 
        required=False, 
        label="Nom",
        widget=forms.TextInput(attrs={
            'class': 'form-control w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white',
            'placeholder': 'Votre nom'
        })
    )
    email = forms.EmailField(
        required=False,
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white',
            'placeholder': 'votre@email.com'
        })
    )
    
    class Meta:
        model = Profil
        fields = ['bio', 'avatar', 'site_web']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-none',
                'rows': 4,
                'placeholder': 'Parlez-nous de vous, vos domaines d\'expertise, vos passions...'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white',
                'accept': 'image/*'
            }),
            'site_web': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white',
                'placeholder': 'https://votre-site.com'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        # Récupérer les arguments personnalisés
        user_instance = kwargs.pop('instance', None)  # Instance User
        profil_instance = kwargs.pop('profil_instance', None)  # Instance Profil
        
        # Utiliser l'instance de profil pour le formulaire
        if profil_instance:
            kwargs['instance'] = profil_instance
        
        super().__init__(*args, **kwargs)
        
        # Si on a une instance User, préremplir les champs utilisateur
        if user_instance:
            self.fields['first_name'].initial = user_instance.first_name
            self.fields['last_name'].initial = user_instance.last_name
            self.fields['email'].initial = user_instance.email
        
        # Rendre les champs requis pour une meilleure UX
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        
        # Messages d'aide
        self.fields['bio'].help_text = "Décrivez-vous en quelques mots (optionnel)"
        self.fields['avatar'].help_text = "Format recommandé : JPG, PNG. Taille max : 2MB"
        self.fields['site_web'].help_text = "Votre site web personnel ou professionnel (optionnel)"
    
    def clean_email(self):
        """Validation de l'email pour éviter les doublons"""
        email = self.cleaned_data.get('email')
        if email:
            # Vérifier si un autre utilisateur utilise déjà cet email
            user = self.instance.user if hasattr(self.instance, 'user') else None
            if User.objects.filter(email=email).exclude(pk=user.pk if user else None).exists():
                raise forms.ValidationError("Cette adresse email est déjà utilisée par un autre compte.")
        return email
    
    def save(self, commit=True):
        """Sauvegarder le profil et les informations utilisateur"""
        profil = super().save(commit=False)
        
        # Mettre à jour les informations de l'utilisateur
        user = profil.user
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.email = self.cleaned_data.get('email', '')
        
        if commit:
            user.save()
            profil.save()
        
        return profil


class ArticleForm(forms.ModelForm):
    # Nouveau champ pour la saisie de nouveaux tags
    nouveaux_tags = forms.CharField(
        required=False,
        label="Nouveaux tags",
        widget=forms.TextInput(attrs={
            'class': 'appearance-none relative block w-full px-3 py-3 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm bg-white dark:bg-gray-700',
            'placeholder': 'Séparez les tags par des virgules (ex: python, django, web)'
        }),
        help_text="Saisissez de nouveaux tags séparés par des virgules. Ils seront créés automatiquement."
    )
    
    class Meta:
        model = Article
        fields = ['titre', 'contenu', 'categorie', 'tags', 'nouveaux_tags', 'image', 'est_publie']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'appearance-none relative block w-full px-3 py-3 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm bg-white dark:bg-gray-700',
                'placeholder': 'Titre de votre article...'
            }),
            'contenu': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Contenu de votre article...'}),
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'est_publie': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categorie'].empty_label = "Sélectionnez une catégorie (optionnel)"
        self.fields['tags'].help_text = "Sélectionnez des tags existants"
        self.fields['est_publie'].help_text = "Décochez pour sauvegarder en brouillon"
        # Rendre le titre et le contenu obligatoires
        self.fields['titre'].required = True
        self.fields['contenu'].required = True

    def clean_nouveaux_tags(self):
        """Validation et nettoyage des nouveaux tags"""
        nouveaux_tags = self.cleaned_data.get('nouveaux_tags', '')
        if nouveaux_tags:
            # Nettoyer et valider les tags
            tags_list = [tag.strip() for tag in nouveaux_tags.split(',')]
            tags_list = [tag for tag in tags_list if tag]  # Supprimer les chaînes vides
            
            # Valider chaque tag
            for tag in tags_list:
                if len(tag) < 2:
                    raise forms.ValidationError(f"Le tag '{tag}' est trop court (minimum 2 caractères).")
                if len(tag) > 50:
                    raise forms.ValidationError(f"Le tag '{tag}' est trop long (maximum 50 caractères).")
                # Vérifier que le tag ne contient que des caractères alphanumériques, espaces, tirets et underscores
                import re
                if not re.match(r'^[a-zA-Z0-9\s\-_]+$', tag):
                    raise forms.ValidationError(f"Le tag '{tag}' contient des caractères non autorisés. Utilisez seulement des lettres, chiffres, espaces, tirets et underscores.")
            
            return tags_list
        return []

    def clean_contenu(self):
        """Validation personnalisée pour le contenu"""
        contenu = self.cleaned_data.get('contenu')
        if contenu:
            # Supprimer les balises HTML pour vérifier le contenu réel
            import re
            contenu_text = re.sub(r'<[^>]+>', '', contenu).strip()
            if not contenu_text:
                raise forms.ValidationError("Le contenu de l'article ne peut pas être vide.")
        else:
            raise forms.ValidationError("Le contenu de l'article est requis.")
        return contenu

    def clean_titre(self):
        """Validation personnalisée pour le titre"""
        titre = self.cleaned_data.get('titre')
        if titre:
            titre = titre.strip()
            if len(titre) < 5:
                raise forms.ValidationError("Le titre doit contenir au moins 5 caractères.")
            if len(titre) > 200:
                raise forms.ValidationError("Le titre ne peut pas dépasser 200 caractères.")
        return titre

    def save(self, commit=True):
        """Sauvegarder l'article et créer les nouveaux tags"""
        from django.utils.text import slugify
        import random
        
        article = super().save(commit=False)
        
        if commit:
            article.save()
            
            # Traiter les nouveaux tags
            nouveaux_tags = self.cleaned_data.get('nouveaux_tags', [])
            if nouveaux_tags:
                tags_crees = []
                couleurs_disponibles = [
                    '#ef4444', '#f97316', '#f59e0b', '#eab308', '#84cc16',
                    '#22c55e', '#10b981', '#14b8a6', '#06b6d4', '#0ea5e9',
                    '#3b82f6', '#6366f1', '#8b5cf6', '#a855f7', '#d946ef',
                    '#ec4899', '#f43f5e', '#6b7280', '#374151', '#1f2937'
                ]
                
                for tag_nom in nouveaux_tags:
                    # Rechercher par nom exact d'abord (insensible à la casse)
                    tag = Tag.objects.filter(nom__iexact=tag_nom).first()
                    
                    if tag:
                        # Tag trouvé, le réutiliser
                        tags_crees.append(tag)
                    else:
                        # Tag non trouvé, en créer un nouveau avec slug unique
                        base_slug = slugify(tag_nom)
                        slug = base_slug
                        counter = 1
                        
                        # Vérifier si le slug existe déjà et créer un slug unique si nécessaire
                        while Tag.objects.filter(slug=slug).exists():
                            slug = f"{base_slug}-{counter}"
                            counter += 1
                        
                        # Créer le nouveau tag avec le slug unique
                        tag = Tag.objects.create(
                            nom=tag_nom,
                            slug=slug,
                            couleur=random.choice(couleurs_disponibles)
                        )
                        tags_crees.append(tag)
                
                # Ajouter les nouveaux tags à l'article
                article.tags.add(*tags_crees)
            
            # Sauvegarder les relations many-to-many pour les tags existants sélectionnés
            self.save_m2m()
        
        return article


class CommentaireForm(forms.ModelForm):
    class Meta:
        model = Commentaire
        fields = ['contenu']
        widgets = {
            'contenu': forms.Textarea(attrs={
                'class': 'appearance-none relative block w-full px-3 py-3 pl-10 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm bg-white dark:bg-gray-700 resize-none',
                'rows': 4,
                'placeholder': 'Partagez votre opinion sur cet article...'
            }),
        }


class MotDePasseOublieForm(PasswordResetForm):
    """Formulaire personnalisé pour la demande de réinitialisation de mot de passe"""
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre adresse email',
            'autocomplete': 'email'
        }),
        label="Adresse email"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].help_text = "Entrez l'adresse email associée à votre compte. Nous vous enverrons un lien pour réinitialiser votre mot de passe."


class NouveauMotDePasseForm(SetPasswordForm):
    """Formulaire personnalisé pour définir un nouveau mot de passe"""
    new_password1 = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nouveau mot de passe',
            'autocomplete': 'new-password'
        }),
        strip=False,
    )
    new_password2 = forms.CharField(
        label="Confirmez le nouveau mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmez le nouveau mot de passe',
            'autocomplete': 'new-password'
        }),
        strip=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].help_text = "Votre mot de passe doit contenir au moins 8 caractères et ne peut pas être entièrement numérique."


class SignalementCommentaireForm(forms.ModelForm):
    """Formulaire pour signaler un commentaire inapproprié"""
    class Meta:
        model = SignalementCommentaire
        fields = ['motif', 'description']
        widgets = {
            'motif': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent dark:bg-gray-700 dark:text-white',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-none',
                'rows': 3,
                'placeholder': 'Décrivez le problème (optionnel)...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['motif'].required = True
        self.fields['description'].required = False
        self.fields['motif'].help_text = "Sélectionnez la raison du signalement"
        self.fields['description'].help_text = "Ajoutez des détails si nécessaire (optionnel)"