from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Article, Commentaire, Categorie, Tag, Profil

class InscriptionForm(UserCreationForm):
    """Formulaire d'inscription personnalisé"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")
    role = forms.ChoiceField(
        choices=[('lecteur', 'Lecteur'), ('auteur', 'Auteur')],
        initial='lecteur',
        label="Type de compte"
    )
    
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
        self.fields['role'].widget.attrs.update({'class': 'form-control'})
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Créer le profil avec le rôle sélectionné
            profil = Profil.objects.create(
                user=user,
                role=self.cleaned_data['role']
            )
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
    first_name = forms.CharField(max_length=30, required=False, label="Prénom")
    last_name = forms.CharField(max_length=30, required=False, label="Nom")
    email = forms.EmailField(required=False)
    
    class Meta:
        model = Profil
        fields = ['bio', 'avatar', 'site_web']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Parlez-nous de vous...'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'site_web': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://votre-site.com'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
            self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
            self.fields['email'].widget.attrs.update({'class': 'form-control'})


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['titre', 'contenu', 'categorie', 'tags', 'image', 'est_publie']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de l\'article'}),
            'contenu': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Contenu de votre article...'}),
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'est_publie': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categorie'].empty_label = "Sélectionnez une catégorie (optionnel)"
        self.fields['tags'].help_text = "Sélectionnez un ou plusieurs tags pour classer votre article"
        self.fields['est_publie'].help_text = "Décochez pour sauvegarder en brouillon"


class CommentaireForm(forms.ModelForm):
    class Meta:
        model = Commentaire
        fields = ['contenu']
        widgets = {
            'contenu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Votre commentaire...'
            }),
        }