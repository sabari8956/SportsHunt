from django.db import models
from core.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

# Create your models here.
class Organisation(models.Model):
    name = models.CharField('organisation name', max_length=254, unique=True)
    mail = models.EmailField(max_length=254, blank=False)
    wh_num = models.CharField('whatsapp number', max_length=10, validators=[RegexValidator(regex=r"^[0-9]{10}$")])
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    mods = models.ManyToManyField(User, related_name='organisation_mod', blank= True)
    
    def save(self, *args, **kwargs):
        if not self.admin.is_organiser:
            raise ValidationError("Only organisers can create an organisation.")
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.name}"