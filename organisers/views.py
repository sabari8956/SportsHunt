from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.
@login_required(login_url="/login/")
def index(req):
    if not (req.user.is_organizer):
        messages.add_message(req, messages.INFO, 'You Need to be a Organiser!')
        return redirect("core:index")
    return HttpResponse("helo Organisers")

@login_required(login_url="/login/")
def organisation_creation_form(req):
    if not (req.user.is_organizer):
        messages.add_message(req, messages.INFO, 'You Need to be a Organiser!')
        return redirect("core:index")
    if req.method == 'POST':
        print(req.POST)
    return render(req, "organisers/organisation_form.html")