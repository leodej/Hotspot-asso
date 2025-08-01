from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import hashlib
from datetime import datetime
from utils.auth import login_required

hotspot_users_bp = Blueprint('hotspot_users', __name__)

@hotspot_users_bp.route('/hotspot-users')
@login_required
def hotspot_users():
    conn = sqlite3.connect('mikrotik_manager.db')
    cursor = conn.cursor()
    
    # Obter filtro de empresa
    company_filter = request.args.get('company', '')
    
    # Buscar usuários hotspot com filtro
    if company_filter:
        cursor.execute('''
            SELECT hu.id, hu.username, hu.email, hu.created_at, hu.status,
                   c.name as company_name, p.name as profile_name,
                   cr.credits_mb, cr.used_credits_mb
            FROM hotspot_users hu
            JOIN companies c ON hu.company_id = c.id
            LEFT JOIN profiles p ON hu.profile_id = p.id
            LEFT JOIN credits cr ON hu.id = cr.hotspot_user_id
            WHERE hu.company_id = ?
            ORDER BY hu.created_at DESC
        ''', (company_filter,))
    else:
        cursor.execute('''
            SELECT hu.id, hu.username, hu.email, hu.created_at, hu.status,
                   c.name as company_name, p.name as profile_name,
                   cr.credits_mb, cr.used_credits_mb
            FROM hotspot_users hu
            JOIN companies c ON hu.company_id = c.id
            LEFT JOIN profiles p ON hu.profile_id = p.id
            LEFT JOIN credits cr ON hu.id = cr.hotspot_user_id
            ORDER BY hu.created_at DESC
        ''')
    
    users = cursor.fetchall()
    
    # Buscar empresas para o filtro
    cursor.execute('SELECT id, name FROM companies ORDER BY name')
    companies = cursor.fetchall()
    
    # Buscar perfis
    cursor.execute('SELECT id, name FROM profiles ORDER BY name')
    profiles = cursor.fetchall()
    
    conn.close()
    
    return render_template('hotspot_users.html', 
                         users=users, 
                         companies=companies, 
                         profiles=profiles,
                         selected_company=company_filter)

@hotspot_users_bp.route('/hotspot-users/add', methods=['POST'])
@login_required
def add_hotspot_user():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email', '')
    name = request.form.get('name', '')
    company_id = request.form.get('company_id')
    profile_id = request.form.get('profile_id')
    
    if not username or not password or not company_id:
        flash('Username, senha e empresa são obrigatórios', 'error')
        return redirect(url_for('hotspot_users.hotspot_users'))
    
    conn = sqlite3.connect('mikrotik_manager.db')
    cursor = conn.cursor()
    
    try:
        # Verificar se username já existe
        cursor.execute('SELECT id FROM hotspot_users WHERE username = ?', (username,))
        if cursor.fetchone():
            flash('Username já existe', 'error')
            return redirect(url_for('hotspot_users.hotspot_users'))
        
        # Inserir usuário hotspot
        cursor.execute('''
            INSERT INTO hotspot_users (username, password, email, name, company_id, profile_id, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'active', ?)
        ''', (username, password, email, name, company_id, profile_id or None, datetime.now()))
        
        hotspot_user_id = cursor.lastrowid
        
        # Se email e nome foram fornecidos, criar usuário do sistema
        if email and name:
            # Verificar se já existe usuário com este email
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            existing_user = cursor.fetchone()
            
            if not existing_user:
                # Criar hash da senha
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                
                # Inserir usuário do sistema
                cursor.execute('''
                    INSERT INTO users (name, email, password, user_type, created_at)
                    VALUES (?, ?, ?, 'hotspot', ?)
                ''', (name, email, password_hash, datetime.now()))
                
                system_user_id = cursor.lastrowid
                
                # Atualizar hotspot_user com user_id
                cursor.execute('UPDATE hotspot_users SET user_id = ? WHERE id = ?', 
                             (system_user_id, hotspot_user_id))
        
        # Obter configurações de crédito padrão
        cursor.execute('SELECT default_credits_mb FROM settings WHERE id = 1')
        settings = cursor.fetchone()
        default_credits = settings[0] if settings else 1024  # 1GB padrão
        
        # Criar registro de créditos
        cursor.execute('''
            INSERT INTO credits (hotspot_user_id, credits_mb, used_credits_mb, last_reset, cumulative_credits_mb)
            VALUES (?, ?, 0, ?, 0)
        ''', (hotspot_user_id, default_credits, datetime.now()))
        
        conn.commit()
        flash('Usuário hotspot criado com sucesso!', 'success')
        
    except Exception as e:
        conn.rollback()
        flash(f'Erro ao criar usuário: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('hotspot_users.hotspot_users'))

@hotspot_users_bp.route('/hotspot-users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_hotspot_user(user_id):
    conn = sqlite3.connect('mikrotik_manager.db')
    cursor = conn.cursor()
    
    try:
        # Buscar user_id do sistema associado
        cursor.execute('SELECT user_id FROM hotspot_users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        system_user_id = result[0] if result else None
        
        # Deletar créditos
        cursor.execute('DELETE FROM credits WHERE hotspot_user_id = ?', (user_id,))
        
        # Deletar usuário hotspot
        cursor.execute('DELETE FROM hotspot_users WHERE id = ?', (user_id,))
        
        # Deletar usuário do sistema se existir
        if system_user_id:
            cursor.execute('DELETE FROM users WHERE id = ?', (system_user_id,))
        
        conn.commit()
        flash('Usuário deletado com sucesso!', 'success')
        
    except Exception as e:
        conn.rollback()
        flash(f'Erro ao deletar usuário: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('hotspot_users.hotspot_users'))

@hotspot_users_bp.route('/hotspot-users/toggle-status/<int:user_id>', methods=['POST'])
@login_required
def toggle_status(user_id):
    conn = sqlite3.connect('mikrotik_manager.db')
    cursor = conn.cursor()
    
    try:
        # Obter status atual
        cursor.execute('SELECT status FROM hotspot_users WHERE id = ?', (user_id,))
        current_status = cursor.fetchone()[0]
        
        # Alternar status
        new_status = 'inactive' if current_status == 'active' else 'active'
        cursor.execute('UPDATE hotspot_users SET status = ? WHERE id = ?', (new_status, user_id))
        
        conn.commit()
        flash(f'Status alterado para {new_status}!', 'success')
        
    except Exception as e:
        conn.rollback()
        flash(f'Erro ao alterar status: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('hotspot_users.hotspot_users'))
