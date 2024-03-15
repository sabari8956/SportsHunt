from django.urls import path
from .views import *

urlpatterns = [
    path('', OrganisationApi, name="org"),
    path('add_to_cart/', add_to_cart, name="add_to_cart"),
]