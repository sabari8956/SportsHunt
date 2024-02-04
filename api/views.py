from rest_framework.decorators import api_view
from rest_framework.response import Response
from organisers.models import *
from core.models import *
from .serializer import *

@api_view(["GET"])
def index(req):
    objs = User.objects.all()
    serializers = UserSerializer(objs, many=True)
    return Response(serializers.data)