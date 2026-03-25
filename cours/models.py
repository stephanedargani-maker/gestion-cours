from django.db import models
from django.contrib.auth.models import User


class Cours(models.Model):
    titre            = models.CharField(max_length=200, verbose_name='Titre du cours')
    enseignant       = models.CharField(max_length=100, verbose_name='Enseignant')
    date_publication = models.DateField(verbose_name='Date de publication')
    description      = models.TextField(blank=True, verbose_name='Description')
    createur         = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='cours_crees', verbose_name='Créé par'
    )

    class Meta:
        verbose_name        = 'Cours'
        verbose_name_plural = 'Cours'
        ordering            = ['-date_publication']

    def __str__(self):
        return self.titre

    def peut_modifier(self, user):
        """Retourne True si l'utilisateur peut modifier ce cours."""
        if user.is_superuser:
            return True
        if user.is_staff and self.createur == user:
            return True
        return False


class Inscription(models.Model):
    etudiant   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inscriptions')
    cours      = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='inscrits')
    date_inscription = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('etudiant', 'cours')
        verbose_name = 'Inscription'
        verbose_name_plural = 'Inscriptions'
        ordering = ['-date_inscription']

    def __str__(self):
        return f"{self.etudiant.username} → {self.cours.titre}"


class ProfilUtilisateur(models.Model):
    ROLES = [
        ('admin', 'Administrateur'),
        ('enseignant', 'Enseignant'),
        ('etudiant', 'Étudiant'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    role = models.CharField(max_length=20, choices=ROLES, default='etudiant')

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
