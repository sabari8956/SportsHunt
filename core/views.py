from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from .models import *
from organisers.models import *
from api.serializer import *
from django.db import IntegrityError
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
# Create your views here.
def index(req):
    messages = req._messages
    now = timezone.now()
    end_date = now + timedelta(days=15)
    upcoming_tournaments = Tournament.objects.filter(start_date__range=(now, end_date)).order_by('start_date')[:5]
    print(upcoming_tournaments)
    return render(req, "core/index.html", {
        "messages":messages,
        "upcoming_tournaments": upcoming_tournaments,
    })

def login_view(req):
    if req.method == "POST":
        username = req.POST["username"]
        password = req.POST["password"]
        user = authenticate(req, username=username, password=password)

        if user is not None:
            login(req, user)
            if user.is_organiser:
                return HttpResponseRedirect(reverse("organisers:index"))
            return HttpResponseRedirect(reverse("core:index"))
        else:
            return render(req, "auth/login.html", {
                "message": "Invalid Username/ Password",
        })
    return render(req, "auth/login.html", {})

def logout_view(req):
    logout(req)
    return HttpResponseRedirect(reverse("core:index"))

def register_view(req):
    if req.method == "POST":
        username = req.POST["username"].strip()
        email = req.POST["email"]
        password = req.POST["password"]
        confirmation = req.POST["confirmation"]
        if not username:
            messages.add_message(req, messages.ERROR, 'Enter a Valid Username')
            return render(req, "auth/register.html", {
                "message": "Enter a Valid Username"
            })        
        if password != confirmation:
            messages.add_message(req, messages.ERROR, 'Passwords must match.')
            return render(req, "auth/register.html", {
                "message": "Passwords must match."
            })
        if User.objects.filter(username=username).exists():
            messages.add_message(req, messages.ERROR, 'Username already taken.')
            return render(req, "auth/register.html", {
                "message": "Username already taken."
            })
            
        elif User.objects.filter(email=email).exists():
            messages.add_message(req, messages.ERROR, 'Email already registed')
            return render(req, "auth/register.html", {
                "message": "Email already registed"
            })
            
        else:
            try:
                user = User.objects.create_user(username, email, password)
                if req.POST.get("is_organiser", False):
                    user.is_organiser = True
                user.save()
            except Exception as e:
                return render(req, "auth/register.html", {
                    "message": str(e)
                })
        login(req, user)
        if user.is_organiser:
            return HttpResponseRedirect(reverse("organisers:index"))
        return HttpResponseRedirect(reverse("core:index"))
    else:
        return render(req, "auth/register.html")

def organisation_view(req, org_name):
    if not (Organisation.objects.filter(name=org_name).exists()):
        return render(req, "errors/organisation_not_found.html", {
            "org_name": org_name,
        })
    org_data = Organisation.objects.get(name=org_name)
    serializer = OrganisationSerializer(org_data, many=False)
    print(serializer.data)
    return render(req, "core/organisation.html", {
        "org_data": serializer.data,
    })
    
def organisation_tournament_view(req, org_name, tournament_name):
    org = Organisation.objects.get(name=org_name)
    if not org:
        return render(req, "errors/organisation_not_found.html", {
            "org_name": org_name,
        })
    
    tournament = Tournament.objects.get(name=tournament_name)
    serializer = TournamentSerializer(tournament, many=False)
    if not tournament or tournament.org != org:
        return render(req, "errors/tournament_not_found.html", {
            "tournament_name": tournament_name,
        })
    return render(req, "core/tournament.html", {
        "tournament_data": serializer.data,
    })