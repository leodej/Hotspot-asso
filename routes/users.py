from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import sqlite3
import uuid
from utils.auth import require_auth
from database import get_db

users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['GET', 'POST'])
@require_auth
def users():
    """Página de usuários do sistema"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'user')
        
        if not all([name, email, password]):
            flash('Todos os campos são obrigatórios', 'error')
        else:
            conn = get_db()
            try:
                conn.execute('''
                    INSERT INTO system_users (id, email, password, name, role)
                    VALUES (?, ?, ?, ?, ?)
                ''', (str(uuid.uuid4()), email, password, name, role))
                conn.commit()
                flash('Usuário cadastrado com sucesso!', 'success')
            except sqlite3.IntegrityError:
                flash('Email já existe no sistema', 'error')
            finally:
                conn.close()
        
        return redirect(url_for('users.users'))
    
    # Buscar usuários
    conn = get_db()
    users_list = conn.execute('''
        SELECT * FROM system_users 
        WHERE active = 1 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('users.html', user={'name': session.get('name')}, users_list=users_list)
