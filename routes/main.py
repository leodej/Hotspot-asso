from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, flash
import sqlite3
from datetime import datetime, timedelta
from utils.auth import login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if 'user_id' in session:
        # Verificar tipo de usuário
        conn = sqlite3.connect('mikrotik_manager.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_type FROM users WHERE id = ?', (session['user_id'],))
        user = cursor.fetchone()
        conn.close()
        
        if user and user[0] == 'hotspot':
            return redirect(url_for('main.user_dashboard'))
        else:
            return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Verificar se é admin
    conn = sqlite3.connect('mikrotik_manager.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_type FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    
    if not user or user[0] != 'admin':
        return redirect(url_for('main.user_dashboard'))
    
    # Obter filtro de empresa
    company_filter = request.args.get('company', '')
    
    # Estatísticas gerais
    if company_filter:
        cursor.execute('SELECT COUNT(*) FROM companies WHERE id = ?', (company_filter,))
        total_companies = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM hotspot_users WHERE company_id = ?', (company_filter,))
        total_hotspot_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM profiles WHERE company_id = ?', (company_filter,))
        total_profiles = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE user_type = "hotspot" AND id IN (SELECT user_id FROM hotspot_users WHERE company_id = ?)', (company_filter,))
        total_users = cursor.fetchone()[0]
    else:
        cursor.execute('SELECT COUNT(*) FROM companies')
        total_companies = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM hotspot_users')
        total_hotspot_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM profiles')
        total_profiles = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE user_type = "hotspot"')
        total_users = cursor.fetchone()[0]
    
    # Obter lista de empresas para o filtro
    cursor.execute('SELECT id, name FROM companies ORDER BY name')
    companies = cursor.fetchall()
    
    # Usuários recentes
    if company_filter:
        cursor.execute('''
            SELECT hu.username, hu.created_at, c.name as company_name 
            FROM hotspot_users hu 
            JOIN companies c ON hu.company_id = c.id 
            WHERE hu.company_id = ?
            ORDER BY hu.created_at DESC LIMIT 5
        ''', (company_filter,))
    else:
        cursor.execute('''
            SELECT hu.username, hu.created_at, c.name as company_name 
            FROM hotspot_users hu 
            JOIN companies c ON hu.company_id = c.id 
            ORDER BY hu.created_at DESC LIMIT 5
        ''')
    recent_users = cursor.fetchall()
    
    # Créditos por empresa
    if company_filter:
        cursor.execute('''
            SELECT c.name, 
                   COALESCE(SUM(cr.credits_mb), 0) as total_credits,
                   COALESCE(SUM(cr.used_credits_mb), 0) as used_credits
            FROM companies c 
            LEFT JOIN hotspot_users hu ON c.id = hu.company_id
            LEFT JOIN credits cr ON hu.id = cr.hotspot_user_id
            WHERE c.id = ?
            GROUP BY c.id, c.name
        ''', (company_filter,))
    else:
        cursor.execute('''
            SELECT c.name, 
                   COALESCE(SUM(cr.credits_mb), 0) as total_credits,
                   COALESCE(SUM(cr.used_credits_mb), 0) as used_credits
            FROM companies c 
            LEFT JOIN hotspot_users hu ON c.id = hu.company_id
            LEFT JOIN credits cr ON hu.id = cr.hotspot_user_id
            GROUP BY c.id, c.name
            ORDER BY total_credits DESC LIMIT 10
        ''')
    credits_by_company = cursor.fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', 
                         total_companies=total_companies,
                         total_hotspot_users=total_hotspot_users,
                         total_profiles=total_profiles,
                         total_users=total_users,
                         recent_users=recent_users,
                         credits_by_company=credits_by_company,
                         companies=companies,
                         selected_company=company_filter)

@main_bp.route('/user-dashboard')
@login_required
def user_dashboard():
    # Verificar se é usuário hotspot
    conn = sqlite3.connect('mikrotik_manager.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_type, email FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    
    if not user or user[0] != 'hotspot':
        return redirect(url_for('main.dashboard'))
    
    # Buscar dados do usuário hotspot
    cursor.execute('''
        SELECT hu.username, hu.email, c.name as company_name,
               p.name as profile_name, p.speed_limit
        FROM hotspot_users hu
        JOIN companies c ON hu.company_id = c.id
        LEFT JOIN profiles p ON hu.profile_id = p.id
        WHERE hu.email = ? OR hu.username = ?
    ''', (user[1], user[1]))
    hotspot_user = cursor.fetchone()
    
    if not hotspot_user:
        flash('Usuário hotspot não encontrado', 'error')
        return redirect(url_for('auth.logout'))
    
    # Buscar créditos
    cursor.execute('''
        SELECT hu.id FROM hotspot_users hu WHERE hu.email = ? OR hu.username = ?
    ''', (user[1], user[1]))
    hotspot_user_id = cursor.fetchone()
    
    if hotspot_user_id:
        cursor.execute('''
            SELECT credits_mb, used_credits_mb, last_reset, cumulative_credits_mb
            FROM credits WHERE hotspot_user_id = ?
        ''', (hotspot_user_id[0],))
        credits = cursor.fetchone()
    else:
        credits = None
    
    # Histórico de uso (últimos 7 dias)
    if hotspot_user_id:
        cursor.execute('''
            SELECT DATE(created_at) as date, SUM(used_credits_mb) as daily_usage
            FROM credits 
            WHERE hotspot_user_id = ? AND created_at >= date('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        ''', (hotspot_user_id[0],))
        usage_history = cursor.fetchall()
    else:
        usage_history = []
    
    conn.close()
    
    # Calcular dados para exibição
    if credits:
        total_credits_mb = credits[0] or 0
        used_credits_mb = credits[1] or 0
        remaining_credits_mb = max(0, total_credits_mb - used_credits_mb)
        usage_percentage = (used_credits_mb / total_credits_mb * 100) if total_credits_mb > 0 else 0
        
        # Converter para GB se necessário
        if total_credits_mb >= 1024:
            total_credits_display = f"{total_credits_mb / 1024:.2f} GB"
            remaining_credits_display = f"{remaining_credits_mb / 1024:.2f} GB"
            used_credits_display = f"{used_credits_mb / 1024:.2f} GB"
        else:
            total_credits_display = f"{total_credits_mb} MB"
            remaining_credits_display = f"{remaining_credits_mb} MB"
            used_credits_display = f"{used_credits_mb} MB"
    else:
        total_credits_mb = 0
        used_credits_mb = 0
        remaining_credits_mb = 0
        usage_percentage = 0
        total_credits_display = "0 MB"
        remaining_credits_display = "0 MB"
        used_credits_display = "0 MB"
    
    return render_template('user_dashboard.html',
                         hotspot_user=hotspot_user,
                         total_credits_display=total_credits_display,
                         remaining_credits_display=remaining_credits_display,
                         used_credits_display=used_credits_display,
                         usage_percentage=usage_percentage,
                         usage_history=usage_history,
                         last_reset=credits[2] if credits else None)

@main_bp.route('/api/user-credits')
@login_required
def api_user_credits():
    """API para atualizar créditos do usuário em tempo real"""
    if session.get('user_type') != 'hotspot':
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = sqlite3.connect('mikrotik_manager.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT credits_mb, used_credits_mb
        FROM hotspot_users
        WHERE email = ?
    ''', (session.get('email'),))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        credits_mb, used_credits_mb = result
        remaining = credits_mb - used_credits_mb
        usage_percent = (used_credits_mb / credits_mb * 100) if credits_mb > 0 else 0
        
        return jsonify({
            'credits_mb': credits_mb,
            'used_credits_mb': used_credits_mb,
            'remaining_credits': max(remaining, 0),
            'usage_percent': min(usage_percent, 100)
        })
    
    return jsonify({'error': 'User not found'}), 404
