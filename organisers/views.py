from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from utils import *
from api.serializer import OrganisationSerializer
from .models import *

# Create your views here.
@login_required(login_url="/login/")
def index(req):
    if not (req.user.is_organiser):
        messages.add_message(req, messages.INFO, 'You Need to be a Organiser!')
        return redirect("core:index")
    
    organisation = req.session.get("organisation", None)
    if not organisation:
        return redirect("organisers:orgs")
    orgs = Organisation.objects.get(id= organisation)
    serializer = OrganisationSerializer(orgs)
    if not (req.user.id == serializer.data["admin"] or  req.user.id in serializer.data["mods"]):
        req.session["organisation"] = None
        return redirect("organisers:orgs")
    return render(req, "organisers/organiser_index.html", {
        "organisation": serializer.data
    })

@login_required(login_url="/login/")
def organisation_creation_form(req):
    
    if not (req.user.is_organiser):
        messages.add_message(req, messages.INFO, 'You Need to be a Organiser!')
        return redirect("core:index")
    
    if req.method == 'POST':
        serializer = OrganisationSerializer(data= req.POST)
        if serializer.is_valid():
            serializer.save()
            return redirect("organisers:orgs")
        
        messages.add_message(req, messages.WARNING, serializer.errors)
        return render(req, "organisers/organisation_form.html", {
            "initial_data": req.POST
            })

    return render(req, "organisers/organisation_form.html")

@login_required(login_url="/login/")
def organisation_page(req):
    orgs = Organisation.objects.filter(admin= req.user)
    serializer = OrganisationSerializer(orgs, many=True)
    orgs = [org['id'] for org in serializer.data]
    if len(orgs) == 0:
        return redirect("organisers:new_organisation")
    if len(orgs) == 1:
        req.session["organisation"] = orgs[0]
        return redirect("organisers:index")
    
    if req.method == "POST":
        opt = int(req.POST["option"])
        if opt in orgs:
            req.session["organisation"] = opt
        else:
            messages.add_message(req, messages.ERROR, 'Some Error OccurEd')
        return redirect("organisers:index")

    if not (req.user.is_organiser):
        messages.add_message(req, messages.INFO, 'You Need to be a Organiser!')
        return redirect("core:index")
    
    return render(req, "organisers/organisation_selection.html", {
        "orgs": serializer.data,
    })