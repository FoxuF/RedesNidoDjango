import re

from django.core import validators
from django.db import models


class MacField(models.CharField):
    default_validators = [
        validators.RegexValidator(
            regex=r"^[0-9A-F]{12}$",
            message="Invalid MAC",
            flags=re.IGNORECASE,
        )
    ]
    description = "Device MAC address"

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 12
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['max_length']
        return name, path, args, kwargs

    def pre_save(self, model_instance, add):
        value: str = getattr(model_instance, self.attname)
        prep_value = value.upper()
        setattr(model_instance, self.attname, prep_value)
        return super().pre_save(model_instance, add)
