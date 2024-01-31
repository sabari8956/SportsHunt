from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    last_name = None
    first_name = None
    is_organizer = models.BooleanField('organizer status', default=False)
    email = models.EmailField(max_length=254, blank= False, unique=True)
    name = models.CharField('full name', max_length=254)
    
    class Meta:
        permissions = [
            ("organiser", "can create tournaments [ hosts] "),
        ]