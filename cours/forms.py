from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Cours, ProfilUtilisateur

INPUT_CLASS  = 'input input-bordered w-full bg-base-100 focus:border-primary'
SELECT_CLASS = 'select select-bordered w-full bg-base-100'
TEXTAREA_CLASS = 'textarea textarea-bordered w-full bg-base-100 focus:border-primary'


class CoursForm(forms.ModelForm):
    class Meta:
        model  = Cours
        fields = ['titre', 'enseignant', 'date_publication', 'description']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': INPUT_CLASS, 'placeholder': 'Ex: Introduction à Python'
            }),
            'enseignant': forms.TextInput(attrs={
                'class': INPUT_CLASS, 'placeholder': 'Nom de l\'enseignant'
            }),
            'date_publication': forms.DateInput(attrs={
                'class': INPUT_CLASS, 'type': 'date'
            }),
            'description': forms.Textarea(attrs={
                'class': TEXTAREA_CLASS, 'rows': 4,
                'placeholder': 'Décrivez le contenu du cours...'
            }),
        }
        labels = {
            'titre': 'Titre du cours',
            'enseignant': 'Enseignant',
            'date_publication': 'Date de publication',
            'description': 'Description',
        }


class InscriptionForm(UserCreationForm):
    email      = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': INPUT_CLASS, 'placeholder': 'votre@email.com'})
    )
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Prénom'})
    )
    last_name  = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Nom'})
    )

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': "Nom d'utilisateur"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': INPUT_CLASS, 'placeholder': 'Mot de passe'})
        self.fields['password2'].widget.attrs.update({'class': INPUT_CLASS, 'placeholder': 'Confirmer le mot de passe'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email      = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name  = self.cleaned_data['last_name']
        if commit:
            user.save()
            # rôle fixé automatiquement à "etudiant"
            ProfilUtilisateur.objects.create(user=user, role='etudiant')
        return user

