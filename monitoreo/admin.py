import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
from django.utils.text import slugify

from monitoreo.models import Subscriber, WatchList


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    search_fields = (
        'email',
    )


class IPDeviceInline(admin.TabularInline):
    model = WatchList.devices.through
    extra = 0
    fields = (
        'ipdevice',
        'device_ip',
        'device_alive',
        'device_lastalive',
    )
    readonly_fields = (
        'device_ip',
        'device_alive',
        'device_lastalive',
    )
    autocomplete_fields = (
        'ipdevice',
    )
    verbose_name = "Device"

    @admin.display(description="IP")
    def device_ip(self, obj):
        return obj.ipdevice.ip

    @admin.display(boolean=True, description="alive")
    def device_alive(self, obj):
        return obj.ipdevice.alive

    @admin.display(description="last alive")
    def device_lastalive(self, obj):
        return obj.ipdevice.lastAlive

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        deviceField = formset.form.base_fields["ipdevice"]
        deviceField.widget.can_add_related = False
        deviceField.widget.can_change_related = False
        deviceField.widget.can_delete_related = False
        return formset


@admin.register(WatchList)
class WatchListAdmin(admin.ModelAdmin):
    change_form_template = "admin/changeform_export.html"
    list_display = (
        'name',
        'device_number',
        'active',
        'recurrence',
        'next_run',
    )
    list_filter = (
        "active",
    )
    fields = (
        ('name', 'active'),
        ('recurrence', 'next_run'),
        'subscribers',
    )
    readonly_fields = (
        'next_run',
    )
    autocomplete_fields = (
        'subscribers',
    )
    inlines = (
        IPDeviceInline,
    )
    actions = (
        "make_active",
        "make_inactive",
    )
    save_on_top = True

    @admin.display(description="Devices")
    def device_number(self, obj):
        return obj.devices.count()

    @admin.display(description="next scheduled run", empty_value="N/A")
    def next_run(self, obj):
        if obj.schedule is not None:
            return f"{obj.schedule.next_run}"
        else:
            return None

    @admin.action(description="Make active")
    def make_active(self, request, queryset):
        queryset.update(active=True)
        for item in queryset:
            item.save()

    @admin.action(description="Make inactive")
    def make_inactive(self, request, queryset):
        queryset.update(active=False)
        for item in queryset:
            item.save()

    def response_change(self, request, obj):
        if "_export-csv" in request.POST:
            FIELD_NAMES = ('name', 'ip')
            response = HttpResponse(content_type='text/csv')
            timestamp = timezone.now()
            timestamp = timestamp.replace(tzinfo=None)
            response['Content-Disposition'] = 'attachment; filename={}-{}.csv'.format(
                slugify(obj), timestamp.isoformat(timespec='minutes')
            )
            writer = csv.writer(response)
            writer.writerow(FIELD_NAMES)
            for ipObj in obj.devices.all():
                row = writer.writerow([getattr(ipObj, field) for field in FIELD_NAMES])
            return response
        return super().response_change(request, obj)
