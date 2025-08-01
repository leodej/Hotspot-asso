from functools import wraps
from flask import session, redirect, url_for

def check_auth():
    """Verifica se o usuário está autenticado"""
    return 'user_id' in session and 'email' in session

def require_auth(f):
    """Decorator para rotas que requerem autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_auth():
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
