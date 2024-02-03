from django.db import models
from core.models import User
from django.core.validators import RegexValidator

# Create your models here.
class Organisation(models.Model):
    name = models.CharField('organisation name', max_length=254, unique=True)
    mail = models.EmailField(max_length=254, blank=False)
    wh_num = models.CharField('whatsapp number', max_length=10, validators=[RegexValidator(regex=r"^[0-9]{10}$")])
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    mods = models.ManyToManyField(User, related_name='organisation_mod')