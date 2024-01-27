from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse

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
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))