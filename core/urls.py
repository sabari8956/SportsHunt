from django.urls import path
from .views import *

urlpatterns = [
    path("", index, name="index" ),
    path("login/", login_view, name="login"),
    path('logout/', logout_view, name="logout"),
    path('register/', register_view, name="register"),
    path('verify_account/', verifyMail_view, name="verifyMail"),
    path('cart/', cart_view, name="cart"),
    path('checkout/', checkout, name="checkout"),
    path('organisation/<str:org_name>/', organisation_view, name="organisation"),
    path('tournament/<str:tournament_name>/', organisation_tournament_view, name='organisation_tournament'),
]
