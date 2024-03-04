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
        self.name = self.name.lower().replace(" ", "_")
        if self.name in [org.name for org in Organisation.objects.all()]:
            raise ValidationError("Organisation name already exists.")
        if not self.admin.is_organiser:
            raise ValidationError("Only organisers can create an organisation.")
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.name}"
    
class Tournament(models.Model):
    name = models.CharField('tournament name', max_length=254, unique=True)
    org = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    mods = models.ManyToManyField(User, related_name='tournament_mod', blank= True)
    start_date = models.DateField()
    end_date = models.DateField()
    game = models.ForeignKey('Game', on_delete=models.CASCADE)
    categories = models.ManyToManyField('Category', related_name='tournament_catagory', blank= True)
    
    def save(self, *args, **kwargs):
        self.name = self.name.lower().replace(" ", "_")
        if self.name in [tour.name for tour in Tournament.objects.all()]:
            raise ValidationError("Tournament name already exists.")
        
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.name}"
    
class Game(models.Model):
    game_type = models.CharField('game type', max_length=254)
    default_categories = models.ManyToManyField('Category', related_name='game_catagory', blank= True)
    
    def __str__(self) -> str:
        return f"{self.game_type}"

class Category(models.Model):
    catagory_type = models.CharField('catogory type', max_length=254)
    details = models.CharField('catogory details', max_length=254, blank= True)
    max_age = models.IntegerField()
    price = models.IntegerField(default=0)
    
    def __str__(self) -> str:
        return f"{self.catagory_type}"