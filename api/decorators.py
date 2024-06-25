from functools import wraps
from django.http import JsonResponse
from django.contrib import messages
from organisers.models import *


def validate_tournament(request, tournament_name):
    tournament = Tournament.objects.filter(name=tournament_name).first()
    if not tournament:
        messages.info(request, 'No Such Tournament Found!')
        return JsonResponse({"error": "No Such Tournament Found!"}, status=404)
        
def validate_category(request, category_name):
    category = Category.objects.filter(catagory_type=category_name).first()
    if not category:
        messages.info(request, 'No Such Category Found!')
        return JsonResponse({"error": "No Such Category Found!"}, status=404)

def validate_match(request, match_id):
    match = Match.objects.filter(id=match_id).first()
    if not match:
        messages.info(request, 'No Such Match Found!')
        return JsonResponse({"error": "No Such Match Found!"}, status=404)

def validate_team(request, team_id):
    team = Team.objects.filter(id=team_id).first()
    if not team:
        messages.info(request, 'No Such Team Found!')
        return JsonResponse({"error": "No Such Team Found!"}, status=404)

def validate_category_in_tournament(request, tournament_name, category_name):
    if not Category.objects.filter(catagory_type=category_name, tournament__name=tournament_name).exists():
        messages.info(request, 'No Such Category Found! in the Tournament')
        return JsonResponse({"error": "No Such Category Found! in the Tournament"}, status=404)


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

def validate_admin(request,tournament_name, admin):
    tournament = Tournament.objects.get(name = tournament_name)
    print(tournament.name)
    print(tournament.org.admin, admin)
    if tournament.org.admin != admin:
        messages.info(request, 'You are not authorised to perform this action!')
        return JsonResponse({"error": "You are not authorised to perform this action!"}, status=401)
    

def login_required(view_func):
    @wraps(view_func)
    @args_validater
    def _wrapped_view(req, *args, **kwargs):
        if not req.user.is_authenticated:
            return JsonResponse({"error": "You Need to be logged in!"}, status=401)
        return view_func(req, *args, **kwargs)
    return _wrapped_view

def organiser_required(view_func):
    @wraps(view_func)
    
    def _wrapped_view(req, *args, **kwargs):
        if not req.user.is_authenticated:
            return JsonResponse({"error": "You Need to be logged in!"}, status=401)
        if not req.user.is_organiser:
            return JsonResponse({"error": "You Need to be an Organiser!"}, status=401)
        return view_func(req, *args, **kwargs)
    return _wrapped_view



def host_required(view_func):
    @wraps(view_func)
    @organiser_required
    @args_validater
    def _wrapped_view(req, *args, **kwargs):
        
        if 'tournament_name' in kwargs:
            tournament_name = kwargs.get('tournament_name')
            admin = req.user
            validate_admin(req, tournament_name, admin)
        
        return view_func(req, *args, **kwargs)
    return _wrapped_view