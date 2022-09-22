from django.core.exceptions import ValidationError
from django.db import models
from polymorphic.models import PolymorphicModel

from todos_los_nodos.fields import MacField


class IPDevice(PolymorphicModel):
    name = models.CharField(unique=True, max_length=50, verbose_name="nombre")
    ip = models.GenericIPAddressField(protocol='IPv4', blank=True, null=True, unique=True, verbose_name="IP")
    notas = models.TextField(blank=True)
    alive = models.BooleanField(default=False, editable=False)
    lastAlive = models.DateTimeField(null=True, editable=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

    def clean_fields(self, exclude=None, validate_unique=True):
        in_name = self.name
        self.name = in_name.strip()


class Switch(IPDevice):
    SWITCH_TYPE_CHOICES = [
        ('FA', 'FastEthernet'),
        ('GI', 'GigabyteEthernet'),
    ]
    tipo = models.CharField(max_length=2, choices=SWITCH_TYPE_CHOICES)
    poe = models.BooleanField()
    site = models.ForeignKey('todos_los_nodos.Site', on_delete=models.PROTECT)

    class Meta:
        verbose_name_plural = "Switches"

    def clean_fields(self, exclude=None, **kwargs):
        super().clean_fields(exclude, **kwargs)
        if self.ip is None:
            raise ValidationError(
                message="IP of Switch cannot be null."
            )
        super().clean_fields(exclude)


class Equipo(IPDevice):
    DEVICE_TYPE_CHOICES = [
        ('PC', 'PC'),
        ('LAP', 'Lap'),
        ('MAC', 'Mac'),
        ('CAM', 'Camara'),
    ]
    tipo = models.CharField(max_length=3, choices=DEVICE_TYPE_CHOICES)
    nodo = models.ForeignKey('todos_los_nodos.Nodo', blank=True, null=True, on_delete=models.SET_NULL)
    usuario = models.ForeignKey('todos_los_nodos.Usuario', blank=True, null=True, on_delete=models.SET_NULL)


class AP(IPDevice):
    nodo = models.OneToOneField('todos_los_nodos.Nodo', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "AP"
        verbose_name_plural = "APs"
