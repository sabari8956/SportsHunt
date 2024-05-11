from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect, render
from .models import *
from api.serializer import decoratorTournamentHostValidator, decoratorOrgSerializer

def args_validater(view_func):
    #  in future add a parameter to the decorator and redirect it there.
    # like if its in a tournament, redirect to the same tournament page.
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'tournament_name' in kwargs:
            tournament_name = kwargs.get('tournament_name')
            tournament = Tournament.objects.filter(name=tournament_name).first()
            if not tournament:
                messages.info(request, 'No Such Tournament Found!')
                return redirect("core:index")
            # in future add a 404 url page.
            
        if 'category_name' in kwargs:
            category_name = kwargs.get('category_name')
            category = Category.filter(catagory_type=category_name).first()
            if not category:
                messages.info(request, 'No Such Category Found!')
                return redirect("core:index")
            # in future add a 404 url page.
        
        if 'match_id' in kwargs:
            match_id = kwargs.get('match_id')
            match = Match.objects.filter(id=match_id).first()
            if not match:
                messages.info(request, 'No Such Match Found!')
                return redirect("core:index")
            # in future add a 404 url page.
            
        if 'team_id' in kwargs:
            team_id = kwargs.get('team_id')
            team = Team.objects.filter(id=team_id).first()
            if not team:
                messages.info(request, 'No Such Team Found!')
                return redirect("core:index")
            # in future add a 404 url page.
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def organiser_required(view_func):
    # IMP DURING TESTING CHECK FOR INF REDIRECTS
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
    @wraps(view_func)
    @args_validater
    @organiser_required
    def _wrapped_view(request, *args, **kwargs):
        
        if 'tournament_name' in kwargs:
            tournament_name = kwargs.get('tournament_name')
            tournament = Tournament.objects.filter(name=tournament_name).first()
            serializer = decoratorTournamentHostValidator(tournament).data
            
            is_admin = request.user.id == serializer["org"]["admin"]
            is_mod = request.user.id in serializer["org"]["mods"] or request.user.id in serializer["mods"]
            
            if not (is_admin or is_mod):
                messages.info(request, 'You Need to be a Host!')
                return redirect("core:index")
            
            # in future add a 404 url page.
        else:
            raise ValueError('No Tournament Name argument found in the view function')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def OrgHost_required(view_func):
    @organiser_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if org := request.session.get('organisation'):
            org = Organisation.objects.filter(id=org).first()
            serializer = decoratorOrgSerializer(org).data
            print(serializer['admin'] == request.user.id)
            if not serializer:
                messages.info(request, 'No Organisation Found!')
                return redirect("organisers:orgs") # check if the user has an organisation
            
            if (request.user.id != serializer['admin'] or request.user.id in serializer['mods']):
                messages.info(request, 'wtf! You are not in this organisation!')
                return redirect("organisers:orgs") # check if the user has an organisation or create one.
            
        else:
            # when coming from organiser:orgs, it creates a inf loop, so i just removed the decorator.
            return redirect("organisers:orgs") # check if the user has an organisation or create one.
        return view_func(request, *args, **kwargs)
    return _wrapped_view