from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from .models import *
from django.db import IntegrityError

# Create your views here.
def index(req):
    return render(req, "core/index.html")

def login_view(req):
    if req.method == "POST":
        username = req.POST["username"]
        password = req.POST["password"]
        user = authenticate(req, username=username, password=password)

        if user is not None:
            login(req, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(req, "auth/login.html", {
                "message": "Invalid Username/ Password",
        })
    return render(req, "auth/login.html", {})

def logout_view(req):
    logout(req)
    return HttpResponseRedirect(reverse("index"))

def register_view(req):
    if req.method == "POST":
        username = req.POST["username"].strip()
        email = req.POST["email"]
        password = req.POST["password"]
        confirmation = req.POST["confirmation"]
        
        if not username:
            return render(req, "auth/register.html", {
                "message": "Enter a Valid Username"
            })        
        if password != confirmation:
            return render(req, "auth/register.html", {
                "message": "Passwords must match."
            })
        if User.objects.filter(username=username).exists():
            return render(req, "auth/register.html", {
                "message": "Username already taken."
            })
            
        elif User.objects.filter(email=email).exists():
            return render(req, "auth/register.html", {
                "message": "Email already registed"
            })
            
        else:
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
            except Exception as e:
                return render(req, "auth/register.html", {
                    "message": str(e)
                })
        login(req, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(req, "auth/register.html")
