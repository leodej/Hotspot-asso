from functools import wraps
from flask import session, redirect, url_for, request

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

def require_admin(f):
    """Decorator para rotas que requerem privilégios de admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_auth():
            return redirect(url_for('auth.login'))
        if session.get('user_type') != 'admin':
            return redirect(url_for('main.user_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def is_admin():
    """Verifica se o usuário é admin"""
    return session.get('user_type') == 'admin'

def is_hotspot_user():
    """Verifica se o usuário é um usuário hotspot"""
    return session.get('user_type') == 'hotspot'
