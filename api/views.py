from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from organisers.models import *
from core.models import *
from .serializer import *
from django.shortcuts import redirect
from django.contrib import messages


@api_view(["GET", "POST"])
def OrganisationApi(req):
    if req.method == "POST":
        data = req.data
        serializers = OrganisationSerializer(data= data)
        if serializers.is_valid():
            serializers.save()
            return redirect('core:index')
        messages.add_message(req, messages.WARNING, serializers.errors)
        return redirect("organisers:new_organisation")
    
    data = Organisation.objects.all()
    serializers = OrganisationSerializer(data, many=True)
    # return Response(serializers.data)
    return redirect('core:index')

@api_view(["GET","POST"])
def add_to_cart(req):
    if not req.user.is_authenticated:
        return Response({"error": "You are not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    data = req.data
    print(data)
    messages.add_message(req, messages.WARNING, "added to cart successfully")
    return Response({"message": data}, status=status.HTTP_200_OK)
