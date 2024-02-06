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
    
    return render(req, "organisers/organiser_index.html", {
        "organisation": serializer.data
    })

@login_required(login_url="/login/")
def organisation_creation_form(req):
    
    if not (req.user.is_organiser):
        messages.add_message(req, messages.INFO, 'You Need to be a Organiser!')
        return redirect("core:index")
    
    if req.method == 'POST':
        form_data = clean_querydict(req.POST)
        print(form_data)
    
    return render(req, "organisers/organisation_form.html")

@login_required(login_url="/login/")
def organisation_page(req):
    orgs = Organisation.objects.filter(admin= req.user)
    serializer = OrganisationSerializer(orgs, many=True)
    if req.method == "POST":
        opt = int(req.POST["option"])
        orgs = [org['id'] for org in serializer.data]
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