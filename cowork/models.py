from django.db import models


class Cowork(models.Model):
    name = models.SlugField(verbose_name="nombre")
    description = models.TextField(verbose_name="descripción", blank=True)
    nodes = models.ManyToManyField(to='todos_los_nodos.Nodo', verbose_name='nodo')
    users = models.ManyToManyField(to='todos_los_nodos.Usuario', verbose_name='usuario')

    def __str__(self):
        return self.name
