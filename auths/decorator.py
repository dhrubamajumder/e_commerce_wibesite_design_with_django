
from django.shortcuts import render
from functools import wraps

def login_required_custom(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, "auths/login_required_message.html")
        return view_func(request, *args, **kwargs)
    return wrapper