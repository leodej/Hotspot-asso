from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import os
import json
from datetime import datetime, timedelta
import hashlib
import sqlite3
import uuid

app = Flask(__name__)
app.secret_key = 'mikrotik-manager-super-secret-key-2024'

# Configurações
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Inicializar banco de dados SQLite
def init_db():
    conn = sqlite3.connect('mikrotik_manager.db')
    cursor = conn.cursor()
    
    # Tabela de usuários do sistema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de empresas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            mikrotik_ip TEXT NOT NULL,
            mikrotik_port INTEGER DEFAULT 8728,
            mikrotik_user TEXT NOT NULL,
            mikrotik_password TEXT NOT NULL,
            turma_ativa TEXT DEFAULT 'A',
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de perfis hotspot
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hotspot_profiles (
            id TEXT PRIMARY KEY,
            company_id TEXT,
            name TEXT NOT NULL,
            download_limit INTEGER NOT NULL,
            upload_limit INTEGER NOT NULL,
            time_limit INTEGER,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    ''')
    
    # Tabela de usuários hotspot
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hotspot_users (
            id TEXT PRIMARY KEY,
            company_id TEXT,
            profile_id TEXT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            full_name TEXT,
            phone TEXT,
            turma TEXT DEFAULT 'A',
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id),
            FOREIGN KEY (profile_id) REFERENCES hotspot_profiles (id)
        )
    ''')
    
    # Tabela de créditos (em MB)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_credits (
            id TEXT PRIMARY KEY,
            hotspot_user_id TEXT,
            total_mb INTEGER DEFAULT 0,
            used_mb INTEGER DEFAULT 0,
            remaining_mb INTEGER DEFAULT 0,
            last_reset DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (hotspot_user_id) REFERENCES hotspot_users (id)
        )
    ''')
    
    # Tabela de configurações
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_settings (
            id TEXT PRIMARY KEY,
            key TEXT UNIQUE NOT NULL,
            value TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Inserir usuário admin padrão
    cursor.execute('''
        INSERT OR IGNORE INTO system_users (id, email, password, name, role)
        VALUES (?, ?, ?, ?, ?)
    ''', (str(uuid.uuid4()), 'admin@demo.com', 'admin123', 'Administrador Sistema', 'admin'))
    
    # Inserir configurações padrão
    settings = [
        ('default_credit_mb', '1024', 'Crédito padrão em MB para novos usuários'),
        ('credit_reset_time', '00:00', 'Horário de reset dos créditos diários'),
        ('enable_cumulative', '1', 'Habilitar créditos cumulativos'),
        ('system_timezone', 'America/Sao_Paulo', 'Timezone do sistema')
    ]
    
    for key, value, desc in settings:
        cursor.execute('''
            INSERT OR IGNORE INTO system_settings (id, key, value, description)
            VALUES (?, ?, ?, ?)
        ''', (str(uuid.uuid4()), key, value, desc))
    
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect('mikrotik_manager.db')
    conn.row_factory = sqlite3.Row
    return conn

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

def get_setting(key, default=None):
    """Busca uma configuração do sistema"""
    conn = get_db()
    setting = conn.execute('SELECT value FROM system_settings WHERE key = ?', (key,)).fetchone()
    conn.close()
    return setting['value'] if setting else default

def update_credits_cumulative():
    """Atualiza créditos cumulativos diariamente"""
    conn = get_db()
    default_credit = int(get_setting('default_credit_mb', 1024))
    enable_cumulative = get_setting('enable_cumulative', '1') == '1'
    
    if enable_cumulative:
        # Adiciona crédito diário aos usuários ativos
        conn.execute('''
            UPDATE user_credits 
            SET total_mb = total_mb + ?, 
                remaining_mb = remaining_mb + ?,
                last_reset = DATE('now'),
                updated_at = CURRENT_TIMESTAMP
            WHERE hotspot_user_id IN (
                SELECT id FROM hotspot_users WHERE active = 1
            )
        ''', (default_credit, default_credit))
    else:
        # Reset diário sem acumular
        conn.execute('''
            UPDATE user_credits 
            SET total_mb = ?, 
                remaining_mb = ?,
                used_mb = 0,
                last_reset = DATE('now'),
                updated_at = CURRENT_TIMESTAMP
            WHERE hotspot_user_id IN (
                SELECT id FROM hotspot_users WHERE active = 1
            )
        ''', (default_credit, default_credit))
    
    conn.commit()
    conn.close()

def update_users_by_turma(company_id, turma_ativa):
    """Ativa/desativa usuários baseado na turma ativa da empresa"""
    conn = get_db()
    
    # Ativar usuários da turma ativa
    conn.execute('''
        UPDATE hotspot_users 
        SET active = 1 
        WHERE company_id = ? AND turma = ?
    ''', (company_id, turma_ativa))
    
    # Desativar usuários da turma inativa
    turma_inativa = 'B' if turma_ativa == 'A' else 'A'
    conn.execute('''
        UPDATE hotspot_users 
        SET active = 0 
        WHERE company_id = ? AND turma = ?
    ''', (company_id, turma_inativa))
    
    conn.commit()
    conn.close()

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
        
        if not email or not password:
            flash('Email e senha são obrigatórios', 'error')
            return render_template('login.html')
        
        conn = get_db()
        user = conn.execute(
            'SELECT * FROM system_users WHERE email = ? AND password = ? AND active = 1',
            (email, password)
        ).fetchone()
        conn.close()
        
        if user:
            session.permanent = True
            session['user_id'] = user['id']
            session['email'] = user['email']
            session['name'] = user['name']
            session['role'] = user['role']
            session['login_time'] = datetime.now().isoformat()
            
            flash(f'Bem-vindo, {user["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou senha incorretos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout do usuário"""
    session.clear()
    flash('Logout realizado com sucesso', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
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

@app.route('/users', methods=['GET', 'POST'])
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
        
        return redirect(url_for('users'))
    
    # Buscar usuários
    conn = get_db()
    users_list = conn.execute('''
        SELECT * FROM system_users 
        WHERE active = 1 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('users.html', user={'name': session.get('name')}, users_list=users_list)

@app.route('/companies', methods=['GET', 'POST'])
@require_auth
def companies():
    """Página de empresas"""
    if request.method == 'POST':
        name = request.form.get('name')
        mikrotik_ip = request.form.get('mikrotik_ip')
        mikrotik_port = request.form.get('mikrotik_port', 8728)
        mikrotik_user = request.form.get('mikrotik_user')
        mikrotik_password = request.form.get('mikrotik_password')
        turma_ativa = request.form.get('turma_ativa', 'A')
        
        if not all([name, mikrotik_ip, mikrotik_user, mikrotik_password]):
            flash('Todos os campos são obrigatórios', 'error')
        else:
            conn = get_db()
            conn.execute('''
                INSERT INTO companies (id, name, mikrotik_ip, mikrotik_port, mikrotik_user, mikrotik_password, turma_ativa)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (str(uuid.uuid4()), name, mikrotik_ip, int(mikrotik_port), mikrotik_user, mikrotik_password, turma_ativa))
            conn.commit()
            conn.close()
            flash('Empresa cadastrada com sucesso!', 'success')
        
        return redirect(url_for('companies'))
    
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

@app.route('/companies/update-turma', methods=['POST'])
@require_auth
def update_company_turma():
    """Atualizar turma ativa da empresa"""
    company_id = request.form.get('company_id')
    turma_ativa = request.form.get('turma_ativa')
    
    if not all([company_id, turma_ativa]):
        flash('Dados inválidos', 'error')
    else:
        conn = get_db()
        conn.execute('''
            UPDATE companies 
            SET turma_ativa = ? 
            WHERE id = ?
        ''', (turma_ativa, company_id))
        conn.commit()
        conn.close()
        
        # Atualizar status dos usuários baseado na nova turma ativa
        update_users_by_turma(company_id, turma_ativa)
        
        flash(f'Turma ativa atualizada para {turma_ativa}!', 'success')
    
    return redirect(url_for('companies'))

@app.route('/profiles', methods=['GET', 'POST'])
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
        
        return redirect(url_for('profiles'))
    
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

@app.route('/hotspot-users', methods=['GET', 'POST'])
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
        turma = request.form.get('turma', 'A')
        
        if not all([company_id, username, password]):
            flash('Campos obrigatórios não preenchidos', 'error')
        else:
            conn = get_db()
            try:
                # Verificar turma ativa da empresa
                company = conn.execute('SELECT turma_ativa FROM companies WHERE id = ?', (company_id,)).fetchone()
                user_active = 1 if company and company['turma_ativa'] == turma else 0
                
                user_id = str(uuid.uuid4())
                conn.execute('''
                    INSERT INTO hotspot_users (id, company_id, profile_id, username, password, full_name, email, phone, turma, active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, company_id, profile_id, username, password, full_name, email, phone, turma, user_active))
                
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
        
        return redirect(url_for('hotspot_users'))
    
    conn = get_db()
    hotspot_users_list = conn.execute('''
        SELECT hu.*, c.name as company_name, p.name as profile_name,
               uc.total_mb, uc.used_mb, uc.remaining_mb
        FROM hotspot_users hu
        JOIN companies c ON hu.company_id = c.id
        LEFT JOIN hotspot_profiles p ON hu.profile_id = p.id
        LEFT JOIN user_credits uc ON hu.id = uc.hotspot_user_id
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

@app.route('/hotspot-users/edit', methods=['POST'])
@require_auth
def edit_hotspot_user():
    """Editar usuário hotspot"""
    user_id = request.form.get('user_id')
    company_id = request.form.get('company_id')
    profile_id = request.form.get('profile_id')
    username = request.form.get('username')
    password = request.form.get('password')
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    turma = request.form.get('turma', 'A')
    
    if not all([user_id, company_id, username]):
        flash('Campos obrigatórios não preenchidos', 'error')
    else:
        conn = get_db()
        try:
            # Verificar turma ativa da empresa
            company = conn.execute('SELECT turma_ativa FROM companies WHERE id = ?', (company_id,)).fetchone()
            user_active = 1 if company and company['turma_ativa'] == turma else 0
            
            if password:  # Se senha foi fornecida, atualizar com senha
                conn.execute('''
                    UPDATE hotspot_users 
                    SET company_id = ?, profile_id = ?, username = ?, password = ?, 
                        full_name = ?, email = ?, phone = ?, turma = ?, active = ?
                    WHERE id = ?
                ''', (company_id, profile_id, username, password, full_name, email, phone, turma, user_active, user_id))
            else:  # Se senha não foi fornecida, manter a atual
                conn.execute('''
                    UPDATE hotspot_users 
                    SET company_id = ?, profile_id = ?, username = ?, 
                        full_name = ?, email = ?, phone = ?, turma = ?, active = ?
                    WHERE id = ?
                ''', (company_id, profile_id, username, full_name, email, phone, turma, user_active, user_id))
            
            conn.commit()
            flash('Usuário hotspot atualizado com sucesso!', 'success')
        except sqlite3.IntegrityError:
            flash('Username já existe', 'error')
        finally:
            conn.close()
    
    return redirect(url_for('hotspot_users'))

@app.route('/credits')
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

@app.route('/reports')
@require_auth
def reports():
    """Página de relatórios"""
    return render_template('reports.html', user={'name': session.get('name')})

@app.route('/settings', methods=['GET', 'POST'])
@require_auth
def settings():
    """Página de configurações"""
    if request.method == 'POST':
        conn = get_db()
        
        # Atualizar configurações
        settings_to_update = [
            ('default_credit_mb', request.form.get('default_credit_mb')),
            ('credit_reset_time', request.form.get('credit_reset_time')),
            ('enable_cumulative', '1' if request.form.get('enable_cumulative') else '0'),
            ('system_timezone', request.form.get('system_timezone'))
        ]
        
        for key, value in settings_to_update:
            if value is not None:
                conn.execute('''
                    UPDATE system_settings 
                    SET value = ? 
                    WHERE key = ?
                ''', (value, key))
        
        conn.commit()
        conn.close()
        flash('Configurações salvas com sucesso!', 'success')
        return redirect(url_for('settings'))
    
    # Buscar configurações atuais
    conn = get_db()
    current_settings = {}
    settings_rows = conn.execute('SELECT key, value FROM system_settings').fetchall()
    for row in settings_rows:
        current_settings[row['key']] = row['value']
    conn.close()
    
    return render_template('settings.html', 
                         user={'name': session.get('name')},
                         settings=current_settings)

# API Routes
@app.route('/api/health')
def api_health():
    """Health check da API"""
    return jsonify({
        'status': 'ok',
        'message': 'MikroTik Manager API funcionando',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/update-credits', methods=['POST'])
@require_auth
def api_update_credits():
    """API para atualizar créditos cumulativos"""
    try:
        update_credits_cumulative()
        return jsonify({'status': 'success', 'message': 'Créditos atualizados'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    init_db()
    print("🚀 Iniciando MikroTik Manager Flask...")
    print("📧 Login: admin@demo.com")
    print("🔑 Senha: admin123")
    print("🌐 URL: http://localhost:5000")
    print("💾 Banco: mikrotik_manager.db")
    app.run(host='0.0.0.0', port=5000, debug=True)
