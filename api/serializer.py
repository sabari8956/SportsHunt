from rest_framework import serializers
from rest_framework.fields import DateField
from organisers.models import *
from core.models import *

# formating the date field to date-month format
class FormattedDateField(DateField):
    def __init__(self, date_format=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.date_format = date_format

    def to_representation(self, value):
        if value:
            if self.date_format:
                return value.strftime(self.date_format)
            else:
                return value.strftime('%d %b')
        return None

# Serializer for displaying tournament details on the home page
class BasicTournamentSerializer(serializers.ModelSerializer):
    """_summary_
    Used to get basic Tournament details.
    Formated dates
    
    Args:
        serializers (_type_): _description_
        None

    Returns:
        _type_: _description_
        
        returns tournament- 
        name, game, start_date, end_date, venue
    """
    class GameSerializer(serializers.ModelSerializer):
        class Meta:
            model = Game
            fields = ['game_type']
        
        def to_representation(self, instance):
            data = super().to_representation(instance)
            return f"{data['game_type']}"
    
    start_date = FormattedDateField(read_only=True)
    end_date = FormattedDateField(read_only=True, date_format='%d %b %y')
    game = GameSerializer(read_only=True)

    class Meta:
        model = Tournament
        fields = ['name', 'game', 'start_date', 'end_date', 'venue']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return dict(data)

# Serializer for category details
class CategorySerializer(serializers.ModelSerializer):
    """_summary_
    gets the category basic details
    Args:
        serializers (_type_): _description_

    Returns:
        _type_: _description_
    """
    class Meta:
        model = Category
        fields = ['id', 'catagory_type' , 'details', 'price', 'registration']
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data

# Serializer for player name
class PlayerSerializer(serializers.ModelSerializer):
    """_summary_
    Just the name
    Args:
        serializers (_type_): _description_

    Returns:
        _type_: _description_
        name
    """
    class Meta:
        model = Player
        fields = ['name']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data['name']

# Serializer for team details
class TeamSerializer(serializers.ModelSerializer):
    members = PlayerSerializer(many=True, read_only=True)
    class Meta:
        model = Team
        fields = ['id','members']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        name = ''
        l_mem = len(data['members'])
        for i, player in enumerate(data['members']):
            if i == l_mem - 1:
                name += player
            else:
                name += player + ', '
        data['members'] = name
        return dict(data)

# Serializer for match details
class MatchSerializer(serializers.ModelSerializer):
    """_summary_
    serializers the match details
    teams details along with name of the players
    Args:
        serializers (_type_): _description_

    Returns:
        _type_: _description_
    """
    team1 = TeamSerializer(read_only=True)
    team2 = TeamSerializer(read_only=True)
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return dict(data)
    class Meta:
        model = Match
        fields = ['id', 'match_no', 'team1', 'team2', 'winner', 'match_state']

# Serializer for fixture details
class FixtureSerializer(serializers.ModelSerializer):
    currentBracket = MatchSerializer(many=True, read_only=True)
    currentWinners = TeamSerializer(many=True, read_only=True)
    class Meta:
        model = Fixtures
        fields = ['id', 'status', 'currentStage', 'currentBracket', 'currentWinners', 'fixture']
        depth = 1
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return dict(data)

# Serializer for creating tournaments with categories
# currently not using this serializer
class CreateCategoriesTournamentSerializer(serializers.ModelSerializer):
    class CategoriesNameSerializer(serializers.ModelSerializer):
        class Meta:
            model = Category
            fields = ['catagory_type']
        
        def to_representation(self, instance):
            data = super().to_representation(instance)
            return data['catagory_type']
        
    categories = CategoriesNameSerializer(many=True, read_only=True)
    class Meta:
        model = Tournament
        fields = ['categories']
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return dict(data)

# Serializer for organiser's tournament details
class OrgTournamentSerializer(serializers.ModelSerializer):
    class GameSerializer(serializers.ModelSerializer):
        class Meta:
            model = Game
            fields = ['game_type']
        def to_representation(self, instance):
            data = super().to_representation(instance)
            return f"{data['game_type']}"
    
    class OrgSerializer(serializers.ModelSerializer):
        class Meta:
            model = Organisation
            fields = ['name']
        
        def to_representation(self, instance):
            data = super().to_representation(instance)
            return data['name']
    
    start_date = FormattedDateField(read_only=True)
    end_date = FormattedDateField(read_only=True, date_format='%d %b %y')
    game = GameSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    org = OrgSerializer(read_only=True)

    class Meta:
        model = Tournament
        fields = ['name', 'game', 'start_date', 'end_date', 'venue', 'categories', 'org']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return dict(data)

# Serializer for category view with fixture and teams
class CategoryViewSerializer(serializers.ModelSerializer):
    fixture = FixtureSerializer(read_only=True)
    teams = TeamSerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'catagory_type', 'details', 'price', 'fixture', 'teams', 'registration', 'winner']
        depth = 1

# Serializer for ongoing matches in a tournament
class TournamentOngoingMatchesSerializer(serializers.ModelSerializer):
    onGoing_matches = MatchSerializer(many=True, read_only=True)
    class Meta:
        model = Tournament
        fields = ['name', 'onGoing_matches']
        depth = 1 

# Serializer for match data and scoreboards
class MatchDataSerializer(serializers.ModelSerializer):
    
    class ScoreboardSerializer(serializers.ModelSerializer):
        winner = TeamSerializer(read_only=True)

        class Meta:
            model = Scoreboard
            fields = ['team1_score', 'team2_score', 'set_no', 'winner', 'set_status']
            depth = 1

        def to_representation(self, instance):
            data = super().to_representation(instance)
            return dict(data)
        
    class CategorySerializer(serializers.ModelSerializer):
        class Meta:
            model = Category
            fields = ['id', 'catagory_type']

        def to_representation(self, instance):
            data = super().to_representation(instance)
            return dict(data)
    
    team1 = TeamSerializer(read_only=True)
    team2 = TeamSerializer(read_only=True)
    sets_scores = ScoreboardSerializer(many=True, read_only=True)
    current_set = ScoreboardSerializer(read_only=True)
    match_category = CategorySerializer(read_only=True)

    class Meta:
        model = Match
        fields = ['id', 'match_no','match_state' ,'team1', 'team2', 'sets', 'sets_scores', 'court', 'current_set', 'match_category']
        
        

class decoratorOrgSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ['admin', 'mods']
    
    
class decoratorTournamentHostValidator(serializers.ModelSerializer):

    org = decoratorOrgSerializer(read_only=True)
    class Meta:
        model = Tournament
        fields = ['id','org', 'mods']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return dict(data)
    
    
# just for now, core org view, OrganisationApi api.
class orgSerlializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = '__all__'
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return dict(data)