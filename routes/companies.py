from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import sqlite3
import uuid
from utils.auth import require_admin
from database import get_db

companies_bp = Blueprint('companies', __name__)

@companies_bp.route('/companies', methods=['GET', 'POST'])
@require_admin
def companies():
    """Página de empresas"""
    if request.method == 'POST':
        name = request.form.get('name')
        mikrotik_ip = request.form.get('mikrotik_ip')
        mikrotik_port = request.form.get('mikrotik_port', 8728)
        mikrotik_user = request.form.get('mikrotik_user')
        mikrotik_password = request.form.get('mikrotik_password')
        
        if not all([name, mikrotik_ip, mikrotik_user, mikrotik_password]):
            flash('Todos os campos são obrigatórios', 'error')
        else:
            conn = get_db()
            conn.execute('''
                INSERT INTO companies (id, name, mikrotik_ip, mikrotik_port, mikrotik_user, mikrotik_password)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (str(uuid.uuid4()), name, mikrotik_ip, int(mikrotik_port), mikrotik_user, mikrotik_password))
            conn.commit()
            conn.close()
            flash('Empresa cadastrada com sucesso!', 'success')
        
        return redirect(url_for('companies.companies'))
    
    # Buscar empresas
    conn = get_db()
    companies_list = conn.execute('''
        SELECT *, 
               (SELECT COUNT(*) FROM hotspot_users WHERE company_id = companies.id AND active = 1) as user_count
        FROM companies 
        WHERE active = 1 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('companies.html', user={'name': session.get('name')}, companies_list=companies_list)
