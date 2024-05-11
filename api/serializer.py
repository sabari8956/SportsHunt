from rest_framework import serializers
from rest_framework.fields import DateField
from organisers.models import *
from core.models import *

# class OrganisationSerializer(serializers.ModelSerializer):
#     admin = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
#     class Meta:
#         model = Organisation
#         fields = '__all__'
#         depth = 1
        

# class UserSerializer(serializers.ModelSerializer):
    
#     class Meta:
#         model = User
#         fields = '__all__'


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

# class TournamentSerializer(serializers.ModelSerializer):
#     start_date = FormattedDateField(read_only=True)
#     end_date = FormattedDateField(read_only=True, date_format='%d %b %y')

#     class Meta:
#         model = Tournament
#         fields = '__all__'
#         depth = 3

# NEED TO REWRITE ALL THE SERIALIZERS
# IMP AS HELL, REGULATE ALL DATA.
# class Tournament_Serializer(serializers.ModelSerializer):
#     start_date = FormattedDateField(read_only=True)
#     end_date = FormattedDateField(read_only=True, date_format='%d %b %y')
#     org_name = serializers.CharField(source='org.name', read_only=True)
#     game_type = serializers.CharField(source='game.game_type', read_only=True)
#     onGoing_matches = 
#     class Meta:
#         model = Tournament
#         fields = ['id', 'name', 'start_date', 'end_date', 'venue', 'org_name', 'game_type', 'onGoing_matches']
# class cartSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['cart']
#         depth = 1
        
# class fixtureSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Fixtures
#         fields = '__all__'
#         depth = 1
        
# class matchSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Match
#         fields = '__all__'
#         depth = 2
        

# class categoryViewSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = '__all__'
#         depth = 1

# class TeamSerializer(serializers.ModelSerializer):
#     members = PlayerSerializer(many=True, read_only=True)
#     class Meta:
#         model = Team
#         fields = ['id', 'members']

#     def to_representation(self, instance):
#         data = super().to_representation(instance)
#         return dict(data)
# class MatchSerializer(serializers.ModelSerializer):
#     team1 = TeamSerializer(read_only=True)
#     team2 = TeamSerializer(read_only=True)

#     class Meta:
#         model = Match
#         fields = ['id', 'match_no', 'team1', 'team2', 'winner', 'match_state']
#     def to_representation(self, instance):
#         data = super().to_representation(instance)
#         return dict(data)

# class FixtureSerializer(serializers.ModelSerializer):
#     currentBracket = MatchSerializer(many=True, read_only=True)
#     currentWinners = TeamSerializer(many=True, read_only=True)

#     class Meta:
#         model = Fixtures
#         fields = ['id', 'status', 'category', 'currentStage', 'currentBracket', 'currentWinners']
        
#         # depth = 1
#     def to_representation(self, instance):
#         data = super().to_representation(instance)
#         return dict(data)
    

# class MatchDataSerializer(serializers.ModelSerializer):
#     class TeamSerializer(serializers.ModelSerializer):
#         members = PlayerSerializer(many=True, read_only=True)

#         class Meta:
#             model = Team
#             fields = ['id', 'members']

#         def to_representation(self, instance):
#             data = super().to_representation(instance)
#             players = ', '.join(player for player in data['members'])
#             data['members'] = players
#             return dict(data)

#     class ScoreboardSerializer(serializers.ModelSerializer):
#         winner = TeamSerializer(read_only=True)

#         class Meta:
#             model = Scoreboard
#             fields = ['team1_score', 'team2_score', 'set_no', 'winner', 'set_status']
#             depth = 1

#         def to_representation(self, instance):
#             data = super().to_representation(instance)
#             return dict(data)

#     class CategorySerializer(serializers.ModelSerializer):
#         class Meta:
#             model = Category
#             fields = ['id', 'catagory_type']

#         def to_representation(self, instance):
#             data = super().to_representation(instance)
#             return dict(data)
    
#     team1 = TeamSerializer(read_only=True)
#     team2 = TeamSerializer(read_only=True)
#     sets_scores = ScoreboardSerializer(many=True, read_only=True)
#     current_set = ScoreboardSerializer(read_only=True)
#     match_category = CategorySerializer(read_only=True)

#     class Meta:
#         model = Match
#         fields = ['id', 'match_no','match_state' ,'team1', 'team2', 'sets', 'sets_scores', 'court', 'current_set', 'match_category']
#         depth = 1


# New Serializer
class home_TournamentSerializer(serializers.ModelSerializer):
    class gameSerializer(serializers.ModelSerializer):
        class Meta:
            model = Game
            fields = ['game_type']
        
        def to_representation(self, instance):
            data = super().to_representation(instance)
            return f"{data['game_type']}"
    
    start_date = FormattedDateField(read_only=True)
    end_date = FormattedDateField(read_only=True, date_format='%d %b %y')
    game = gameSerializer(read_only=True)

    class Meta:
        model = Tournament
        fields = ['name', 'game', 'start_date', 'end_date', 'venue']
    
    def to_representation(self, instance):
            data = super().to_representation(instance)
            return dict(data)
 
class categorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['catagory_type' , 'details', 'price']
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        print(f"{data}")
        return data
class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['name']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data['name']

class TeamSerializer(serializers.ModelSerializer):
    members = PlayerSerializer(many=True, read_only=True)
    class Meta:
        model = Team
        fields = ['id','members']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return dict(data)

class MatchSerializer(serializers.ModelSerializer):
    team1 = TeamSerializer(read_only=True)
    team2 = TeamSerializer(read_only=True)
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return dict(data)
    class Meta:
        model = Match
        fields = ['id', 'match_no', 'team1', 'team2', 'winner', 'match_state']

class FixtureSerializer(serializers.ModelSerializer):
    currentBracket = MatchSerializer(many=True, read_only=True)
    currentWinners = TeamSerializer(many=True, read_only=True)
    class Meta:
        model = Fixtures
        fields = ['id', 'status', 'currentStage', 'currentBracket', 'currentWinners']
        depth = 1
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return dict(data)


class create_categories_TournamentSerializer(serializers.ModelSerializer):

    categories = categorySerializer(many=True, read_only=True)
    class Meta:
        model = Tournament
        fields = ['id', 'name', 'categories']    
    def to_representation(self, instance):
            data = super().to_representation(instance)
            return dict(data)

class org_tournamentSerializer(serializers.ModelSerializer):
    class gameSerializer(serializers.ModelSerializer):
        class Meta:
            model = Game
            fields = ['game_type']
        def to_representation(self, instance):
            data = super().to_representation(instance)
            return f"{data['game_type']}"
    
    class orgSerializer(serializers.ModelSerializer):
        class Meta:
            model = Organisation
            fields = ['name']
        
        def to_representation(self, instance):
            data = super().to_representation(instance)
            return data['name']
    
    start_date = FormattedDateField(read_only=True)
    end_date = FormattedDateField(read_only=True, date_format='%d %b %y')
    game = gameSerializer(read_only=True)
    categories = categorySerializer(many=True, read_only=True)
    org = orgSerializer(read_only=True)

    class Meta:
        model = Tournament
        fields = ['name', 'game', 'start_date', 'end_date', 'venue', 'categories', 'org']
    
    def to_representation(self, instance):
            data = super().to_representation(instance)
            return dict(data)

class categoryView_Serializer(serializers.ModelSerializer):
    fixture = FixtureSerializer(read_only=True)
    teams = TeamSerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['catagory_type', 'details', 'price', 'fixture', 'teams']
        depth = 1
    
class Tournament_ongoingMatches_Serializer(serializers.ModelSerializer):
    
    onGoing_matches = MatchSerializer(many=True, read_only=True)
    class Meta:
        model = Tournament
        fields = ['name', 'onGoing_matches']
        depth = 1 
        

    
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