from django import forms
from django.contrib import messages
from django.contrib.admin import helpers
from django.contrib.admin.decorators import action
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _
from django.utils.translation import ngettext

from monitoreo.models import WatchList


class WatchlistForm(forms.Form):
    watchlist = forms.ModelChoiceField(queryset=WatchList.objects.all())


@action(
    permissions=['change'],
    description='Add to watchlist'
)
def add_to_watchlist(modeladmin, request, queryset):
    """
    Action to batch add selected IPDevices to a watchlist.
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label

    # User has chosen list and confirmed addition
    if request.POST.get("post"):
        form = WatchlistForm(request.POST)  # form populated from request
        if form.is_valid():
            related_watchlist = form.cleaned_data['watchlist']
            # do not add duplicates
            registered_devices = related_watchlist.devices.all()
            queryset_new = queryset.exclude(pk__in=registered_devices)  # get only new
            n = queryset_new.count()
            duplicates = queryset.count() - n
            if duplicates:
                msg_skipped = ngettext(
                    'Skipped %(count)d item already in watchlist.',
                    'Skipped %(count)d items already in watchlist.',
                    duplicates
                ) % {
                    'count': duplicates,
                }
            if n:
                related_watchlist.devices.add(*queryset_new)
                related_watchlist.save()
                msg = ngettext(
                    'Successfully added %(count)d item to watchlist: %(watchlist_name)s.',
                    'Successfully added %(count)d items to watchlist: %(watchlist_name)s.',
                    n
                ) % {
                          'count': n,
                          'watchlist_name': related_watchlist.name,
                      }
                if duplicates:
                    modeladmin.message_user(
                        request,
                        " ".join([msg, msg_skipped]),
                        messages.WARNING,
                    )
                else:
                    modeladmin.message_user(
                        request,
                        msg,
                        messages.SUCCESS,
                    )
            else:
                modeladmin.message_user(
                    request,
                    msg_skipped,
                    messages.WARNING,
                )
            return None
    else:
        form = WatchlistForm()

    title = _("Add to watchlist")

    context = {
        **modeladmin.admin_site.each_context(request),
        "title": title,
        "form": form,
        "queryset": queryset,
        "opts": opts,
        "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
        "media": modeladmin.media,
    }

    request.current_app = modeladmin.admin_site.name
    return TemplateResponse(
        request,
        [
            "admin/%s/%s/add_to_watchlist_confirmation.html"
            % (app_label, opts.model_name),
            "admin/%s/add_to_watchlist_confirmation.html" % app_label,
            "admin/add_to_watchlist_confirmation.html",
        ],
        context
    )
