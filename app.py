from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import os
import json
from datetime import datetime, timedelta
import hashlib

app = Flask(__name__)
app.secret_key = 'mikrotik-manager-super-secret-key-2024'

# Configurações
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Usuários demo (em produção usar banco de dados)
USERS = {
    'admin@demo.com': {
        'password': 'admin123',
        'name': 'Administrador Sistema',
        'role': 'admin',
        'id': '1'
    },
    'manager@demo.com': {
        'password': 'manager123',
        'name': 'Gerente',
        'role': 'manager',
        'id': '2'
    },
    'user@demo.com': {
        'password': 'user123',
        'name': 'Usuário Padrão',
        'role': 'user',
        'id': '3'
    }
}

def check_auth():
    """Verifica se o usuário está autenticado"""
    return 'user_id' in session and 'email' in session

def require_auth(f):
    """Decorator para rotas que requerem autenticação"""
    def decorated_function(*args, **kwargs):
        if not check_auth():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    """Página inicial - redireciona para login ou dashboard"""
    if check_auth():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        print(f"[LOGIN] Tentativa de login: {email}")
        
        if not email or not password:
            flash('Email e senha são obrigatórios', 'error')
            return render_template('login.html')
        
        # Verificar credenciais
        if email in USERS and USERS[email]['password'] == password:
            user = USERS[email]
            
            # Criar sessão
            session.permanent = True
            session['user_id'] = user['id']
            session['email'] = email
            session['name'] = user['name']
            session['role'] = user['role']
            session['login_time'] = datetime.now().isoformat()
            
            print(f"[LOGIN] Login realizado com sucesso: {email}")
            flash(f'Bem-vindo, {user["name"]}!', 'success')
            
            return redirect(url_for('dashboard'))
        else:
            print(f"[LOGIN] Credenciais inválidas: {email}")
            flash('Email ou senha incorretos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout do usuário"""
    email = session.get('email', 'Usuário desconhecido')
    print(f"[LOGOUT] Logout realizado: {email}")
    
    session.clear()
    flash('Logout realizado com sucesso', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@require_auth
def dashboard():
    """Dashboard principal"""
    user_data = {
        'name': session.get('name'),
        'email': session.get('email'),
        'role': session.get('role'),
        'login_time': session.get('login_time')
    }
    
    # Estatísticas demo
    stats = {
        'total_users': 156,
        'active_companies': 12,
        'active_connections': 89,
        'total_credits': 25000
    }
    
    # Atividades recentes
    activities = [
        {'type': 'success', 'title': 'Novo usuário cadastrado', 'description': 'João Silva - há 5 minutos'},
        {'type': 'info', 'title': 'Roteador conectado', 'description': '192.168.1.1 - há 12 minutos'},
        {'type': 'warning', 'title': 'Backup realizado', 'description': 'Sistema - há 1 hora'},
        {'type': 'success', 'title': 'Login realizado', 'description': f'{user_data["name"]} - agora mesmo'}
    ]
    
    return render_template('dashboard.html', user=user_data, stats=stats, activities=activities)

@app.route('/users')
@require_auth
def users():
    """Página de usuários"""
    return render_template('users.html', user={'name': session.get('name')})

@app.route('/companies')
@require_auth
def companies():
    """Página de empresas"""
    return render_template('companies.html', user={'name': session.get('name')})

@app.route('/profiles')
@require_auth
def profiles():
    """Página de perfis hotspot"""
    return render_template('profiles.html', user={'name': session.get('name')})

@app.route('/hotspot-users')
@require_auth
def hotspot_users():
    """Página de usuários hotspot"""
    return render_template('hotspot_users.html', user={'name': session.get('name')})

@app.route('/credits')
@require_auth
def credits():
    """Página de créditos"""
    return render_template('credits.html', user={'name': session.get('name')})

@app.route('/reports')
@require_auth
def reports():
    """Página de relatórios"""
    return render_template('reports.html', user={'name': session.get('name')})

@app.route('/settings')
@require_auth
def settings():
    """Página de configurações"""
    return render_template('settings.html', user={'name': session.get('name')})

# API Routes
@app.route('/api/health')
def api_health():
    """Health check da API"""
    return jsonify({
        'status': 'ok',
        'message': 'MikroTik Manager API funcionando',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/stats')
@require_auth
def api_stats():
    """API de estatísticas"""
    return jsonify({
        'total_users': 156,
        'active_companies': 12,
        'active_connections': 89,
        'total_credits': 25000,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Iniciando MikroTik Manager Flask...")
    print("📧 Login: admin@demo.com")
    print("🔑 Senha: admin123")
    print("🌐 URL: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
