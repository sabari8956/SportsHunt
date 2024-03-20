from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from utils import *
from api.serializer import OrganisationSerializer, TournamentSerializer
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
    print(tournament_serializer.data)
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
    tournament = Tournament.objects.get(name=tournament_name)
    if not tournament:
        messages.add_message(req, messages.ERROR, 'No Such Tournament Found.')
        return redirect("organisers:index")
    serializer = TournamentSerializer(tournament, many=False)
    
    if not (req.user.id == serializer.data["org"]["admin"] or req.user.id in serializer.data["org"]["mods"]):
        messages.add_message(req, messages.ERROR, 'You are not authorised to create categories.')
        return redirect("organisers:index")
    cats = [c["catagory_type"] for c in serializer.data["categories"]]
    if req.POST:
        form = CategoriesForm(req.POST)
        if form.is_valid():
            if form.cleaned_data["catagory_type"] in cats:
                print("Category already exists")
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
    })