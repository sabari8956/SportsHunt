from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from organisers.models import *
from core.models import *
from .serializer import *
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

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

@login_required
@api_view(["POST"])
def add_to_cart(req):
    data = req.data
    name_fields = [value for key, value in data.lists() if key.startswith('name_')]
    players_instances = [Player.objects.create(name=name[0]) for name in name_fields]
    category_instance = Category.objects.get(id= int(data['category']))
    team_size= category_instance.team_size
    if len(players_instances) != team_size:
        return Response({"error": f"Team size must be {team_size}"}, status=status.HTTP_400_BAD_REQUEST)
    team_instance = Team.objects.create(category= category_instance)
    team_instance.members.set(players_instances)
    
    user_instance = User.objects.get(username= req.user)
    user_instance.cart.add(team_instance)
    messages.add_message(req, messages.SUCCESS, "added to cart successfully")
    return Response({"message": data}, status=status.HTTP_200_OK)

@login_required
@api_view(["POST"])
def checkout(req):
    user_instance = User.objects.get(username= req.user)
    cart_data = user_instance.cart.all()
    for item in cart_data:
        item.category.teams.add(item)
    user_instance.cart.remove(*cart_data)
    return Response({"message": "Checkout was  successfully"}, status=status.HTTP_200_OK)
