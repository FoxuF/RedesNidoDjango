"""
Django shared settings for RedesDjango project.
"""
import os
import configparser
from pathlib import Path
import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType

BASE_DIR = Path(__file__).resolve().parent.parent
SECRETS_DIR = BASE_DIR / 'secrets'

# SECURITY WARNING: keep the secret key used in production secret!
# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'todos_los_nodos.apps.TodosLosNodosConfig',
    'monitoreo.apps.MonitoreoConfig',
    'cowork.apps.CoworkConfig',
    'django_q',
    'polymorphic',
    'RedesDjango.apps.CustomAdminConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]


JAZZMIN_SETTINGS = {
    'site_title': 'Lumu',
    'site_header': 'Lumu',
    'site_logo': 'img/LogoUP.png',
    'site_brand':'Lumu',
    'login_logo':'img/LogoUP.p',
    'welcome_sign': 'Sign In',
    'copyright':'Sitio de Transformacion Digital creditos al Brunos y al Foxu Alumnos de la Universidad Panamericana ',
    'order_with_respect_to':['auth','todos_los_nodos','monitoreo','cowork','django_q'],
    "custom_css": "css/bootstrap-dark.css",
    'icons':{
        'auth.user': 'fas fa-user',
        'auth.Group': 'fas fa-users',

        'todos_los_nodos.ap':'fas fa-wifi',
        'todos_los_nodos.equipo':'fas fa-desktop',
        'todos_los_nodos.nodo':'fas fa-signal',
        'todos_los_nodos.site':'fas fa-network-wired',
        'todos_los_nodos.switch':'fas fa-ethernet',
        'todos_los_nodos.telefono':'fas fa-phone',
        'todos_los_nodos.usuario':'fas fa-user-cog',

        'monitoreo.subscriber':'fas fa-users',
        'monitoreo.watchlist':'fas fa-eye',

        'cowork.cowork': 'fas fa-building',

        'django_q.failed_task':'fas fa-user',
        'django_q.queue_task':'fas fa-user',
        'django_q.schedule':'fas fa-calendar',
        'django_q.success':'fas fa-check'

    },
    'topmenu_links':[
        {'app':'todos_los_nodos'},
        {'model':'todos_los_nodos.Nodo'}
    ],
    "changeform_format": "horizontal_tabs",
    'show_ui_builder':True

}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-warning",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": True,
    "sidebar_fixed": False,
    "sidebar": "sidebar-light-dark",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "darkly",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-outline-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

STATICFILES_DIRS = [os.path.join(BASE_DIR,'static')]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'RedesDjango.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'RedesDjango.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Mexico_City'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

# static files
STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django Q
Q_CLUSTER = {
    'name': 'QCluster',
    'sync': True,
    'workers': 1,
    'orm': 'default',
    'timeout': 90,
    'retry': 120,
    'queue_limit': 50,
}

# SMTP Confing
iniParser = configparser.ConfigParser()
iniParser.read(SECRETS_DIR / 'conf.ini', encoding='utf-8')
EMAIL_HOST = iniParser.get('MAIL', 'host')
EMAIL_PORT = iniParser.getint('MAIL', 'port', fallback=25)
DEFAULT_FROM_EMAIL = iniParser.get('MAIL', 'from_mail')

# LDAP AUTH
# TODO make setup.py to download and install python-ldap
# install python-ldap manually for now
# from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#python-ldap
AUTHENTICATION_BACKENDS = [
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
]
AUTH_LDAP_SERVER_URI = "ldap://{}".format(iniParser.get('LDAP', 'server'))
AUTH_LDAP_BIND_DN = iniParser.get('LDAP', 'bind_dn', fallback="")
AUTH_LDAP_BIND_PASSWORD = iniParser.get('LDAP', 'bind_password', fallback="")
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    iniParser.get('LDAP', 'user_search_base', fallback=""),
    ldap.SCOPE_SUBTREE,
    "(&(sAMAccountName=%(user)s)(objectCategory=Person))"
)
# group stuff (not optional)
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    iniParser.get('LDAP', 'group_base'),
    ldap.SCOPE_SUBTREE,
    "(objectClass=group)"
)
AUTH_LDAP_GROUP_TYPE = GroupOfNamesType()
AUTH_LDAP_REQUIRE_GROUP = iniParser.get('LDAP', 'require_group')
# disable referrals
AUTH_LDAP_CONNECTION_OPTIONS = {
    ldap.OPT_REFERRALS: 0,
}
