from django.contrib import admin

from cowork.models import Cowork


@admin.register(Cowork)
class CoworkAdmin(admin.ModelAdmin):
    filter_horizontal = (
        'nodes',
        'users',
    )
