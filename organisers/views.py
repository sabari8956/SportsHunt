from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from utils import *
from api.serializer import *
from .models import *
from .forms import *
from .decorators import organiser_required, host_required
from .validators import *
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
# Create your views here.

@host_required
def index(req):
    organisation = req.session.get("organisation", None)
    org = Organisation.objects.get(id= organisation)
    tourns = Tournament.objects.filter(org= org)
    tournament_serializer = BasicTournamentSerializer(tourns, many=True)
    now = timezone.now()
    now_date = now.date()
    end_date = now + timedelta(days=15)
    upcoming_tournaments = tourns.filter(start_date__range=(now, end_date)).order_by('start_date')[:3]    
    ongoing_tournaments = tourns.filter(start_date=now_date)[:3]
    recent_tournaments = tourns.filter(start_date__lt=now_date).order_by('-start_date')[:3]
    
    return render(req, "organisers/organiser_index.html", {
        "organisation": org.name,
        "tournaments": tournament_serializer.data,
        "upcoming_tournaments": upcoming_tournaments,
        "ongoing_tournaments": ongoing_tournaments,
        "recent_tournaments": recent_tournaments,
    })

@organiser_required
def organisation_creation_form(req):
    if req.method == "POST":
        
        if OrganisationValidator(req).clean_validate_save():
            return redirect("organisers:index")
        
        return render(req, "organisers/organisation_form.html", {
            })
    
    return render(req, "organisers/organisation_form.html",{
    })


@organiser_required
def organisation_page(req): # org selection page
    org = Organisation.objects.filter(admin= req.user)
    orgs = [_org.id for _org in org]
    if req.method == "POST":
        opt = int(req.POST["organisation"])
        if opt in orgs:
            req.session["organisation"] = opt
        else:
            messages.add_message(req, messages.ERROR, 'Some Error OccurEd')
        return redirect("organisers:index")
    
    if len(orgs) == 0:
        return redirect("organisers:new_organisation")
    
    elif len(orgs) == 1:
        req.session["organisation"] = orgs[0]
        return redirect("organisers:index")

    return render(req, "organisers/organisation_selection.html", {
        "orgs": org,
    })
    
@organiser_required
def tournament_creation_form(req):
    # Convert all these into serializers
    if req.method == "POST":
        if tourn := TournamentValidator(req).clean_validate_save():
            return redirect(reverse("organisers:create_categories", kwargs={'tournament_name': tourn.name}))
        
    return render(req, "organisers/tournament_form.html",{
    })


@host_required
def create_categories(req, tournament_name):
    
    if req.method == "POST":
        print(req.POST)
        if cat := CategoryValidator(req, tournament_name).clean_validate_save():
            return redirect(reverse("organisers:category", kwargs={'tournament_name': tournament_name, "category_name": cat.catagory_type}))
    return render(req, "organisers/create_catogry_form.html", )


@host_required
def org_tournament_view(req, tournament_name):
    tournament = Tournament.objects.get(name=tournament_name)
    serializer = OrgTournamentSerializer(tournament, many=False)
    return render(req, "organisers/org_tournament_view.html", {
        "tournament_data": serializer.data,
    })

@host_required
def category_view(req, tournament_name, category_name):
    
    stages_dict = {
        None: 'Not Started',
        0: 'Completed',
        1: 'Finals',
        2: 'Semi Finals',
        3: 'Quater Finals',
        4: 'Round of 16',
        5: 'Round of 32',
    }
    
    tournament_instance = Tournament.objects.get(name=tournament_name)
    category_instance = tournament_instance.categories.get(catagory_type=category_name)
    serializers = CategoryViewSerializer(category_instance, many=False).data
    teams = [team['members'] for team in serializers["teams"]]
    fixture_data = serializers["fixture"]
    
    upcoming_matches, stage = None, 'Fixture not Created Yet!'
    if fixture_data:
        upcoming_matches = fixture_data.get("currentBracket")
        stage = stages_dict.get(fixture_data["currentStage"] + 1, "Not Started -")
    
    return render(req, "organisers/category.html", {
        "tournament_data": tournament_instance,
        "category_data": category_instance,
        "fixture_id": fixture_data['id'] if fixture_data else None,
        "teams": teams,
        "upcoming_matches": upcoming_matches,
        "stage": stage,

    })
    

@host_required
def score_ongoingMatches(req, tournament_name):
    tournament_instance = Tournament.objects.get(name=tournament_name)
    tournamentSerializer = TournamentOngoingMatchesSerializer(tournament_instance, many=False).data
    
    ongoing_matches = tournamentSerializer["onGoing_matches"]
    return render(req, "organisers/scoreboard_ongoing_matches.html", {
        "ongoing_matches": ongoing_matches,
        "tournament_name": tournament_instance.name,
    })

@host_required
def scoreboard_view(req, tournament_name, match_id):
    tournament_instance = Tournament.objects.get(name=tournament_name)
    tournament_serializer = TournamentOngoingMatchesSerializer(tournament_instance, many=False).data
    match_instance = Match.objects.get(id= match_id)
    match_serializer = MatchDataSerializer(match_instance).data
    if match_serializer["id"] not in [ match["id"] for match in tournament_serializer["onGoing_matches"] ]:
        return render(req, "errors/tournament_not_found.html", { # Change this to match not found
            "match_id": match_id,
            "tournament_name": "error match nt found" 
        })
        
    if not match_serializer["sets_scores"]:
        for i in range(match_serializer["sets"]):
            match_instance.sets_scores.create(set_no= i+1, match= match_instance)
            if i == 0:
                match_instance.current_set = match_instance.sets_scores.get(set_no= 1)
        match_instance.save()
        
    return render(req, "organisers/scoreboard.html", {
        "tournament_data": tournament_instance,
        "match_data": match_serializer,
    })
    

@host_required
def scoreboard(req):
    organisation = req.session.get("organisation", None)
    org = Organisation.objects.get(id= organisation)
    tourns = Tournament.objects.filter(org= org)
    now = timezone.now()
    now_date = now.date()
    ongoing_tournaments = tourns.filter(start_date=now_date)
    return render(req, "organisers/ongoing_tournaments.html", {
        "tournaments": ongoing_tournaments,
    })