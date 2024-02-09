from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect

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

