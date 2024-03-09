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
        if self.pk:
            if Tournament.objects.filter(name=self.name).exclude(pk=self.pk).exists():
                raise ValidationError("Tournament name already exists.")
        else:
            if Tournament.objects.filter(name=self.name).exists():
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
    team_size = models.IntegerField(default=1)
    teams = models.ManyToManyField('Team', related_name='category_team', blank= True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    fixture = models.ManyToManyField('Match', related_name='category_fixture', blank= True)
    
    def __str__(self) -> str:
        return f"{self.tournament} -> {self.catagory_type}"
    
class Team(models.Model):
    members = models.ManyToManyField(User, related_name='team_members', blank= True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    def save(self, *args, **kwargs):
        # if len(self.members.all()) > self.category.team_size:
        #     raise ValidationError("Team size exceeded.")
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.category.tournament.name}>{self.category.catagory_type} -- {[mem.username for mem in self.members.all()]}"
    
class Match(models.Model):
    match_no = models.IntegerField(null=True, blank=True)
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team1')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team2')
    winner = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='winner', blank=True, null=True)
    loser = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='loser', blank=True, null=True)
    match_state = models.BooleanField(default=False)
    sets = models.IntegerField(default=1)
    # sets_scores = TODO later
    
    def __str__(self) -> str:
        return f"{self.team1} vs {self.team2}"

