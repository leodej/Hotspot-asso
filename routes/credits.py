from flask import Blueprint, render_template, session
from utils.auth import require_auth
from database import get_db

credits_bp = Blueprint('credits', __name__)

@credits_bp.route('/credits')
@require_auth
def credits():
    """Página de créditos"""
    conn = get_db()
    
    # Estatísticas de créditos
    stats = {
        'total_credits_mb': conn.execute('SELECT SUM(total_mb) as total FROM user_credits').fetchone()['total'] or 0,
        'used_credits_mb': conn.execute('SELECT SUM(used_mb) as total FROM user_credits').fetchone()['total'] or 0,
        'remaining_credits_mb': conn.execute('SELECT SUM(remaining_mb) as total FROM user_credits').fetchone()['total'] or 0,
        'active_users': conn.execute('SELECT COUNT(*) as count FROM hotspot_users WHERE active = 1').fetchone()['count']
    }
    
    # Lista de créditos por usuário
    credits_list = conn.execute('''
        SELECT hu.username, hu.full_name, c.name as company_name,
               uc.total_mb, uc.used_mb, uc.remaining_mb, uc.last_reset, uc.updated_at
        FROM user_credits uc
        JOIN hotspot_users hu ON uc.hotspot_user_id = hu.id
        JOIN companies c ON hu.company_id = c.id
        WHERE hu.active = 1
        ORDER BY uc.updated_at DESC
    ''').fetchall()
    
    conn.close()
    
    return render_template('credits.html', 
                         user={'name': session.get('name')}, 
                         stats=stats,
                         credits_list=credits_list)
