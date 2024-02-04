from rest_framework import serializers
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
        