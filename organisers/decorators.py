from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect, render
from .models import *
from api.serializer import decoratorTournamentHostValidator, decoratorOrgSerializer

def validate_tournament(request, tournament_name):
    tournament = Tournament.objects.filter(name=tournament_name).first()
    if not tournament:
        messages.info(request, 'No Such Tournament Found!')
        return render(request, "errors/tournament_not_found.html", {
            "tournament_name": tournament_name, 
        })
        
def validate_category(request, category_name):
    category = Category.objects.filter(catagory_type=category_name).first()
    if not category:
        messages.info(request, 'No Such Category Found!')
        return redirect("core:index")

def validate_match(request, match_id):
    match = Match.objects.filter(id=match_id).first()
    if not match:
        messages.info(request, 'No Such Match Found!')
        return redirect("core:index")

def validate_team(request, team_id):
    team = Team.objects.filter(id=team_id).first()
    if not team:
        messages.info(request, 'No Such Team Found!')
        return redirect("core:index")

def validate_category_in_tournament(request, tournament_name, category_name):
    if not Category.objects.filter(catagory_type=category_name, tournament__name=tournament_name).exists():
        messages.info(request, 'No Such Category Found! in the Tournament')
        return redirect("core:index")

def args_validater(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'tournament_name' in kwargs:
            tournament_name = kwargs.get('tournament_name')
            validate_tournament(request, tournament_name)
              
        if 'category_name' in kwargs:
            category_name = kwargs.get('category_name')
            validate_category(request, category_name)
        
        if 'match_id' in kwargs:
            match_id = kwargs.get('match_id')
            validate_match(request, match_id)
        
        if 'team_id' in kwargs:
            team_id = kwargs.get('team_id')
            validate_team(request, team_id)
        
        if 'tournament_name' in kwargs and 'category_name' in kwargs:
            tournament_name = kwargs.get('tournament_name')
            category_name = kwargs.get('category_name')
            validate_category_in_tournament(request, tournament_name, category_name)
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def organiser_required(view_func):
    @wraps(view_func)
    @args_validater
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, 'You Need to be logged in!')
            return redirect("core:login")
        
        if not request.user.is_organiser:
            messages.info(request, 'You Need to be an Organiser!')
            return redirect("core:index")

        return view_func(request, *args, **kwargs)
    return _wrapped_view


def host_required(view_func):
    @organiser_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if org := request.session.get('organisation'):
            org = Organisation.objects.filter(id=org).first()
            serializer = decoratorOrgSerializer(org).data
            if not serializer:
                messages.info(request, 'No Organisation Found!')
                return redirect("organisers:orgs") # check if the user has an organisation
            
            if (request.user.id != serializer['admin'] or request.user.id in serializer['mods']):
                messages.info(request, 'wtf! You are not in this organisation!')
                return redirect("organisers:orgs") # check if the user has an organisation or create one.
            
            if 'tournament_name' in kwargs:
                tournament_name = kwargs.get('tournament_name')
                tournament = Tournament.objects.filter(name=tournament_name).first()
                serializer = decoratorTournamentHostValidator(tournament).data
                
                is_admin = request.user.id == serializer["org"]["admin"]
                is_mod = request.user.id in serializer["org"]["mods"] or request.user.id in serializer["mods"]
                
                if not (is_admin or is_mod):
                    messages.info(request, 'You Need to be a Host!')
                    return redirect("core:index")

            
        else:
            return redirect("organisers:orgs")
        return view_func(request, *args, **kwargs)
    return _wrapped_view