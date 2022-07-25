from django.shortcuts import redirect
from functools import wraps


def superuser_required(redirect_url):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                return redirect(redirect_url)

        return _wrapped_view

    return decorator
