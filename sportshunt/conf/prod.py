from .common import *
import os

from dotenv import load_dotenv
load_dotenv()

DEBUG = False
SECRET_KEY = os.environ.get("SECRET_KEY")
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(' ')
RAZOR_KEY_ID = os.environ.get("RAZOR_KEY_ID")
RAZOR_KEY_SECRET = os.environ.get("RAZOR_KEY_SECRET")
CSRF_TRUSTED_ORIGINS = ['https://api.razorpay.com', 'https://sportshunt.azurewebsites.net', 'https://sportshunt.in']



WSGI_APPLICATION = 'sportshunt.wsgi_prod.application'
ASGI_APPLICATION = 'sportshunt.asgi.prod.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.prod.sqlite3',
    }
}

# Static files conf
STATIC_URL = 'static/'


STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'media'),
]

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.hostinger.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get("OTP_MAIL_ADDRESS")
EMAIL_HOST_PASSWORD = os.environ.get("OTP_MAIL_PASSWORD")

# Azure Blob Storage settings
AZURE_ACCOUNT_NAME = os.environ.get("STORAGE_BUCKET_NAME")
AZURE_ACCOUNT_KEY = os.environ.get("STORAGE_BUCKET_KEY")
AZURE_CONTAINER = os.environ.get("STORAGE_BUCKET_CONTAINER")

# Use Azure Blob Storage for media files
DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'
AZURE_CUSTOM_DOMAIN = f'{AZURE_ACCOUNT_NAME}.blob.core.windows.net'
MEDIA_URL = f'https://{AZURE_CUSTOM_DOMAIN}/{AZURE_CONTAINER}/'


# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

# SECURE_HSTS_SECONDS = 31536000 
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
