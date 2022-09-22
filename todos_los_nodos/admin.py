import csv
from distutils.util import strtobool
from functools import update_wrapper
from io import TextIOWrapper
from itertools import chain

from django import forms
from django.apps import apps
from django.contrib import admin, messages
from django.core.exceptions import ValidationError, ObjectDoesNotExist, BadRequest
from django.db import IntegrityError
from django.db.models import Model as DjangoModel
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.text import capfirst, slugify
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin, PolymorphicChildModelFilter

from todos_los_nodos import models

# admin.site.register(models.Site)
# admin.site.register(models.Switch)
# admin.site.register(models.Nodo)
# admin.site.register(models.Usuario)
# admin.site.register(models.AP)
# admin.site.register(models.Equipo)
# admin.site.register(models.Telefono)
BAD_CSV_MESSAGE = 'Unprocessable Entity: CSV File not in the expected format'


class CsvImportForm(forms.Form):
    csv_file = forms.FileField(label='CSV file')
    overwrite = forms.BooleanField(required=False)


class SuperAdmin(admin.ModelAdmin):
    def get_urls(self):
        from django.urls import path

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        my_urls = [
            path('import-csv/', wrap(self.import_csv), name="%s_%s_importcsv" % info),
        ]
        return my_urls + urls

    def _build_model_fields(self, row):
        raise NotImplementedError

    def _get_csv_syntax(self):
        raise NotImplementedError

    def import_csv(self, request, form_url="", extra_context=None):
        model: DjangoModel = self.model
        opts = model._meta
        app_label = opts.app_label
        context = {
            **self.admin_site.each_context(request),
            "title": "Import CSV",
            "opts": opts,
            "app_label": app_label,
            "model_name": opts.verbose_name_plural,
            "csv_syntax": self._get_csv_syntax(),
        }

        def format_callback(pObj):
            has_admin = model in self.admin_site._registry

            no_edit_link = "%s: %s" % (capfirst(opts.verbose_name), pObj)
            if has_admin:
                try:
                    admin_url = reverse(
                        "%s:%s_%s_change"
                        % (self.admin_site.name, opts.app_label, opts.model_name),
                        None,
                        (pObj.pk,),
                    )
                except NoReverseMatch:
                    return no_edit_link
                return format_html(
                    '<a href="{}">{}</a>', admin_url, pObj
                )
            else:
                return no_edit_link

        if request.method == "POST":
            csv_file = TextIOWrapper(request.FILES['csv_file'], encoding='utf-8')
            reader = csv.reader(csv_file)
            created_objs = []
            mod_objs = []
            create_obj_errors = []

            for row in reader:
                # try to create new entry
                try:
                    fields = self._build_model_fields(row)
                    obj = model(**fields)
                    obj.full_clean()
                    obj.save()
                    created_objs.append(format_callback(obj))
                except ValidationError as e:
                    if request.POST.get('overwrite'):
                        # overwrite
                        changed = False
                        # assume first field is unique identifier
                        entry = iter(fields.items())
                        key, name = next(entry)
                        obj = model.objects.get(**{key: name})
                        for field, val in entry:
                            if val != getattr(obj, field):
                                setattr(obj, field, val)
                                changed = True
                        if changed:
                            mod_objs.append(format_callback(obj))
                            obj.full_clean()
                            obj.save()

                    else:
                        # log errors
                        create_obj_errors.append((reader.line_num, str(e)))
                        continue
                except (ObjectDoesNotExist, IntegrityError) as e:
                    create_obj_errors.append((reader.line_num, str(e)))
                    continue

            csv_file.close()
            if create_obj_errors:
                self.message_user(request, "File imported with errors", level=messages.ERROR)
            elif not len(created_objs) and not len(mod_objs):
                self.message_user(request, "File imported: No instances changed", level=messages.WARNING)
            else:
                self.message_user(request, "File imported", level=messages.SUCCESS)
            context.update(
                {
                    "create_complete": True,
                    "created_objects": created_objs,
                    "created_count": len(created_objs),
                    "mod_objects": mod_objs,
                    "mod_count": len(mod_objs),
                    "create_errors": create_obj_errors,
                    "error_count": len(create_obj_errors),
                }
            )
        else:
            # unfilled form
            form = CsvImportForm()
            media = self.media + form.media
            context.update({
                "form": form,
                "media": media
            })

        return TemplateResponse(
            request,
            [
                "admin/%s/%s/csv_form.html" % (app_label, opts.model_name),
                "admin/%s/csv_form.html" % app_label,
                "admin/csv_form.html",
            ],
            context
        )

    actions = ['export_csv_selected']

    @admin.action(description="Export selected")
    def export_csv_selected(self, request, queryset):
        csv_syntax = self._get_csv_syntax()
        field_names = [field.split(':')[0].strip() for field in csv_syntax.split(',')]
        response = HttpResponse(content_type='text/csv')
        timestamp = timezone.now()
        timestamp = timestamp.replace(tzinfo=None)
        response['Content-Disposition'] = 'attachment; filename={}-{}.csv'.format(
            slugify(self.model._meta.model_name), timestamp.isoformat(timespec='minutes')
        )
        writer = csv.writer(response)
        writer.writerow(field_names)
        for obj in queryset.all():
            row = writer.writerow([getattr(obj, field) for field in field_names])
        return response


@admin.register(models.Site)
class SiteAdmin(SuperAdmin):
    search_fields = ('nombre',)
    ordering = ('nombre',)
    list_display = (
        'nombre',
        'brief_description',
    )

    def _get_csv_syntax(self):
        return 'nombre: str, descripcion: str'

    def _build_model_fields(self, row):
        rowlen = len(row)
        if rowlen != 2:
            raise BadRequest(BAD_CSV_MESSAGE)

        (name,
         descr) = row
        return {'nombre': name, 'descripcion': descr}

    @admin.display(description="Descripción")
    def brief_description(self, obj):
        description_lines = obj.descripcion.splitlines()
        if description_lines:
            return description_lines[0]


@admin.register(models.Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    search_fields = ('login',)
    ordering = ('login',)

    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        my_urls = [
            path('import-csv/', self.import_csv, name="%s_%s_importcsv" % info)
        ]
        return my_urls + urls

    def import_csv(self, request):
        self.message_user(request, "Unsupported model", level=messages.WARNING)
        return redirect('..')


@admin.register(models.Telefono)
class TelefonoAdmin(SuperAdmin):
    def _get_csv_syntax(self):
        return 'serie: str, modelo: str, mac: str, nodo: nodo_nombre or empty, usuario: usuario_login or empty'

    def _build_model_fields(self, row):
        rowlen = len(row)
        if rowlen == 5:
            # full format
            (serie,
             modelo,
             mac,
             nodo,
             usuario) = row
            nodo_obj = models.Nodo.objects.get(nombre=nodo) if nodo != '' else None
            usuario_obj = models.Nodo.objects.get(login=usuario) if usuario != '' else None
        elif rowlen == 4:
            # assume missing usuario
            (serie,
             modelo,
             mac,
             nodo) = row
            nodo_obj = models.Nodo.objects.get(nombre=nodo) if nodo != '' else None
            usuario_obj = None
        elif rowlen == 4:
            # bare format
            (serie,
             modelo,
             mac) = row
            nodo_obj = None
            usuario_obj = None
        return {'serie': serie, 'modelo': modelo, 'mac': mac, 'nodo': nodo_obj, 'usuario': usuario_obj}


@admin.register(models.Nodo)
class NodoAdmin(SuperAdmin):
    # list options
    list_display = (
        'nombre',
        'switch',
        'type_port',
        'type',
        'related_devices',
        'brief_description',
    )
    ordering = (
        'nombre',
    )
    search_fields = (
        'nombre',
        'port',
        'switch__name',
    )
    search_help_text = "Search by: nombre, switch, port"
    list_filter = (
        'type',
        ('port', admin.EmptyFieldListFilter),
    )
    # form options
    fields = (
        ('nombre', 'type'),
        ('switch', 'switch_type'),
        'port',
        'description',
    )
    autocomplete_fields = (
        'switch',
    )
    readonly_fields = (
        'switch_type',
    )

    @admin.display(description="Port", ordering='port')
    def type_port(self, obj):
        if obj.switch:
            return f"{obj.switch.tipo.capitalize()} {obj.port}"

    @admin.display(description="tipo")
    def switch_type(self, obj):
        if obj.switch:
            return obj.switch.tipo.capitalize()

    @admin.display(description="Equipos")
    def related_devices(self, obj):
        return ", ".join([
            ipDevice.name for ipDevice in chain([obj.ap], obj.equipo_set.all())
        ])

    @admin.display(description="Descripción")
    def brief_description(self, obj):
        description_lines = obj.description.splitlines()
        if description_lines:
            return description_lines[0]

    def _get_csv_syntax(self):
        return 'nombre: str, switch: switch_nombre, port: port_nombre'

    def _build_model_fields(self, row):
        rowlen = len(row)
        if rowlen != 3:
            raise BadRequest(BAD_CSV_MESSAGE)

        (name,
         switch,
         port) = row
        switch_obj = models.Switch.objects.get(name=switch)
        return {'nombre': name, 'switch': switch_obj, 'port': port}


# ** Polymorphic **

# common display fields
@admin.display(description="switch")
def related_switch(obj):
    if obj.nodo and obj.nodo.switch:
        return obj.nodo.switch


@admin.display(description="port")
def related_port(obj):
    if obj.nodo and obj.nodo.switch:
        return f"{obj.nodo.switch.tipo.capitalize()} {obj.nodo.port}"


class IPDeviceChildAdmin(PolymorphicChildModelAdmin, SuperAdmin):
    """ Base admin class for all ip device models """
    base_model = models.IPDevice
    list_display = (
        'name',
        'ip',
    )
    search_fields = (
        'name',
        'ip',
    )
    search_help_text = "Search by: nombre, ip"

    def get_actions(self, request):
        actions = super().get_actions(request)
        if apps.is_installed('monitoreo'):
            from monitoreo.actions import add_to_watchlist
            actions['add_to_watchlist'] = (
                add_to_watchlist,
                'add_to_watchlist',
                add_to_watchlist.short_description,
            )
        return actions


@admin.register(models.Switch)
class SwitchAdmin(IPDeviceChildAdmin):
    base_model = models.Switch
    show_in_index = True
    list_display = (
        'name',
        'ip',
        'tipo',
        'site',
        'site_description',
    )
    fields = (
        'name',
        'ip',
        ('tipo', 'poe'),
        'site',
        'notas',
    )
    autocomplete_fields = (
        'site',
    )
    list_filter = (
        'tipo',
    )

    def _get_csv_syntax(self):
        return 'name: str, ip: str, tipo: str, poe: bool, site: site_name'

    def _build_model_fields(self, row):
        rowlen = len(row)
        if rowlen != 5:
            raise BadRequest(BAD_CSV_MESSAGE)

        (name,
         ip,
         tipo,
         poe,
         site) = row
        site_obj = models.Site.objects.get(nombre=site)
        type_clean = tipo[:2].upper()
        return {'name': name, 'ip': ip, 'tipo': type_clean, 'poe': bool(strtobool(poe)), 'site': site_obj}

    @admin.display(description="Descripción Site")
    def site_description(self, obj):
        related_site = obj.site
        if related_site:
            description_lines = related_site.descripcion.splitlines()
            if description_lines:
                return description_lines[0]


@admin.register(models.AP)
class APAdmin(IPDeviceChildAdmin):
    base_model = models.AP
    show_in_index = True
    # list view
    list_display = (
        'name',
        'ip',
        'nodo',
        related_switch,
        related_port,
    )
    search_fields = (
        'name',
        'ip',
        'nodo__nombre',
        'nodo__port'
    )
    search_help_text = "Search by: nombre, ip, nodo, port"
    list_filter = (
        ('nodo', admin.EmptyFieldListFilter),
    )
    # form view
    fields = (
        'name',
        'ip',
        ('nodo', related_switch, related_port),
        'notas',
    )
    readonly_fields = (
        related_switch,
        related_port,
    )
    autocomplete_fields = (
        'nodo',
    )

    def _get_csv_syntax(self):
        return 'name: str, ip: str, nodo: nodo_name or empty'

    def _build_model_fields(self, row):
        rowlen = len(row)
        if rowlen == 3:
            # complete format
            (name,
             ip,
             nodo) = row
            nodo_obj = models.Nodo.objects.get(nombre=nodo) if nodo != '' and nodo != '-' else None
        elif rowlen == 2:
            # empty nodo column
            (name,
             ip) = row
            nodo_obj = None
        else:
            raise BadRequest(BAD_CSV_MESSAGE)
        return {'name': name, 'ip': ip, 'nodo': nodo_obj}


@admin.register(models.Equipo)
class EquipoAdmin(IPDeviceChildAdmin):
    base_model = models.Equipo
    show_in_index = True
    # list options
    list_display = (
        'name',
        'ip',
        'nodo',
        related_switch,
        related_port,
        'usuario',
    )
    list_filter = (
        'tipo',
    )
    search_fields = (
        'name',
        'ip',
        'nodo__nombre',
        'usuario__login',
    )
    search_help_text = "Search by: nombre, ip, nodo, usuario login"
    # form options
    fields = (
        ('name', 'tipo'),
        'ip',
        'usuario',
        ('nodo', related_switch, related_port),
        'notas'
    )
    readonly_fields = (
        related_switch,
        related_port,
    )
    radio_fields = {
        'tipo': admin.VERTICAL,
    }
    autocomplete_fields = (
        'usuario',
        'nodo',
    )

    def _get_csv_syntax(self):
        return 'name: str, ip: str, tipo: str, nodo: nodo_name or empty, usuario: usuario_login or empty'

    def _build_model_fields(self, row):
        rowlen = len(row)
        if rowlen == 5:
            # full format
            (name,
             ip,
             tipo,
             nodo,
             usuario) = row
            tipo_clean = tipo[:3].upper()
            nodo_obj = models.Nodo.objects.get(nombre=nodo) if nodo != '' else None
            usuario_obj = models.Usuario.objects.get(login=usuario) if usuario != '' else None
        if rowlen == 4:
            # incomplete format
            # assume missing usuario column
            (name,
             ip,
             tipo,
             nodo) = row
            tipo_clean = tipo[:3].upper()
            nodo_obj = models.Nodo.objects.get(nombre=nodo) if nodo != '' else None
            usuario_obj = None
        elif rowlen == 3:
            # bare format
            (name,
             ip,
             tipo) = row
            tipo_clean = tipo[:3].upper()
            nodo_obj = None
            usuario_obj = None
        else:
            raise BadRequest(BAD_CSV_MESSAGE)
        return {'name': name, 'ip': ip, 'tipo': tipo_clean, 'nodo': nodo_obj, 'usuario': usuario_obj}


@admin.register(models.IPDevice)
class IPDeviceParentAdmin(PolymorphicParentModelAdmin):
    base_model = models.IPDevice
    child_models = (
        models.Switch,
        models.AP,
        models.Equipo,
    )
    list_filter = (PolymorphicChildModelFilter,)
    search_fields = (
        'name',
        'ip',
    )

    def has_module_permission(self, request):
        return False
