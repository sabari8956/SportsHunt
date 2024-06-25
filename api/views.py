from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from organisers.models import *
from core.models import *
from .serializer import *
from django.shortcuts import redirect
from django.contrib import messages
from organisers.utils import *
from sportshunt.conf import dev as settings
from django.urls import reverse
import razorpay
from .decorators import host_required, login_required

# from organisers.decorators import host_required, OrgHost_required 
# NEED TO CREATE API VERSION DECORATORS

@login_required
@api_view(["POST"])
def add_to_cart(req):
    data = req.data
    if not data:
        return Response({"error": "Data is required"}, status=status.HTTP_400_BAD_REQUEST)
    name = data.get('name')
    if not name:
        return Response({"error": "Name is required"}, status=status.HTTP_400_BAD_REQUEST)
    players_instances = Player.objects.create(name=name)

    name_fields = [value for key, value in data.lists() if key.startswith('name_')]
    players_instances = [Player.objects.create(name=name[0]) for name in name_fields]

    category_id = data.get('category')
    if not category_id:
        return Response({"error": "Category is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        category_instance = Category.objects.get(id=int(category_id))
    except (ValueError, Category.DoesNotExist):
        return Response({"error": "Invalid category ID"}, status=status.HTTP_400_BAD_REQUEST)

    # team_size = category_instance.team_size
    # print(players_instances, team_size)
    # if len(players_instances) != team_size:
    #     return Response({"error": f"Team size must be {team_size}"}, status=status.HTTP_400_BAD_REQUEST)

    if category_instance.registration:
        return Response({"error": "Registration closed"}, status=status.HTTP_400_BAD_REQUEST)

    team_instance = Team.objects.create(category=category_instance)
    team_instance.members.set([players_instances])
    user_instance = User.objects.get(username=req.user)
    user_instance.cart.add(team_instance)
    messages.add_message(req, messages.SUCCESS, "added to cart successfully")
    return Response({"message": "added to cart successfully!"}, status=status.HTTP_200_OK)

# @host_required
@api_view(["GET", "POST"])
def create_fixture(req, tournament_name, category_name):
    if not (Tournament.objects.filter(name= tournament_name).exists() and category_name in Tournament.objects.get(name= tournament_name).categories.all().values_list('catagory_type', flat=True)):
        return Response({"error": "Tournament or Category not found"}, status=status.HTTP_404_NOT_FOUND)

    tournament_instance = Tournament.objects.get(name= tournament_name)
    category_instance = tournament_instance.categories.get(catagory_type= category_name)
    # if category_instance.fixture:
    #     return Response({"error": "Fixture already exists"}, status=status.HTTP_400_BAD_REQUEST)
    tournament_instance.onGoing_matches.clear()
    tournament_instance.save()
    fixture_instance = Fixtures.objects.create(
        category= category_instance,
        )
    fixture = KnockOutFixture()
    try:
        response = fixture.initialBracket(fixture_instance.id)
    except Exception as e:
        return Response({"error": f"Error creating fixture: {e}"}, status=status.HTTP_400_BAD_REQUEST)
    
    
    if not response:
        return Response({"error": "Error creating fixture"}, status=status.HTTP_400_BAD_REQUEST)
    return Response({
        "id": fixture_instance.id,
        "fixture_matches": [ match.id for match in fixture_instance.currentBracket.all()],
        "message": "Fixture created successfully",
        },
       status=status.HTTP_200_OK)    
    
@host_required
@api_view(["POST"])
def update_winner(req, tournament_name, category_name):
    winner_team_id = int(req.data.get('winner_team_id'))
    if not winner_team_id:
        return Response({"error": "Winner team ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    if not (Tournament.objects.filter(name= tournament_name).exists() and category_name in Tournament.objects.get(name= tournament_name).categories.all().values_list('catagory_type', flat=True)):
        return Response({"error": "Tournament or Category not found"}, status=status.HTTP_404_NOT_FOUND)

    tournament_instance = Tournament.objects.get(name= tournament_name)
    category_instance = tournament_instance.categories.get(catagory_type= category_name)
    fixture_instance = category_instance.fixture
    if not fixture_instance:
        return Response({"error": "Fixture not found"}, status=status.HTTP_404_NOT_FOUND)
    
    fixture = KnockOutFixture()
    status_ = fixture.add_winners_new(fixture_instance.id, winner_team_id)
    return Response({"message": status_}, status=status.HTTP_200_OK)


@login_required
@api_view(["GET"])
def view_fixture(req, tournament_name, category_name):
    tournament_instance = Tournament.objects.get(name= tournament_name)
    category_instance = tournament_instance.categories.get(catagory_type= category_name)
    fixture_instance = category_instance.fixture
    if not fixture_instance:
        return Response({"error": "Fixture not found"}, status=status.HTTP_404_NOT_FOUND)
    serializers = FixtureSerializer(fixture_instance)
    if len(serializers.data['currentBracket']) == 0 and len(serializers.data['currentWinners']) == 1:
        return Response({"message": "Fixture completed", "winner":serializers.data['currentWinners'][0]}, status=status.HTTP_200_OK)
    return Response(serializers.data, status=status.HTTP_200_OK)


@host_required
@api_view(["POST"])
def schedule_match(req):
    data = req.data
    match_ids = data.get('match_id', None)
    print(match_ids)

    if not match_ids:
        return Response({"error": "Match ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    for match_id in match_ids:
        if not Match.objects.filter(id=match_id).exists():
            return Response({"error": "Invalid match ID"}, status=status.HTTP_400_BAD_REQUEST)
        match_instance = Match.objects.get(id=match_id)
        category_instance = match_instance.match_category
        tournament_instance = category_instance.tournament
        fixture_instance = category_instance.fixture
        if not fixture_instance:
            return Response({"error": "Fixture not found"}, status=status.HTTP_400_BAD_REQUEST)
        if tournament_instance.org.admin != req.user:
            return Response({"error": "You are not authorised to schedule matches"}, status=status.HTTP_403_FORBIDDEN)
        try:
            fixture_instance.currentBracket.remove(match_instance)
            tournament_instance.onGoing_matches.add(match_instance)
            tournament_instance.save()
        except Exception as e:
            return Response({"error": f"Error scheduling match: {e}"}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "Match scheduled"}, status=status.HTTP_200_OK)
            
@host_required
@api_view(["GET", "POST"])  
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

@host_required
@api_view(["GET", "POST"])
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

@host_required
@api_view(["POST"])
def declare_match_winner(req):
    #validate user and tournament
    match_id = req.data.get('match_id', None)
    tournament_id = req.data.get('tournament_id', None)
    
    if not (match_id and tournament_id):
        print('match_id and tournament_id are required')
        return Response({"error": "Match ID and tournament ID are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        match_instance = Match.objects.get(id=match_id)
    
    except Match.DoesNotExist:
        print('Invalid match ID')
        return Response({"error": "Invalid match ID"}, status=status.HTTP_400_BAD_REQUEST)

    if match_instance.match_state:
        print('Match completed')
        return Response({"error": "Match completed"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        tournament_instance = Tournament.objects.get(id=tournament_id)
    except Tournament.DoesNotExist:
        print('Invalid tournament ID')
        return Response({"error": "Invalid tournament ID"}, status=status.HTTP_400_BAD_REQUEST)

    if match_instance not in tournament_instance.onGoing_matches.all():
        print('Match not found in the tournament')
        return Response({"error": "Match not found in the tournament"}, status=status.HTTP_400_BAD_REQUEST)

    fixture_instance = match_instance.match_category.fixture
    if not fixture_instance:
        print('Fixture not found')
        return Response({"error": "Fixture not found"}, status=status.HTTP_400_BAD_REQUEST)

    current_set = match_instance.current_set
    team1_score = current_set.team1_score
    team2_score = current_set.team2_score

    if team1_score > team2_score:
        current_set.winner = match_instance.team1
    elif team2_score > team1_score:
        current_set.winner = match_instance.team2
    else:
        return Response({"message": "Set can't be a draw"}, status=status.HTTP_403_FORBIDDEN)

    current_set.set_status = True
    current_set.save()

    completed_sets = match_instance.sets_scores.filter(set_status=True)
    print(completed_sets, match_instance.sets)
    if len(completed_sets) == match_instance.sets:
        team1_wins = completed_sets.filter(winner=match_instance.team1).count()
        team2_wins = completed_sets.filter(winner=match_instance.team2).count()

        if team1_wins > team2_wins:
            match_instance.winner = match_instance.team1
            match_instance.loser = match_instance.team2
        elif team2_wins > team1_wins:
            match_instance.winner = match_instance.team2
            match_instance.loser = match_instance.team1
        else:
            return Response({"message": "Match can't be a draw or have even sets"}, status=status.HTTP_403_FORBIDDEN)

        match_instance.match_state = True
        match_instance.save()
        KnockOutFixture().add_winners(fixture_instance.id, match_instance.winner.id)
        return Response({"message": "Match completed"}, status=status.HTTP_200_OK)


    set_ids = [s.id for s in match_instance.sets_scores.all()]
    current_set_index = set_ids.index(current_set.id)
    if current_set_index < len(set_ids) - 1:
        match_instance.current_set = Scoreboard.objects.get(id=set_ids[current_set_index + 1])
        match_instance.current_set.save()
    else:
        match_instance.match_state = True
        match_instance.save()
        KnockOutFixture().add_winners(fixture_instance.id, current_set.winner.id)
        return Response({"message": "Match completed"}, status=status.HTTP_200_OK)

    return Response({"message": "Set completed"}, status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
def fixtureJSON(req, fixture_id):
    if not Fixtures.objects.filter(id=fixture_id).exists():
        return Response({"error": "Fixture not found"}, status=status.HTTP_404_NOT_FOUND)
    fixture_instance = Fixtures.objects.get(id=fixture_id)
    serializers = FixtureSerializer(fixture_instance)
    return Response(serializers.data["fixture"], status=status.HTTP_200_OK)
    
@login_required
@api_view(["POST"])
def create_order(request):
    print('here create order')
    if not request.user.is_authenticated:
        return Response({'status': 'not authenticated'} , status=401)
    
    user_instance = User.objects.get(id=request.user.id)
    cart_data = user_instance.cart.all()
    
    team_ids = []
    total_amount = 0
    for item in cart_data:
        team_ids.append(item.id)
        total_amount += item.category.price
    
    print(cart_data, total_amount)
    if total_amount == 0:
        return Response({'status': 'cart is empty'} , status=400)
    
    currency = 'INR'
    amount = total_amount * 100
    try:
        razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID,
                                        settings.RAZOR_KEY_SECRET))
        
        razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                        currency=currency,
                                                        payment_capture='0'))
        
    except Exception as e:
        print(f'error from razorpay side {e}')
        return Response({"error": f'error from razorpay side {e}'}, status=400)
        
    razorpay_order_id = razorpay_order['id']
    callback_url = reverse('core:checkout')
    
    response = {}
    response['razorpay_order_id'] = razorpay_order_id
    response['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    response['razorpay_amount'] = amount
    response['currency'] = currency
    response['callback_url'] = callback_url
    
    
    
    order_instance = Order.objects.create(user=user_instance,
                                          order_id=razorpay_order_id,
                                          amount=amount, status='pending'
                                          )
    
    order_instance.cart_items.set(cart_data)
    order_instance.save()
    print(response)
    return Response(response)

@host_required
@api_view(["POST"])
# techically this host_required will not work when v1.0.0 make sure the tournament name is passed in the arg
def register_player(req):
    #this doesnt work fr doubles and more. only singles
    data = req.data
    print(data)
    name = data.get('name')
    category_id = data.get('category')
    print(name, category_id)
    
    if not (name and category_id):
        return Response({"error": "Name and category ID are required"}, status=status.HTTP_400_BAD_REQUEST)
    
    if not Category.objects.filter(id=int(category_id)).exists():
        return Response({"error": "Invalid category ID"}, status=status.HTTP_400_BAD_REQUEST)
    
    category_instance = Category.objects.get(id=int(category_id))
    tournament_instance = category_instance.tournament
    
    if not tournament_instance.org.admin == req.user:
        messages.add_message(req, messages.ERROR, "You are not authorised to register players")
        return Response({"error": "You are not authorised to register players"}, status=status.HTTP_403_FORBIDDEN)
    
    if category_instance.registration:
        messages.add_message(req, messages.ERROR, "Registration closed")
        return Response({"error": "Registration closed"}, status=status.HTTP_400_BAD_REQUEST)
    
    team_instance = Team.objects.create(category=category_instance, payment_method=False)
    team_instance.members.set([Player.objects.create(name=name)])
    
    category_instance.teams.add(team_instance)
    category_instance.save()
    
    messages.add_message(req, messages.SUCCESS, "Player registered successfully")
    return Response(data, status=status.HTTP_200_OK)

@host_required
@api_view(["POST"])
def close_registration(req, tournament_name, category_name=None):
    if req.user != Tournament.objects.get(name=tournament_name).org.admin:
        return Response("You are not authorised to close registration", status=status.HTTP_403_FORBIDDEN)
    
    if not Tournament.objects.filter(name=tournament_name).exists():
        return Response("Tournament not found", status=status.HTTP_404_NOT_FOUND)
    
    tournament_instance = Tournament.objects.get(name=tournament_name)
    
    if not tournament_instance.categories.filter(catagory_type=category_name).exists():
        return Response("Category not found", status=status.HTTP_404_NOT_FOUND)
    
    if not category_name:
        all_categories = tournament_instance.categories.all()
        for category in all_categories:
            category.registration = True
            category.save()
        return Response("Registration closed for all categories", status=status.HTTP_200_OK)
    
    category_instance = tournament_instance.categories.get(catagory_type=category_name)
    category_instance.registration = True
    category_instance.save()
    return Response(f"Registration closed for {category_name}", status=status.HTTP_200_OK)


@api_view(["POST"])
def edit_mail(req):
    print('here')
    if not req.user.is_authenticated:
        messages.add_message(req, messages.ERROR, "Not authenticated")
        return redirect("core:login")
    
    user_instance = User.objects.get(id=req.user.id)
    data = req.data
    email = data.get('email')
    if user_instance.verified:
        messages.add_message(req, messages.ERROR, "Email already verified")
        return Response("Email already verified", status=status.HTTP_403_FORBIDDEN)
    
    if User.objects.filter(email=email).exists():
        print(User.objects.filter(email=email))
        messages.add_message(req, messages.ERROR, "Email already exists")
        return Response("Email already exists", status=status.HTTP_409_CONFLICT)
    
    user_instance.email = email
    user_instance.save()
    messages.add_message(req, messages.SUCCESS, "Email updated successfully")
    return Response("Email updated successfully", status=status.HTTP_200_OK)
    