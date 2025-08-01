from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import uuid
from utils.auth import require_auth
from database import get_db

profiles_bp = Blueprint('profiles', __name__)

@profiles_bp.route('/profiles', methods=['GET', 'POST'])
@require_auth
def profiles():
    """Página de perfis hotspot"""
    if request.method == 'POST':
        company_id = request.form.get('company_id')
        name = request.form.get('name')
        download_limit = request.form.get('download_limit')
        upload_limit = request.form.get('upload_limit')
        time_limit = request.form.get('time_limit')
        
        if not all([company_id, name, download_limit, upload_limit]):
            flash('Campos obrigatórios não preenchidos', 'error')
        else:
            conn = get_db()
            conn.execute('''
                INSERT INTO hotspot_profiles (id, company_id, name, download_limit, upload_limit, time_limit)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (str(uuid.uuid4()), company_id, name, int(download_limit), int(upload_limit), 
                  int(time_limit) if time_limit else None))
            conn.commit()
            conn.close()
            flash('Perfil criado com sucesso!', 'success')
        
        return redirect(url_for('profiles.profiles'))
    
    conn = get_db()
    profiles_list = conn.execute('''
        SELECT p.*, c.name as company_name
        FROM hotspot_profiles p
        JOIN companies c ON p.company_id = c.id
        WHERE p.active = 1
        ORDER BY p.created_at DESC
    ''').fetchall()
    
    companies_list = conn.execute('SELECT * FROM companies WHERE active = 1').fetchall()
    conn.close()
    
    return render_template('profiles.html', 
                         user={'name': session.get('name')}, 
                         profiles_list=profiles_list,
                         companies_list=companies_list)
