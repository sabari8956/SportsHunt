from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('new_org', organisation_creation_form, name="new_organisation"),
    path('my_orgs', organisation_page, name="orgs"),
    path('new_tournament', tournament_creation_form, name="new_tournament"),
    path('tournament/<str:tournament_name>/',org_tournament_view , name="tournament"),
    path('tournament/<str:tournament_name>/new_category', create_categories, name="create_categories"),
    path('tournament/<str:tournament_name>/<str:category_name>', category_view, name='category'),

]

