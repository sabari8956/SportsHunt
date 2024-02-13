from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('new_org', organisation_creation_form, name="new_organisation"),
    path('my_orgs', organisation_page, name="orgs"),
    path('new_tournament', tournament_creation_form, name="new_tournament"),
]

