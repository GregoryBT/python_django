from django import forms
from .models import Article, Commentaire, Categorie, Tag

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['titre', 'contenu', 'auteur', 'categorie', 'tags', 'image']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de l\'article'}),
            'contenu': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Contenu'}),
            'auteur': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de l\'auteur'}),
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categorie'].empty_label = "Sélectionnez une catégorie (optionnel)"
        self.fields['tags'].help_text = "Sélectionnez un ou plusieurs tags pour classer votre article"


class CommentaireForm(forms.ModelForm):
    class Meta:
        model = Commentaire
        fields = ['nom_auteur', 'contenu']
        widgets = {
            'nom_auteur': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre nom'
            }),
            'contenu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Votre commentaire...'
            }),
        }