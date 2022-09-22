from django.core import validators
from django.db import models
from django.db.models import Q

from todos_los_nodos.fields import MacField


class Site(models.Model):
    nombre = models.SlugField(unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Nodo(models.Model):
    class NodeTypeChoices(models.IntegerChoices):
        SALAS = 1
        CDC = 2, 'CDC'
        USUARIO = 3
        OTRO = 4

    nombre = models.SlugField(max_length=20, unique=True)
    port = models.CharField(max_length=6, blank=True, null=True, validators=[
        validators.RegexValidator(
            regex=r"^([0-9]+/){1,2}[0-9]+",
            message="Invalid port format"
        )
    ])
    switch = models.ForeignKey('todos_los_nodos.Switch', on_delete=models.SET_NULL, blank=True, null=True)
    type = models.PositiveSmallIntegerField(choices=NodeTypeChoices.choices, default=NodeTypeChoices.OTRO)
    description = models.TextField(blank=True, verbose_name="Descripción")

    def __str__(self):
        return self.nombre

    class Meta:
        unique_together = ('switch', 'port')

        constraints = [
            models.CheckConstraint(
                check=(
                        (Q(port__isnull=True) & Q(switch__isnull=True))
                        | (Q(port__isnull=False) & Q(switch__isnull=False))
                ),
                name="port_xnor_switch"
            )
        ]


class Usuario(models.Model):
    login = models.SlugField(max_length=15, unique=True)
    nombre = models.CharField(max_length=40, blank=True)
    apellidos = models.CharField(max_length=40, blank=True)
    ext = models.CharField(max_length=4, unique=True, blank=True, null=True)
    notas = models.TextField(blank=True)

    def __str__(self):
        return self.login


class Telefono(models.Model):
    serie = models.CharField(max_length=15, unique=True, blank=True, null=True)
    modelo = models.CharField(max_length=4)
    mac = MacField(unique=True)
    nodo = models.OneToOneField(Nodo, blank=True, null=True, on_delete=models.SET_NULL)
    usuario = models.ForeignKey(Usuario, blank=True, null=True, on_delete=models.SET_NULL)
    notas = models.TextField(blank=True)

    def __str__(self):
        return self.serie
