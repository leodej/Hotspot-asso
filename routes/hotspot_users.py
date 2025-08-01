from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import sqlite3
import uuid
from utils.auth import require_auth
from utils.helpers import get_setting
from database import get_db

hotspot_users_bp = Blueprint('hotspot_users', __name__)

@hotspot_users_bp.route('/hotspot-users', methods=['GET', 'POST'])
@require_auth
def hotspot_users():
    """Página de usuários hotspot"""
    if request.method == 'POST':
        company_id = request.form.get('company_id')
        profile_id = request.form.get('profile_id')
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        if not all([company_id, username, password]):
            flash('Campos obrigatórios não preenchidos', 'error')
        else:
            conn = get_db()
            try:
                user_id = str(uuid.uuid4())
                conn.execute('''
                    INSERT INTO hotspot_users (id, company_id, profile_id, username, password, full_name, email, phone)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, company_id, profile_id, username, password, full_name, email, phone))
                
                # Criar crédito inicial
                default_credit = int(get_setting('default_credit_mb', 1024))
                conn.execute('''
                    INSERT INTO user_credits (id, hotspot_user_id, total_mb, remaining_mb, last_reset)
                    VALUES (?, ?, ?, ?, DATE('now'))
                ''', (str(uuid.uuid4()), user_id, default_credit, default_credit))
                
                conn.commit()
                flash('Usuário hotspot criado com sucesso!', 'success')
            except sqlite3.IntegrityError:
                flash('Username já existe', 'error')
            finally:
                conn.close()
        
        return redirect(url_for('hotspot_users.hotspot_users'))
    
    conn = get_db()
    hotspot_users_list = conn.execute('''
        SELECT hu.*, c.name as company_name, p.name as profile_name,
               uc.total_mb, uc.used_mb, uc.remaining_mb
        FROM hotspot_users hu
        JOIN companies c ON hu.company_id = c.id
        LEFT JOIN hotspot_profiles p ON hu.profile_id = p.id
        LEFT JOIN user_credits uc ON hu.id = uc.hotspot_user_id
        WHERE hu.active = 1
        ORDER BY hu.created_at DESC
    ''').fetchall()
    
    companies_list = conn.execute('SELECT * FROM companies WHERE active = 1').fetchall()
    profiles_list = conn.execute('SELECT * FROM hotspot_profiles WHERE active = 1').fetchall()
    conn.close()
    
    return render_template('hotspot_users.html', 
                         user={'name': session.get('name')}, 
                         hotspot_users_list=hotspot_users_list,
                         companies_list=companies_list,
                         profiles_list=profiles_list)
