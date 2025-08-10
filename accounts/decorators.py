from django.shortcuts import redirect

def role_required(role_name):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if not hasattr(request.user, 'role') or request.user.role != role_name:
                return redirect('no_permission')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
