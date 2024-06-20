"""
WSGI config for dentalhealthyclinic project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""
from whitenoise import WhiteNoise

import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dentalhealthyclinic.settings')

application = get_wsgi_application()
application = WhiteNoise(application, root=os.path.join(BASE_DIR, 'staticfiles'))

