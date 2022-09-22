from django.contrib.admin.apps import AdminConfig


def populate_receiver(user, ldap_user, **kwargs):
    from django.db.models import Q
    from django.contrib.auth.models import Group  # weird stuff
    # all valid users are staff
    user.is_staff = True
    user.save()  # user needs to exist ID before adding many-to-many
    try:
        # apply existing groups
        # AUTH_LDAP_FIND_GROUP_PERMS not working??
        # case-insensitive in
        q = Q()
        for group_name in ldap_user.group_names:
            q = q | Q(name__iexact=group_name)
        groupset = Group.objects.filter(q)
        # add groups to user
        user.groups.add(*groupset)
    except Exception as e:
        # delete instance if failure in groups
        user.delete()
        raise e  # continue with exception


class CustomAdminConfig(AdminConfig):
    def ready(self):
        from django_auth_ldap.backend import populate_user  # fails if import on module
        populate_user.connect(populate_receiver)
        super().ready()
