from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from utils import *
from api.serializer import OrganisationSerializer
from .models import *
from .decorators import organiser_required
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
    
    return render(req, "organisers/organiser_index.html", {
        "organisation": serializer.data
    })

@organiser_required
def organisation_creation_form(req):
    if req.method == 'POST':
        serializer = OrganisationSerializer(data= req.POST)
        if serializer.is_valid():
            serializer.save()
            return redirect("organisers:orgs")
        
        messages.add_message(req, messages.WARNING, serializer.errors)
        return render(req, "organisers/organisation_form.html", {
            "form_data": req.POST
            })

    return render(req, "organisers/organisation_form.html")

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