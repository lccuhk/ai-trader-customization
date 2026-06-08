from functools import wraps
from flask import request, g
from services.security_service import create_audit_log


def audit_log(action: str, resource_type: str = None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = None
            if hasattr(g, 'current_user') and g.current_user:
                user_id = g.current_user.id

            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent')

            resource_id = kwargs.get('id') or kwargs.get('user_id') or kwargs.get('signal_id')

            old_values = None
            if request.method in ['PUT', 'PATCH', 'DELETE']:
                old_values = {'method': request.method}

            new_values = None
            if request.method in ['POST', 'PUT', 'PATCH']:
                try:
                    new_values = request.get_json(silent=True)
                except:
                    new_values = None

            create_audit_log(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                old_values=old_values,
                new_values=new_values,
                ip_address=ip_address,
                user_agent=user_agent
            )

            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def sensitive_operation(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'current_user') or not g.current_user:
            return {'success': False, 'message': '请先登录', 'code': 401}, 401

        return f(*args, **kwargs)
    
    return decorated_function
