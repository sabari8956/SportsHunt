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