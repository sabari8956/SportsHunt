from rest_framework.decorators import api_view
from rest_framework.response import Response
from organisers.models import *
from core.models import *
from .serializer import *
from django.shortcuts import redirect

@api_view(["GET", "POST"])
def OrganisationApi(req):
    if req.method == "POST":
        data = req.data
        serializers = OrganisationSerializer(data= data)
        if serializers.is_valid():
            serializers.save()
            return redirect('core:index')
        return Response(serializers.errors)
    
    data = Organisation.objects.all()
    serializers = OrganisationSerializer(data, many=True)
    return Response(serializers.data)