from django.db import models

class Cours(models.Model):
    titre            = models.CharField(max_length=200, verbose_name='Titre du cours')
    enseignant       = models.CharField(max_length=100, verbose_name='Enseignant')
    date_publication = models.DateField(verbose_name='Date de publication')

    class Meta:
        verbose_name        = 'Cours'
        verbose_name_plural = 'Cours'
        ordering            = ['-date_publication']

    def __str__(self):
        return self.titre


