from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from utils import *
from api.serializer import *
from .models import *
from .forms import *
from .decorators import organiser_required, host_required
# Create your views here.

@organiser_required
def index(req):
    
    organisation = req.session.get("organisation", None)
    if not organisation:
        return redirect("organisers:orgs")
    
    orgs = Organisation.objects.get(id= organisation)
    serializer = OrganisationSerializer(orgs)
    
    if not (req.user.id == serializer.data["admin"] or  req.user.id in serializer.data["mods"]):
        req.session["organisation"] = None
        return redirect("organisers:orgs")
    
    tourns = Tournament.objects.filter(org= organisation)
    tournament_serializer = TournamentSerializer(tourns, many=True)
    return render(req, "organisers/organiser_index.html", {
        "organisation": serializer.data,
        "tournaments": tournament_serializer.data
    })

@organiser_required
def organisation_creation_form(req):
    if req.method == "POST":
        form = OrganaisationForm(req.POST)
        if form.is_valid():
            req.session["organisation"] = form.save(admin= req.user).id
            return redirect("organisers:index")
        
        return render(req, "organisers/organisation_form.html", {
            "form": form 
            })
    
    return render(req, "organisers//organisation_form.html",{
        "form": OrganaisationForm(),
    })


@organiser_required
def organisation_page(req):
    orgs = Organisation.objects.filter(admin= req.user)
    serializer = OrganisationSerializer(orgs, many=True)
    orgs = [org['id'] for org in serializer.data]
    
    if req.method == "POST":
        opt = int(req.POST["option"])
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
        "orgs": serializer.data,
    })
    
@organiser_required
def tournament_creation_form(req):
    if req.method == "POST":
        form = TournamentForm(req.POST)
        if form.is_valid():
            form.save(org= req.session["organisation"])
            return redirect("organisers:index")

        return render(req, "organisers/tournament_form.html", {
            "form": form 
            })
    
    return render(req, "organisers/tournament_form.html",{
        "form": TournamentForm(),
    })

@organiser_required
def create_categories(req, tournament_name):
    print("here")
    tournament = Tournament.objects.get(name=tournament_name)
    if not tournament:
        print("here")
        messages.add_message(req, messages.ERROR, 'No Such Tournament Found.')
        return redirect("organisers:index")
    serializer = TournamentSerializer(tournament, many=False)
    
    # if not (req.user.id == serializer.data["org"]["admin"] or req.user.id in serializer.data["org"]["mods"]):
    #     messages.add_message(req, messages.ERROR, 'You are not authorised to create categories.')
    #     return redirect("organisers:index")
    cats = [c["catagory_type"] for c in serializer.data["categories"]]
    if req.POST:
        form = CategoriesForm(req.POST)
        if form.is_valid():
            if form.cleaned_data["catagory_type"] in cats:
                messages.add_message(req, messages.ERROR, 'Category already exists.')
                return render(req, r"organisers\create_catogry_form.html", {
                    "form": form ,
                })
            else:
                
                cat = form.save(tournament=tournament)
                tournament.categories.add(cat)
            return redirect("organisers:index")
        return render(req, r"organisers\create_catogry_form.html", {
            "form": form 
            })

    return render(req, r"organisers\create_catogry_form.html",{
        "form": CategoriesForm(),
    })

@host_required
def org_tournament_view(req, tournament_name):
    if not (Tournament.objects.filter(name=tournament_name).exists()):
        return render(req, "errors/tournament_not_found.html", {
            "tournament_name": tournament_name, 
        })
    tournament = Tournament.objects.get(name=tournament_name)
    serializer = TournamentSerializer(tournament, many=False)
    return render(req, "organisers/org_tournament_view.html", {
        "tournament_data": serializer.data,
        "n_categories": range(len(serializer.data["categories"])),
    })

@host_required
def category_view(req, tournament_name, category_name):
    if not (Tournament.objects.filter(name=tournament_name).exists()):
        return render(req, "errors/tournament_not_found.html", {
            "tournament_name": tournament_name, 
        })
    
    if not (Tournament.objects.get(name=tournament_name).categories.filter(catagory_type=category_name).exists()):
        return render(req, "errors/category_not_found.html", {
            "category_name": category_name, 
        })
    
    tournament_instance = Tournament.objects.get(name=tournament_name)
    category_instance = tournament_instance.categories.get(catagory_type=category_name)
    fixture_instance = category_instance.fixture
    fixture_serializer = fixtureSerializer(fixture_instance)
    tournament_data = TournamentSerializer(tournament_instance, many=False).data
    teams = [[mem.name for mem in team.members.all()] for team in category_instance.teams.all()] 
    fixture_data = FixtureSerializer(fixture_instance, many=False).data
    fixture_brackets = []
    fixture_brackets_serialized = []
    
    if fixture_serializer.data.get("currentBracket"):
        fixture_brackets_serialized = fixture_serializer.data["currentBracket"]
        
    for match in fixture_brackets_serialized:
        match_serializer = matchSerializer(Match.objects.get(id=match["id"]))
        fixture_brackets.append(match_serializer.data)
        
    stages_dict = {
        None: 'Not Started',
        0: 'Completed',
        1: 'Finals',
        2: 'Semi Finals',
        3: 'Quater Finals',
        4: 'Round of 16',
        5: 'Round of 32',
    }
    
    ongoing_matches = []
    
    for match in tournament_data["onGoing_matches"]:
        if match["match_category"]["id"] == category_instance.id:
            ongoing_matches.append(match) 
            
    for matches in ongoing_matches:
        print(f"{matches["team1"]["id"]} vs {matches["team2"]["id"]}")
    winner = None
    if fixture_data.get("currentWinners"):
        winner = fixture_data["currentWinners"]
        if len(winner) == 1:
            winner = winner[0]
    
    data = {
        "tournament_data": tournament_instance,
        "category_data": category_instance,
        "fixture_instance": fixture_instance,
        "fixture_data": fixture_data,
        "fixture_serializer": fixture_serializer.data,
        "teams": teams,
        "fixture_brackets": fixture_brackets,
        "stage": stages_dict.get(fixture_data["currentStage"], "Not Started"),
        "winner": winner,
        "ongoing_matches": ongoing_matches,
        "upcoming_matches": fixture_data.get("currentBracket"),
    }
    
    return render(req, "organisers/category.html", data)

@host_required
def score_ongoingMatches(req, tournament_name):
    
    if not (Tournament.objects.filter(name=tournament_name).exists()):
        return render(req, "errors/tournament_not_found.html", {
            "tournament_name": tournament_name, 
        })
    
    tournament_instance = Tournament.objects.get(name=tournament_name)
    tournamentSerializer = TournamentSerializer(tournament_instance, many=False).data
    
    ongoing_matches = tournamentSerializer["onGoing_matches"]
    
    return render(req, "organisers/scoreboard_ongoing_matches.html", {
        "ongoing_matches": ongoing_matches,
        "tournament_name": tournament_instance.name,
    })
    
@host_required
def scoreboard_view(req, tournament_name, match_id):
    
    if not (Tournament.objects.filter(name=tournament_name).exists()):
        return render(req, "errors/tournament_not_found.html", {
            "tournament_name": tournament_name, 
        })
    
    if not (Match.objects.filter(id=match_id).exists()):
        return render(req, "errors/tournament_not_found.html", { # Change this to match not found
            "match_id": match_id, 
        })
    
    tournament_instance = Tournament.objects.get(name=tournament_name)
    tournament_serializer = TournamentSerializer(tournament_instance, many=False).data
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
    
    # print(tournament_serializer)
    print(match_serializer)
    
    return render(req, "organisers/scoreboard.html", {
        "tournament_data": tournament_instance,
        "match_data": match_serializer,
    })