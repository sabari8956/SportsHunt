from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    last_name = None
    first_name = None
    is_organiser = models.BooleanField('organizer status', default=False)
    email = models.EmailField(max_length=254, blank= False, unique=True)
    name = models.CharField('full name', max_length=254)
    cart = models.ManyToManyField('organisers.Team',blank=True)
    otp = models.CharField(max_length=4, blank=True, null=True)
    otpTime = models.DateTimeField(blank=True, null=True)
    verified = models.BooleanField(default=False)