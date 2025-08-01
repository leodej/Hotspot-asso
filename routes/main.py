from flask import Blueprint, render_template, session
from utils.auth import require_auth
from database import get_db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Página inicial - redireciona para login ou dashboard"""
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@require_auth
def dashboard():
    """Dashboard principal"""
    conn = get_db()
    
    # Estatísticas reais
    stats = {
        'total_users': conn.execute('SELECT COUNT(*) as count FROM hotspot_users WHERE active = 1').fetchone()['count'],
        'active_companies': conn.execute('SELECT COUNT(*) as count FROM companies WHERE active = 1').fetchone()['count'],
        'total_profiles': conn.execute('SELECT COUNT(*) as count FROM hotspot_profiles WHERE active = 1').fetchone()['count'],
        'total_credits_mb': conn.execute('SELECT SUM(remaining_mb) as total FROM user_credits').fetchone()['total'] or 0
    }
    
    # Atividades recentes
    activities = conn.execute('''
        SELECT 'user' as type, 'Novo usuário cadastrado' as title, 
               full_name || ' - ' || datetime(created_at, 'localtime') as description
        FROM hotspot_users 
        WHERE active = 1 
        ORDER BY created_at DESC 
        LIMIT 5
    ''').fetchall()
    
    conn.close()
    
    user_data = {
        'name': session.get('name'),
        'email': session.get('email'),
        'role': session.get('role')
    }
    
    return render_template('dashboard.html', user=user_data, stats=stats, activities=activities)
