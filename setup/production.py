import os

from .base import *  # noqa

DEBUG = False

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("A variável de ambiente DJANGO_SECRET_KEY não foi definida.")

ALLOWED_HOSTS = ['seu-dominio.com', 'www.seu-dominio.com']
