"""WSGI config for the BuildLog project."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "buildlog.settings")

application = get_wsgi_application()
