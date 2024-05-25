from django.urls import path
from .views import *

urlpatterns = [
    path('', OrganisationApi, name="org"),
    path('add_to_cart/', add_to_cart, name="add_to_cart"),
    path('create_order/', create_order, name="create_order"),
    # path('payment/', handle_payment, name="payment"),
    # path('checkout/', checkout, name="checkout"),# after payment we will need to validate the payment[signature] and then add the teams to the tournament
    path('declare_winner/', declare_match_winner, name='declare_winner'),
    path('increment_score/<int:match_id>/<int:team_id>/', increment_score, name='increment_score'),
    path('decrement_score/<int:match_id>/<int:team_id>/', decrement_score, name='decrement_score'),
    path('get_fixture_json/<int:fixture_id>/', fixtureJSON, name='get_fixture_json'),
    path('<str:tournament_name>/<str:category_name>/view_fixture/', view_fixture, name="view_fixture"),
    path('<str:tournament_name>/<str:category_name>/create_fixture/', create_fixture, name="create_fixture"),
    path('<str:tournament_name>/<str:category_name>/add_winner/', update_winner, name="add_winner"),
    path('<str:tournament_name>/<str:category_name>/schedule_match/', schedule_match, name="schedule_match"),
]