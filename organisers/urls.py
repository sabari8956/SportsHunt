from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('new_org', organisation_creation_form, name="new_organisation"),
]

