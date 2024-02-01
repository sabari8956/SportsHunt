from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index')
]

app_name = "organisers"