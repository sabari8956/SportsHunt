from django.urls import path
from .views import *

urlpatterns = [
    path('add_to_cart/', add_to_cart, name="add_to_cart"), 
    path('create_order/', create_order, name="create_order"),
    path('offline_register/', register_player, name="offline_register"),
    path('declare_winner/', declare_match_winner, name='declare_winner'),
    path('schedule_match/', schedule_match, name="schedule_match"),
    path('increment_score/<int:match_id>/<int:team_id>/', increment_score, name='increment_score'),
    path('decrement_score/<int:match_id>/<int:team_id>/', decrement_score, name='decrement_score'),
    path('get_fixture_json/<int:fixture_id>/', fixtureJSON, name='get_fixture_json'),
    path('close_registration/<str:tournament_name>/', close_registration, name="close_registration"),
    path('close_registration/<str:tournament_name>/<str:category_name>/', close_registration, name="close_registration"),
    path('<str:tournament_name>/<str:category_name>/view_fixture/', view_fixture, name="view_fixture"),
    path('<str:tournament_name>/<str:category_name>/create_fixture/', create_fixture, name="create_fixture"),
    path('<str:tournament_name>/<str:category_name>/add_winner/', update_winner, name="add_winner"),

]