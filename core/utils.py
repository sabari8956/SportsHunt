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
        return False       
    if password != confirmation:
        messages.add_message(req, messages.ERROR, 'Passwords must match.')
        return False
    if User.objects.filter(username=username).exists():
        messages.add_message(req, messages.ERROR, 'Username already taken.')
        return False
        
    elif User.objects.filter(email=email).exists():
        messages.add_message(req, messages.ERROR, 'Email already registed')
        return False
        
    else:
        try:
            user = User.objects.create_user(username, email, password)
            if req.POST.get("is_organiser", False):
                user.is_organiser = True
            user.save()
        except Exception as e:
            messages.add_message(req, messages.ERROR, 'Error: ' + str(e))
            return False
    return user