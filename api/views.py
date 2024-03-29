from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from organisers.models import *
from core.models import *
from .serializer import *
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from organisers.utils import *
from organisers.decorators import host_required

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
@api_view(["GET","POST"])
def checkout(req):
    user_instance = User.objects.get(username= req.user)
    cart_data = user_instance.cart.all()
    for item in cart_data:
        item.category.teams.add(item)
    user_instance.cart.remove(*cart_data)
    return Response({"message": "Checkout was  successfully"}, status=status.HTTP_200_OK)

@host_required
@api_view(["GET", "POST"])
def create_fixture(req, tournament_name, category_name):
    if not (Tournament.objects.filter(name= tournament_name).exists() and category_name in Tournament.objects.get(name= tournament_name).categories.all().values_list('catagory_type', flat=True)):
        return Response({"error": "Tournament or Category not found"}, status=status.HTTP_404_NOT_FOUND)

    tournament_instance = Tournament.objects.get(name= tournament_name)
    category_instance = tournament_instance.categories.get(catagory_type= category_name)
    if category_instance.fixture:
        return Response({"error": "Fixture already exists"}, status=status.HTTP_400_BAD_REQUEST)
    fixture_instance = Fixtures.objects.create(
        category= category_instance,
        )
    fixture = knockoutFixtureGenerator()
    response = fixture.initialBracket(fixture_instance.id)
    if not response:
        return Response({"error": "Error creating fixture"}, status=status.HTTP_400_BAD_REQUEST)
    return Response({
        "id": fixture_instance.id,
        "fixture_matches": [ match.id for match in fixture_instance.currentBracket.all()],
        "message": "Fixture created successfully",
        },
       status=status.HTTP_200_OK)    
    
@host_required
@api_view(["GET", "POST"])
def update_winner(req, tournament_name, category_name, winner_team_id):
    if not (Tournament.objects.filter(name= tournament_name).exists() and category_name in Tournament.objects.get(name= tournament_name).categories.all().values_list('catagory_type', flat=True)):
        return Response({"error": "Tournament or Category not found"}, status=status.HTTP_404_NOT_FOUND)

    tournament_instance = Tournament.objects.get(name= tournament_name)
    category_instance = tournament_instance.categories.get(catagory_type= category_name)
    fixture_instance = category_instance.fixture
    if not fixture_instance:
        return Response({"error": "Fixture not found"}, status=status.HTTP_404_NOT_FOUND)
    status_ = knockoutFixtureGenerator().add_winners(fixture_instance.id, winner_team_id)
    return Response({"message": status_}, status=status.HTTP_200_OK)

@host_required
@api_view(["GET"])
def view_fixture(req, tournament_name, category_name):
    if not (Tournament.objects.filter(name= tournament_name).exists() and category_name in Tournament.objects.get(name= tournament_name).categories.all().values_list('catagory_type', flat=True)):
        return Response({"error": "Tournament or Category not found"}, status=status.HTTP_404_NOT_FOUND)

    tournament_instance = Tournament.objects.get(name= tournament_name)
    category_instance = tournament_instance.categories.get(catagory_type= category_name)
    fixture_instance = category_instance.fixture
    if not fixture_instance:
        return Response({"error": "Fixture not found"}, status=status.HTTP_404_NOT_FOUND)
    serializers = fixtureSerializer(fixture_instance)
    if len(serializers.data['currentBracket']) == 0 and len(serializers.data['currentWinners']) == 1:
        return Response({"message": "Fixture completed", "winner":serializers.data['currentWinners'][0]}, status=status.HTTP_200_OK)
    return Response(serializers.data, status=status.HTTP_200_OK)