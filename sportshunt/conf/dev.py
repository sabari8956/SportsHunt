from .common import *
import os
import razorpay
from dotenv import load_dotenv


load_dotenv()

DEBUG = os.environ.get("DEBUG")
SECRET_KEY = os.environ.get("SECRET_KEY")
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(' ')
RAZOR_KEY_ID = os.environ.get("RAZOR_KEY_ID")
RAZOR_KEY_SECRET = os.environ.get("RAZOR_KEY_SECRET")
CSRF_TRUSTED_ORIGINS = ['https://api.razorpay.com']



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

WSGI_APPLICATION = 'sportshunt.wsgi.application'
ASGI_APPLICATION = 'sportshunt.asgi.application'

# Static files conf
STATIC_URL = 'static/'

# Azure Blob Storage settings
AZURE_ACCOUNT_NAME = os.environ.get("STORAGE_BUCKET_NAME")
AZURE_ACCOUNT_KEY = os.environ.get("STORAGE_BUCKET_KEY")
AZURE_CONTAINER = os.environ.get("STORAGE_BUCKET_CONTAINER")

# Use Azure Blob Storage for media files
DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'
AZURE_CUSTOM_DOMAIN = f'{AZURE_ACCOUNT_NAME}.blob.core.windows.net'
MEDIA_URL = f'https://{AZURE_CUSTOM_DOMAIN}/{AZURE_CONTAINER}/'



STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'media'),
]


LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.hostinger.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get("OTP_MAIL_ADDRESS")
EMAIL_HOST_PASSWORD = os.environ.get("OTP_MAIL_PASSWORD")
