from flask import Blueprint, render_template, session, redirect, url_for, request
from utils.auth import require_auth, require_admin, is_admin
from utils.helpers import format_mb_to_gb
from database import get_db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Página inicial - redireciona para login ou dashboard"""
    if 'user_id' in session:
        if session.get('user_type') == 'hotspot':
            return redirect(url_for('main.user_dashboard'))
        else:
            return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@require_admin
def dashboard():
    """Dashboard principal para administradores"""
    conn = get_db()
    
    # Filtro por empresa
    company_filter = request.args.get('company_id', '')
    
    # Query base para estatísticas
    base_query = ""
    params = []
    
    if company_filter:
        base_query = " AND company_id = ?"
        params = [company_filter]
    
    # Estatísticas reais
    stats = {
        'total_users': conn.execute(f'SELECT COUNT(*) as count FROM hotspot_users WHERE active = 1{base_query}', params).fetchone()['count'],
        'active_companies': conn.execute('SELECT COUNT(*) as count FROM companies WHERE active = 1').fetchone()['count'],
        'total_profiles': conn.execute('SELECT COUNT(*) as count FROM hotspot_profiles WHERE active = 1').fetchone()['count'],
        'total_credits_mb': conn.execute(f'''
            SELECT SUM(uc.remaining_mb) as total 
            FROM user_credits uc 
            JOIN hotspot_users hu ON uc.hotspot_user_id = hu.id 
            WHERE hu.active = 1{base_query}
        ''', params).fetchone()['total'] or 0
    }
    
    # Atividades recentes
    activities_query = f'''
        SELECT 'user' as type, 'Novo usuário cadastrado' as title, 
               hu.full_name || ' - ' || datetime(hu.created_at, 'localtime') as description,
               c.name as company_name
        FROM hotspot_users hu
        JOIN companies c ON hu.company_id = c.id
        WHERE hu.active = 1{base_query}
        ORDER BY hu.created_at DESC 
        LIMIT 10
    '''
    activities = conn.execute(activities_query, params).fetchall()
    
    # Lista de empresas para o filtro
    companies = conn.execute('SELECT * FROM companies WHERE active = 1 ORDER BY name').fetchall()
    
    conn.close()
    
    user_data = {
        'name': session.get('name'),
        'email': session.get('email'),
        'role': session.get('role')
    }
    
    return render_template('dashboard.html', 
                         user=user_data, 
                         stats=stats, 
                         activities=activities,
                         companies=companies,
                         selected_company=company_filter,
                         format_mb_to_gb=format_mb_to_gb)

@main_bp.route('/user-dashboard')
@require_auth
def user_dashboard():
    """Dashboard específico para usuários hotspot"""
    if session.get('user_type') != 'hotspot':
        return redirect(url_for('main.dashboard'))
    
    conn = get_db()
    
    # Buscar dados do usuário hotspot
    hotspot_user_id = session.get('hotspot_user_id')
    
    user_data = conn.execute('''
        SELECT hu.*, c.name as company_name, p.name as profile_name,
               uc.total_mb, uc.used_mb, uc.remaining_mb, uc.last_reset
        FROM hotspot_users hu
        JOIN companies c ON hu.company_id = c.id
        LEFT JOIN hotspot_profiles p ON hu.profile_id = p.id
        LEFT JOIN user_credits uc ON hu.id = uc.hotspot_user_id
        WHERE hu.id = ?
    ''', (hotspot_user_id,)).fetchone()
    
    # Histórico de uso dos últimos 7 dias (simulado)
    usage_history = []
    for i in range(7):
        usage_history.append({
            'date': f'2024-01-{25+i:02d}',
            'used_mb': (i + 1) * 50,
            'remaining_mb': user_data['remaining_mb'] if user_data else 0
        })
    
    conn.close()
    
    session_data = {
        'name': session.get('name'),
        'email': session.get('email')
    }
    
    return render_template('user_dashboard.html', 
                         user=session_data,
                         hotspot_user=user_data,
                         usage_history=usage_history,
                         format_mb_to_gb=format_mb_to_gb)
