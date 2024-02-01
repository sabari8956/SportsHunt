from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url="/accounts/login/")
def index(req):
    if not (req.user.is_organizer):
       return redirect("core:index")
    return HttpResponse("helo Organisers")