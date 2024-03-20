from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect, render
from .models import Tournament

def organiser_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, 'You Need to be logged in!')
            return redirect("core:login")
        if not request.user.is_organiser:
            messages.info(request, 'You Need to be an Organiser!')
            return redirect("core:index")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def host_required(function):
    def wrap(request, *args, **kwargs):
        tournament_name = kwargs.get('tournament_name')
        tournament = Tournament.objects.filter(name=tournament_name).first()
        if request.user == tournament.org.admin or request.user in tournament.org.mods.all():
            return function(request, *args, **kwargs)
        else:
            return render(request, "errors/403.html")
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return organiser_required(wrap)
