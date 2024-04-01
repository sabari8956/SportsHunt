from django.urls import path
from .views import *

urlpatterns = [
    path('', OrganisationApi, name="org"),
    path('add_to_cart/', add_to_cart, name="add_to_cart"),
    path('checkout/', checkout, name="checkout"), # after payment we will need to validate the payment[signature] and then add the teams to the tournament
    path('<str:tournament_name>/<str:category_name>/view_fixture/', view_fixture, name="view_fixture"),
    path('<str:tournament_name>/<str:category_name>/create_fixture/', create_fixture, name="create_fixture"),
    path('<str:tournament_name>/<str:category_name>/add_winner/', update_winner, name="add_winner"),
]