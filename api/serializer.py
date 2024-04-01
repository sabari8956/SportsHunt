from rest_framework import serializers
from rest_framework.fields import DateField
from organisers.models import *
from core.models import *

class OrganisationSerializer(serializers.ModelSerializer):
    admin = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model = Organisation
        fields = '__all__'
        depth = 1
        

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = '__all__'


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

class TournamentSerializer(serializers.ModelSerializer):
    start_date = FormattedDateField(read_only=True)
    end_date = FormattedDateField(read_only=True, date_format='%d %b %y')

    class Meta:
        model = Tournament
        fields = '__all__'
        depth = 3
        
class cartSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['cart']
        depth = 1
        
class fixtureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fixtures
        fields = '__all__'
        depth = 1
        
class matchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = '__all__'
        depth = 2
        

class categoryViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        depth = 1

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['name']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return dict(data)
class TeamSerializer(serializers.ModelSerializer):
    members = PlayerSerializer(many=True, read_only=True)
    class Meta:
        model = Team
        fields = ['id', 'members']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return dict(data)
class MatchSerializer(serializers.ModelSerializer):
    team1 = TeamSerializer(read_only=True)
    team2 = TeamSerializer(read_only=True)

    class Meta:
        model = Match
        fields = ['id', 'match_no', 'team1', 'team2', 'winner', 'match_state']
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return dict(data)

class FixtureSerializer(serializers.ModelSerializer):
    currentBracket = MatchSerializer(many=True, read_only=True)
    currentWinners = TeamSerializer(many=True, read_only=True)

    class Meta:
        model = Fixtures
        fields = ['id', 'status', 'category', 'currentStage', 'currentBracket', 'currentWinners']
        # depth = 1
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return dict(data)