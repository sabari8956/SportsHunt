from django.urls import path
from .views import *

urlpatterns = [
    path('', OrganisationApi, name="org"),
]