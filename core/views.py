from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from .models import *
from organisers.models import *
from api.serializer import *
from django.db import IntegrityError
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from organisers.forms import *
from .utils import *
# Create your views here.


def index(req):
    messages = req._messages
    now = timezone.now()
    end_date = now + timedelta(days=15)
    upcoming_tournaments = Tournament.objects.filter(start_date__range=(now, end_date)).order_by('start_date')[:5]
    # print(upcoming_tournaments)x
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
            messages.add_message(req, messages.ERROR, 'Invalid Username/ Password')
            return render(req, "auth/login.html")
    return render(req, "auth/login.html", {})

def logout_view(req):
    logout(req)
    return HttpResponseRedirect(reverse("core:index"))

def register_view(req):
    if req.method == "POST":
        user = validateRegister(req)
        if user:
            login(req, user)
            return redirect("core:verifyMail")
        
        return render(req, "auth/register.html")
    else:
        return render(req, "auth/register.html")

@login_required(login_url="/login/")
def verifyMail_view(req):
    user = req.user
    user_instance = User.objects.get(id=user.id)
    
    if user.verified:
        messages.add_message(req, messages.INFO, 'Email already verified')
        return redirect("core:index")
    
    if req.method == "POST":
        otp = req.POST["otp"]
        valid_otp = user_instance.otp == otp and user_instance.otpTime > timezone.now() - timezone.timedelta(minutes=5)
        if valid_otp:
            user_instance.verified = True
            user_instance.save()
            messages.add_message(req, messages.SUCCESS, 'Email Verified Successfully')
            
            if user.is_organiser:
                return HttpResponseRedirect(reverse("organisers:index"))
            return HttpResponseRedirect(reverse("core:index"))
        
        messages.add_message(req, messages.ERROR, 'Invalid OTP or OTP Expired')
        return render(req, "auth/verifyMail.html") 
    
    print(user_instance.otpTime)
    if not user_instance.otpTime or user_instance.otpTime < timezone.now() - timezone.timedelta(minutes=5):
        if sendOTP(user_instance):
            messages.add_message(req, messages.INFO, 'OTP sent to your email')
        else:
            messages.add_message(req, messages.ERROR, 'Error sending OTP')            

    return render(req, "auth/verifyMail.html")


def organisation_view(req, org_name):
    if not (Organisation.objects.filter(name=org_name).exists()):
        return render(req, "errors/organisation_not_found.html", {
            "org_name": org_name,
        })
    org_data = Organisation.objects.get(name=org_name)
    serializer = orgSerlializer(org_data, many=False)
    return render(req, "core/organisation.html", {
        "org_data": serializer.data,
    })
    
def organisation_tournament_view(req, tournament_name):
    if not (Tournament.objects.filter(name=tournament_name).exists()):
        return render(req, "errors/tournament_not_found.html", {
            "tournament_name": tournament_name, 
        })
    tournament = Tournament.objects.get(name=tournament_name)
    serializer = OrgTournamentSerializer(tournament, many=False)
    return render(req, "core/tournament.html", {
        "tournament_data": serializer.data,  
    })

@login_required(login_url="/login/") # maybe rewrite this
def cart_view(req):
    user = User.objects.get(username=req.user)
    cart = user.cart.all()
    cart_data = []
    total = 0
    for item in cart:
        item_dict = {}
        item_dict["members"] = item.members.all()
        item_dict["category"] = item.category
        cart_data.append(item_dict)
        total += item.category.price
    return render(req, "core/cart.html", {
        "cart": cart_data,
        "total":total,
    })