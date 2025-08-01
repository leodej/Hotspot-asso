from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from database import get_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not email or not password:
            flash('Email e senha são obrigatórios', 'error')
            return render_template('login.html')
        
        conn = get_db()
        user = conn.execute(
            'SELECT * FROM system_users WHERE email = ? AND password = ? AND active = 1',
            (email, password)
        ).fetchone()
        conn.close()
        
        if user:
            session.permanent = True
            session['user_id'] = user['id']
            session['email'] = user['email']
            session['name'] = user['name']
            session['role'] = user['role']
            session['user_type'] = user['user_type']
            session['hotspot_user_id'] = user['hotspot_user_id']
            session['login_time'] = datetime.now().isoformat()
            
            flash(f'Bem-vindo, {user["name"]}!', 'success')
            
            # Redirecionar baseado no tipo de usuário
            if user['user_type'] == 'hotspot':
                return redirect(url_for('main.user_dashboard'))
            else:
                return redirect(url_for('main.dashboard'))
        else:
            flash('Email ou senha incorretos', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Logout do usuário"""
    session.clear()
    flash('Logout realizado com sucesso', 'info')
    return redirect(url_for('auth.login'))
