from django.shortcuts import render
from django.contrib import messages
from .models import *

def validateRegister(req):
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
    return user