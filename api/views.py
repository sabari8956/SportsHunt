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

    category_id = data.get('category')
    if not category_id:
        return Response({"error": "Category is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        category_instance = Category.objects.get(id=int(category_id))
    except (ValueError, Category.DoesNotExist):
        return Response({"error": "Invalid category ID"}, status=status.HTTP_400_BAD_REQUEST)

    team_size = category_instance.team_size
    if len(players_instances) != team_size:
        return Response({"error": f"Team size must be {team_size}"}, status=status.HTTP_400_BAD_REQUEST)

    team_instance = Team.objects.create(category=category_instance)
    team_instance.members.set(players_instances)
    user_instance = User.objects.get(username=req.user)
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

# @host_required
@api_view(["GET", "POST"])
def create_fixture(req, tournament_name, category_name):
    if not (Tournament.objects.filter(name= tournament_name).exists() and category_name in Tournament.objects.get(name= tournament_name).categories.all().values_list('catagory_type', flat=True)):
        return Response({"error": "Tournament or Category not found"}, status=status.HTTP_404_NOT_FOUND)

    tournament_instance = Tournament.objects.get(name= tournament_name)
    category_instance = tournament_instance.categories.get(catagory_type= category_name)
    # if category_instance.fixture:
    #     return Response({"error": "Fixture already exists"}, status=status.HTTP_400_BAD_REQUEST)
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
    
# @host_required
@api_view(["POST"])
def update_winner(req, tournament_name, category_name):
    winner_team_id = int(req.data.get('winner_team_id'))
    print(winner_team_id)
    if not winner_team_id:
        return Response({"error": "Winner team ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    if not (Tournament.objects.filter(name= tournament_name).exists() and category_name in Tournament.objects.get(name= tournament_name).categories.all().values_list('catagory_type', flat=True)):
        return Response({"error": "Tournament or Category not found"}, status=status.HTTP_404_NOT_FOUND)

    tournament_instance = Tournament.objects.get(name= tournament_name)
    category_instance = tournament_instance.categories.get(catagory_type= category_name)
    fixture_instance = category_instance.fixture
    if not fixture_instance:
        return Response({"error": "Fixture not found"}, status=status.HTTP_404_NOT_FOUND)
    status_ = knockoutFixtureGenerator().add_winners(fixture_instance.id, winner_team_id)
    return Response({"message": status_}, status=status.HTTP_200_OK)

# @host_required
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

# @host_required
@api_view(["GET","POST"])
def schedule_match(req, tournament_name, category_name):
    match_id = req.data.get('match_id', None)
    court_id = req.data.get('court_id', None)
    if not match_id:
        return Response({"error": "Match ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    if not (Tournament.objects.filter(name= tournament_name).exists() and category_name in Tournament.objects.get(name= tournament_name).categories.all().values_list('catagory_type', flat=True)):
        return Response({"error": "Tournament or Category not found"}, status=status.HTTP_404_NOT_FOUND)
    
    tournament_instance = Tournament.objects.get(name= tournament_name)
    category_instance = tournament_instance.categories.get(catagory_type= category_name)
    fixture_instance = category_instance.fixture
    if not fixture_instance:
        return Response({"error": "Fixture not found"}, status=status.HTTP_404_NOT_FOUND)
    # serializers = fixtureSerializer(fixture_instance)
    
    # if len(serializers.data['currentBracket']) == 0 and len(tournament_instance.onGoing_matches.filter(match_category=category_instance)) == 0 and len(serializers.data['currentWinners']) == 1:
    #     return Response({"message": "Fixture completed", "winner": serializers.data['currentWinners'][0]}, status=status.HTTP_200_OK)

    category_matches = [ match.id for match in fixture_instance.currentBracket.all()]
    if not (Match.objects.filter(id=match_id).exists()):
        return Response({"error": "Invalid match ID"}, status=status.HTTP_400_BAD_REQUEST)
    match_instance = Match.objects.get(id=match_id)
    if not (match_instance.match_category.id == category_instance.id):
        return Response({"error": "match ID and category id doesnt match"}, status=status.HTTP_400_BAD_REQUEST)
    if not match_instance.id in category_matches:
        return Response({"error": "Match not found in the fixture"}, status=status.HTTP_400_BAD_REQUEST)

    if court_id:
        match_instance.court = court_id
        match_instance.save()
    
    fixture_instance.currentBracket.remove(match_instance)
    tournament_instance.onGoing_matches.add(match_instance)
    tournament_instance.save()

    return Response({"message":"match Scheduled"}, status=status.HTTP_200_OK)

@api_view(["GET", "POST"])  
# @host_required
def increment_score(req, match_id, team_id):
    
    if not (Match.objects.filter(id=match_id).exists() and Team.objects.filter(id=team_id).exists()):
        return Response({"error": "Invalid match or team ID"}, status=status.HTTP_400_BAD_REQUEST)
    match_instance = Match.objects.get(id=match_id)
    
    if not (team_id == match_instance.team1.id or team_id == match_instance.team2.id):
        return Response({"error": "Team not found in the match"}, status=status.HTTP_400_BAD_REQUEST)
    if team_id == match_instance.team1.id:
        score_team1 = match_instance.current_set.team1_score
        match_instance.current_set.team1_score = ( score_team1 + 1)
    
    elif team_id == match_instance.team2.id:
        score_team2 = match_instance.current_set.team2_score
        match_instance.current_set.team2_score = (score_team2 + 1)

    else:
        return Response({"error": "Team not found in the match"}, status=status.HTTP_400_BAD_REQUEST)
    match_instance.current_set.save()
    return Response({"message": "Score updated", "score":{
        "team1": match_instance.current_set.team1_score,
        "team2": match_instance.current_set.team2_score,
        }}, status=status.HTTP_200_OK)

@api_view(["GET", "POST"])
# @host_required
def decrement_score(req, match_id, team_id):

    if not (Match.objects.filter(id=match_id).exists() and Team.objects.filter(id=team_id).exists()):
        return Response({"error": "Invalid match or team ID"}, status=status.HTTP_400_BAD_REQUEST)
    match_instance = Match.objects.get(id=match_id)
    if not (team_id == match_instance.team1.id or team_id == match_instance.team2.id):
        return Response({"error": "Team not found in the match"}, status=status.HTTP_400_BAD_REQUEST)
    if team_id == match_instance.team1.id:
        match_instance.current_set.team1_score -= 1
    
    elif team_id == match_instance.team2.id:
        match_instance.current_set.team2_score -= 1
    match_instance.current_set.save()
    return Response({"message": "Score updated"}, status=status.HTTP_200_OK)

@api_view(["GET", "POST"])
def declare_match_winner(req, match_id, tournament_id):
    
    if not req.user.is_authenticated:
        return Response({"error": "Login required"}, status=status.HTTP_401_UNAUTHORIZED)
    
    if not Match.objects.filter(id=match_id).exists():
        return Response({"error": "Invalid match ID"}, status=status.HTTP_400_BAD_REQUEST)
    
    if Match.objects.get(id=match_id).match_state:
        return Response({"error": "Match completed"}, status=status.HTTP_400_BAD_REQUEST)
    
    if not Tournament.objects.filter(id=tournament_id).exists():
        return Response({"error": "Invalid tournament ID"}, status=status.HTTP_400_BAD_REQUEST)
    
    # if not (req.user in Tournament.objects.get(id=tournament_id).mods or req.user == Tournament.objects.get(id=tournament_id).org.admin):
    #     return Response({"error": "Permission denied"}, status=status.HTTP_401_UNAUTHORIZED)
    
    match_instance = Match.objects.get(id=match_id)

    no_sets = match_instance.sets
    sets_compeleted = [_set.winner.id for _set in match_instance.sets_scores.all() if _set.set_status]
    if no_sets == len(sets_compeleted):
        team1_wins = sets_compeleted.count(match_instance.team1.id)
        team2_wins = sets_compeleted.count(match_instance.team2.id)
        if team1_wins > team2_wins:
            match_instance.winner = match_instance.team1
            match_instance.loser = match_instance.team2
            match_instance.match_state = True
            match_instance.save()
            return Response({"message": "Match completed"}, status=status.HTTP_200_OK)
        elif team2_wins > team1_wins:
            match_instance.winner = match_instance.team2
            match_instance.loser = match_instance.team1
            match_instance.match_state = True
            match_instance.save()
            return Response({"message": "Match completed"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Match cant be draw or have even sets"}, status=status.HTTP_403_FORBIDDEN)
        

    
    teamA_score = match_instance.current_set.team1_score
    teamB_score = match_instance.current_set.team2_score
    if teamA_score > teamB_score:
        match_instance.current_set.winner = match_instance.team1
        match_instance.current_set.set_status = True
        print("winner", match_instance.current_set.winner)
        set_id = match_instance.current_set.id
        sets = [match.id for match in match_instance.sets_scores.all()]
        match_instance.current_set = Scoreboard.objects.get(id=sets[sets.index(set_id)+1])
        match_instance.current_set.save()
        
        return Response({"message": "Set completed"}, status=status.HTTP_200_OK)
    
    elif teamB_score > teamA_score:
        match_instance.current_set.winner = match_instance.team2
        match_instance.current_set.set_status = True
        set_id = match_instance.current_set.id
        sets = [match.id for match in match_instance.sets_scores.all()]
        match_instance.current_set = Scoreboard.objects.get(id=sets[sets.index(set_id)+1])
        match_instance.current_set.save()

        print("winner", match_instance.current_set.winner)

        return Response({"message": "Set completed"}, status=status.HTTP_200_OK)
    
    else:
        return Response({"message": "Set cant be draw"}, status=status.HTTP_403_FORBIDDEN)
    