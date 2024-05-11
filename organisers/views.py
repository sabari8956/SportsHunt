from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from utils import *
from api.serializer import *
from .models import *
from .forms import *
from .decorators import organiser_required, host_required, OrgHost_required
# Create your views here.

@OrgHost_required
def index(req):
    # we can move this inside @organiser_required decorator
    organisation = req.session.get("organisation", None)
    orgs = Organisation.objects.get(id= organisation)
    serializer = BasicTournamentSerializer(orgs)

    
    tourns = Tournament.objects.filter(org= organisation)
    tournament_serializer = BasicTournamentSerializer(tourns, many=True)
    return render(req, "organisers/organiser_index.html", {
        "organisation": serializer.data,
        "tournaments": tournament_serializer.data
    })

@organiser_required
def organisation_creation_form(req):
    # Convert all these into serializers
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
def organisation_page(req): # org selection page
    orgs = Organisation.objects.filter(admin= req.user)
    orgs = [org.id for org in orgs]
    
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
        "orgs": orgs,
    })
    
@OrgHost_required
# change this to API soon.
def create_tournament(req, form):
    if req.method == "POST":
        if form.is_valid():
            form.save(org=req.session["organisation"])
            return redirect("organisers:index")

        return render(req, "organisers/tournament_form.html", {
            "form": form 
        })
# i spilted this for now but we can merge this with the above function as a API soon.
def tournament_creation_form(req):
    # Convert all these into serializers
    form = TournamentForm(req.POST) if req.method == "POST" else TournamentForm()
    return create_tournament(req, form)

@OrgHost_required
@host_required
def create_categories(req, tournament_name):
    print("here")
    tournament = Tournament.objects.get(name=tournament_name)
    if not tournament:
        print("here")
        messages.add_message(req, messages.ERROR, 'No Such Tournament Found.')
        return redirect("organisers:index")

    serializer = CreateCategoriesTournamentSerializer(tournament).data
    cats = serializer["categories"]
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
            return redirect("organisers:index")# redirect to the category page in future
        return render(req, r"organisers\create_catogry_form.html", {
            "form": form 
            })

    return render(req, r"organisers\create_catogry_form.html",{
        "form": CategoriesForm(),
    })
@OrgHost_required
@host_required
def org_tournament_view(req, tournament_name):
    if not (Tournament.objects.filter(name=tournament_name).exists()):
        return render(req, "errors/tournament_not_found.html", {
            "tournament_name": tournament_name, 
        })
    tournament = Tournament.objects.get(name=tournament_name)
    serializer = OrgTournamentSerializer(tournament, many=False)
    print(serializer.data)
    return render(req, "organisers/org_tournament_view.html", {
        "tournament_data": serializer.data,
        "n_categories": range(len(serializer.data["categories"])),
    })

@OrgHost_required
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
    upcoming_matches = fixture_data["currentBracket"]
    
    print(fixture_data)
    return render(req, "organisers/category.html", {
        "tournament_data": tournament_instance,
        "category_data": category_instance,
        "fixture_data": fixture_data,
        "teams": teams,
        "upcoming_matches": upcoming_matches,
        "stage": stages_dict.get(fixture_data["currentStage"], "Not Started -")
        
    })
    
@OrgHost_required
@host_required
def score_ongoingMatches(req, tournament_name):
    
    if not (Tournament.objects.filter(name=tournament_name).exists()):
        return render(req, "errors/tournament_not_found.html", {
            "tournament_name": tournament_name, 
        })
    
    tournament_instance = Tournament.objects.get(name=tournament_name)
    tournamentSerializer = TournamentOngoingMatchesSerializer(tournament_instance, many=False).data
    
    ongoing_matches = tournamentSerializer["onGoing_matches"]
    print(tournamentSerializer)
    return render(req, "organisers/scoreboard_ongoing_matches.html", {
        "ongoing_matches": ongoing_matches,
        "tournament_name": tournament_instance.name,
    })

@OrgHost_required 
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