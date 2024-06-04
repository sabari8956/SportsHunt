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
    game = models.ForeignKey('Game', on_delete=models.SET_NULL, related_name='tournament_game', blank= True, null= True , default=1)
    categories = models.ManyToManyField('Category', related_name='tournament_catagory', blank= True)
    venue = models.CharField('Venue', max_length=1024, default="TBA")
    venue_link = models.URLField('Venue Link', max_length=1024, blank= True, null= True)
    onGoing_matches = models.ManyToManyField('Match', related_name='tournament_on_going_matches', blank= True)
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
    # fixture_type =  create a model fr types of fixture and add it here
    fixture = models.ForeignKey('Fixtures', on_delete=models.SET_NULL, related_name="this_fixture", blank= True, null= True)
    winner = models.ForeignKey('Team', on_delete=models.SET_NULL, related_name='category_winner', blank= True, null= True)
    registration = models.BooleanField(default=False)
    def __str__(self) -> str:
        return f"{self.tournament} -> {self.catagory_type}"

class Player(models.Model):
    name = models.CharField('player name', max_length=254)
class Team(models.Model):
    members = models.ManyToManyField(Player, related_name='team_members', blank= True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    payment_method = models.BooleanField(default=True)
    def save(self, *args, **kwargs):
        # if len(self.members.all()) > self.category.team_size:
        #     raise ValidationError("Team size exceeded.")
        super().save(*args, **kwargs)
    
    def name(self):
        return f"{self.members.all()}"
    
    def __str__(self) -> str:
        return f"{self.category.tournament.name}>{self.category.catagory_type} -- {[mem.name for mem in self.members.all()]}"
    
class Match(models.Model):
    match_no = models.IntegerField(null=True, blank=True)
    match_category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='match_category', blank= True, null= True)# have to change blank and null to false
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team1')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team2', null= True, blank= True)
    winner = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='winner', blank=True, null=True)
    loser = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='loser', blank=True, null=True)
    match_state = models.BooleanField(default=False)
    sets = models.IntegerField(default=1)
    sets_scores = models.ManyToManyField('Scoreboard', related_name='match_scoreboard', blank= True)
    current_set = models.ForeignKey('Scoreboard', on_delete=models.SET_NULL, related_name='current_set', blank= True, null= True)
    court = models.ForeignKey('Court', on_delete=models.SET_NULL, related_name='match_court', blank= True, null= True)
    def __str__(self) -> str:
        return f"{self.team1} vs {self.team2}"
    
class Scoreboard(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    team1_score = models.IntegerField(default=0)
    team2_score = models.IntegerField(default=0)
    set_no = models.IntegerField(default=1)
    winner = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='scoreboard_winner', blank=True, null=True)
    set_status = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return f"{self.match} -> {self.team1_score} - {self.team2_score}"

class Fixtures(models.Model):
    status = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="fixtures_category")
    fixture = models.JSONField(blank=True, null=True)
    winners_stages = models.JSONField(blank=True, null=True)
    currentStage = models.IntegerField(default=0)
    currentBracket = models.ManyToManyField(Match, related_name='current_bracket', blank= True)
    currentWinners = models.ManyToManyField(Team, related_name='current_winners', blank= True)
    def __str__(self) -> str:
        return f"{self.category} {self.id}"
    
class Court(models.Model):
    name = models.CharField('court name', max_length=254)
    current_match = models.ForeignKey(Match, on_delete=models.SET_NULL, related_name='current_match', blank= True, null= True)
    tournamet = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    def __str__(self) -> str:
        return f"{self.name}"
