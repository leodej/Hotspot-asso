from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
import hashlib
import paramiko
import re
import threading
import time
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Configurações
DATABASE = 'mikrotik_manager.db'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Variável global para controle da coleta automática
auto_collect_thread = None
auto_collect_running = False

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Tabela de usuários do sistema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de empresas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mikrotik_ip TEXT NOT NULL,
            mikrotik_port INTEGER DEFAULT 22,
            mikrotik_user TEXT NOT NULL,
            mikrotik_password TEXT NOT NULL,
            turma_ativa TEXT DEFAULT 'A',
            connection_status TEXT DEFAULT 'disconnected',
            last_connection_test TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de perfis hotspot
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hotspot_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            rate_limit TEXT,
            session_timeout INTEGER,
            idle_timeout INTEGER,
            shared_users INTEGER DEFAULT 1,
            is_default BOOLEAN DEFAULT 0,
            company_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    ''')
    
    # Tabela de usuários hotspot
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hotspot_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            profile_id INTEGER,
            company_id INTEGER NOT NULL,
            turma TEXT DEFAULT 'A',
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (profile_id) REFERENCES hotspot_profiles (id),
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    ''')
    
    # Tabela de créditos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_credits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            company_id INTEGER NOT NULL,
            total_mb INTEGER DEFAULT 0,
            used_mb INTEGER DEFAULT 0,
            remaining_mb INTEGER DEFAULT 0,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES hotspot_users (id),
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    ''')
    
    # Tabela de logs MikroTik
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mikrotik_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            status TEXT DEFAULT 'success',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    ''')
    
    # Tabela de configurações
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Inserir configurações padrão
    cursor.execute('''
        INSERT OR IGNORE INTO settings (key, value) VALUES 
        ('system_name', 'MikroTik Manager'),
        ('system_logo', ''),
        ('auto_collect_usage', 'true')
    ''')
    
    # Criar usuário admin padrão
    admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
    cursor.execute('''
        INSERT OR IGNORE INTO users (name, email, password, role) 
        VALUES ('Administrador', 'admin@admin.com', ?, 'admin')
    ''', (admin_password,))
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def log_mikrotik_action(company_id, action, details, status='success'):
    """Registra ações do MikroTik nos logs"""
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO mikrotik_logs (company_id, action, details, status)
        VALUES (?, ?, ?, ?)
    ''', (company_id, action, details, status))
    conn.commit()
    conn.close()

def connect_mikrotik(ip, port, username, password):
    """Conecta ao MikroTik via SSH"""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port=port, username=username, password=password, timeout=10)
        return ssh
    except Exception as e:
        return None

def collect_user_usage_from_mikrotik(company_id):
    """Coleta dados de uso dos usuários do MikroTik via comment"""
    conn = get_db_connection()
    company = conn.execute('SELECT * FROM companies WHERE id = ?', (company_id,)).fetchone()
    
    if not company:
        conn.close()
        return False, "Empresa não encontrada"
    
    try:
        # Conectar ao MikroTik
        ssh = connect_mikrotik(company['mikrotik_ip'], company['mikrotik_port'], 
                             company['mikrotik_user'], company['mikrotik_password'])
        
        if not ssh:
            log_mikrotik_action(company_id, 'collect_usage', 'Falha na conexão SSH', 'error')
            conn.close()
            return False, "Falha na conexão SSH"
        
        # Executar comando para listar usuários hotspot com comments
        stdin, stdout, stderr = ssh.exec_command('/ip hotspot user print detail')
        output = stdout.read().decode('utf-8')
        ssh.close()
        
        # Parse dos usuários e seus dados de uso
        users_data = parse_mikrotik_users_usage(output)
        updated_count = 0
        
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        for user_data in users_data:
            username = user_data.get('name', '')
            comment = user_data.get('comment', '')
            
            if not username:
                continue
            
            # Buscar usuário no sistema
            user = conn.execute('''
                SELECT id FROM hotspot_users 
                WHERE name = ? AND company_id = ?
            ''', (username, company_id)).fetchone()
            
            if not user:
                continue
            
            # Extrair dados de uso do comment
            used_mb = parse_usage_from_comment(comment)
            
            if used_mb is None:
                continue
            
            # Buscar ou criar registro de crédito
            credit = conn.execute('''
                SELECT * FROM user_credits 
                WHERE user_id = ? AND company_id = ? AND month = ? AND year = ?
            ''', (user['id'], company_id, current_month, current_year)).fetchone()
            
            if credit:
                # Atualizar registro existente
                remaining_mb = max(0, credit['total_mb'] - used_mb)
                conn.execute('''
                    UPDATE user_credits 
                    SET used_mb = ?, remaining_mb = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (used_mb, remaining_mb, credit['id']))
            else:
                # Criar novo registro (assumindo 1000MB como padrão)
                total_mb = 1000
                remaining_mb = max(0, total_mb - used_mb)
                conn.execute('''
                    INSERT INTO user_credits (user_id, company_id, total_mb, used_mb, remaining_mb, month, year)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user['id'], company_id, total_mb, used_mb, remaining_mb, current_month, current_year))
            
            updated_count += 1
        
        conn.commit()
        
        # Log da operação
        log_mikrotik_action(company_id, 'collect_usage', 
                          f'Coletados dados de uso de {updated_count} usuários', 'success')
        
        conn.close()
        return True, f"Dados de uso coletados para {updated_count} usuários"
        
    except Exception as e:
        log_mikrotik_action(company_id, 'collect_usage', f'Erro: {str(e)}', 'error')
        conn.close()
        return False, f"Erro na coleta: {str(e)}"

def parse_mikrotik_users_usage(output):
    """Parse da saída do comando MikroTik para extrair usuários e comments"""
    users = []
    current_user = {}
    
    lines = output.split('\n')
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('name='):
            # Novo usuário encontrado
            if current_user:
                users.append(current_user)
            current_user = {}
            
            # Extrair nome
            name_match = re.search(r'name=(?:"([^"]+)"|([^\s]+))', line)
            if name_match:
                current_user['name'] = name_match.group(1) or name_match.group(2)
        
        elif 'comment=' in line and current_user:
            # Extrair comment
            comment_match = re.search(r'comment=(?:"([^"]+)"|([^\s]+))', line)
            if comment_match:
                current_user['comment'] = comment_match.group(1) or comment_match.group(2)
    
    # Adicionar último usuário
    if current_user:
        users.append(current_user)
    
    return users

def parse_usage_from_comment(comment):
    """Extrai dados de uso em MB do comment"""
    if not comment:
        return None
    
    # Procurar padrões como "1024MB", "1.5GB", "512KB"
    patterns = [
        r'(\d+(?:\.\d+)?)\s*MB',
        r'(\d+(?:\.\d+)?)\s*GB',
        r'(\d+(?:\.\d+)?)\s*KB',
        r'(\d+(?:\.\d+)?)\s*mb',
        r'(\d+(?:\.\d+)?)\s*gb',
        r'(\d+(?:\.\d+)?)\s*kb'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, comment, re.IGNORECASE)
        if match:
            value = float(match.group(1))
            unit = pattern.split('\\s*')[1].replace(')', '').upper()
            
            if 'GB' in unit:
                return int(value * 1024)  # Converter GB para MB
            elif 'KB' in unit:
                return int(value / 1024)  # Converter KB para MB
            else:  # MB
                return int(value)
    
    return None

def auto_collect_usage():
    """Função para coleta automática de uso a cada 1 minuto"""
    global auto_collect_running
    
    while auto_collect_running:
        try:
            # Verificar se a coleta automática está habilitada
            conn = get_db_connection()
            setting = conn.execute('SELECT value FROM settings WHERE key = ?', ('auto_collect_usage',)).fetchone()
            
            if setting and setting['value'] == 'true':
                # Buscar todas as empresas
                companies = conn.execute('SELECT id FROM companies').fetchall()
                
                for company in companies:
                    collect_user_usage_from_mikrotik(company['id'])
                    time.sleep(1)  # Pequena pausa entre empresas
            
            conn.close()
            
        except Exception as e:
            print(f"Erro na coleta automática: {e}")
        
        # Aguardar 60 segundos (1 minuto)
        time.sleep(60)

def start_auto_collect():
    """Inicia a coleta automática"""
    global auto_collect_thread, auto_collect_running
    
    if not auto_collect_running:
        auto_collect_running = True
        auto_collect_thread = threading.Thread(target=auto_collect_usage, daemon=True)
        auto_collect_thread.start()

def stop_auto_collect():
    """Para a coleta automática"""
    global auto_collect_running
    auto_collect_running = False

# Middleware para verificar autenticação
@app.before_request
def require_login():
    allowed_routes = ['login', 'static']
    if request.endpoint not in allowed_routes and 'user_id' not in session:
        return redirect(url_for('login'))

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', 
                          (email, password)).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou senha incorretos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    
    # Estatísticas gerais
    stats = {
        'total_companies': conn.execute('SELECT COUNT(*) as count FROM companies').fetchone()['count'],
        'total_users': conn.execute('SELECT COUNT(*) as count FROM hotspot_users').fetchone()['count'],
        'total_profiles': conn.execute('SELECT COUNT(*) as count FROM hotspot_profiles').fetchone()['count'],
        'connected_companies': conn.execute("SELECT COUNT(*) as count FROM companies WHERE connection_status = 'connected'").fetchone()['count']
    }
    
    # Empresas recentes
    recent_companies = conn.execute('''
        SELECT name, connection_status, last_connection_test 
        FROM companies 
        ORDER BY created_at DESC 
        LIMIT 5
    ''').fetchall()
    
    # Logs recentes
    recent_logs = conn.execute('''
        SELECT ml.action, ml.details, ml.timestamp, c.name as company_name
        FROM mikrotik_logs ml
        JOIN companies c ON ml.company_id = c.id
        ORDER BY ml.timestamp DESC
        LIMIT 10
    ''').fetchall()
    
    conn.close()
    
    user = {'name': session.get('user_name', 'Usuário')}
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         recent_companies=recent_companies,
                         recent_logs=recent_logs,
                         user=user)

@app.route('/companies', methods=['GET', 'POST'])
def companies():
    if request.method == 'POST':
        name = request.form['name']
        mikrotik_ip = request.form['mikrotik_ip']
        mikrotik_port = int(request.form['mikrotik_port'])
        mikrotik_user = request.form['mikrotik_user']
        mikrotik_password = request.form['mikrotik_password']
        turma_ativa = request.form['turma_ativa']
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO companies (name, mikrotik_ip, mikrotik_port, mikrotik_user, mikrotik_password, turma_ativa)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, mikrotik_ip, mikrotik_port, mikrotik_user, mikrotik_password, turma_ativa))
        conn.commit()
        conn.close()
        
        flash('Empresa cadastrada com sucesso!', 'success')
        return redirect(url_for('companies'))
    
    conn = get_db_connection()
    companies_list = conn.execute('''
        SELECT c.*, 
               COUNT(hu.id) as user_count
        FROM companies c
        LEFT JOIN hotspot_users hu ON c.id = hu.company_id
        GROUP BY c.id
        ORDER BY c.name
    ''').fetchall()
    conn.close()
    
    user = {'name': session.get('user_name', 'Usuário')}
    
    return render_template('companies.html', companies_list=companies_list, user=user)

@app.route('/companies/<int:company_id>/edit', methods=['POST'])
def edit_company(company_id):
    name = request.form['name']
    mikrotik_ip = request.form['mikrotik_ip']
    mikrotik_port = int(request.form['mikrotik_port'])
    mikrotik_user = request.form['mikrotik_user']
    mikrotik_password = request.form['mikrotik_password']
    turma_ativa = request.form['turma_ativa']
    
    conn = get_db_connection()
    conn.execute('''
        UPDATE companies 
        SET name = ?, mikrotik_ip = ?, mikrotik_port = ?, mikrotik_user = ?, mikrotik_password = ?, turma_ativa = ?
        WHERE id = ?
    ''', (name, mikrotik_ip, mikrotik_port, mikrotik_user, mikrotik_password, turma_ativa, company_id))
    conn.commit()
    conn.close()
    
    flash('Empresa atualizada com sucesso!', 'success')
    return redirect(url_for('companies'))

@app.route('/companies/<int:company_id>/test-connection', methods=['POST'])
def test_company_connection(company_id):
    conn = get_db_connection()
    company = conn.execute('SELECT * FROM companies WHERE id = ?', (company_id,)).fetchone()
    
    if company:
        ssh = connect_mikrotik(company['mikrotik_ip'], company['mikrotik_port'], 
                             company['mikrotik_user'], company['mikrotik_password'])
        
        if ssh:
            ssh.close()
            conn.execute('''
                UPDATE companies 
                SET connection_status = 'connected', last_connection_test = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (company_id,))
            conn.commit()
            log_mikrotik_action(company_id, 'test_connection', 'Conexão bem-sucedida', 'success')
            flash('Conexão testada com sucesso!', 'success')
        else:
            conn.execute('''
                UPDATE companies 
                SET connection_status = 'disconnected', last_connection_test = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (company_id,))
            conn.commit()
            log_mikrotik_action(company_id, 'test_connection', 'Falha na conexão', 'error')
            flash('Falha na conexão com o MikroTik', 'error')
    
    conn.close()
    return redirect(url_for('companies'))

@app.route('/companies/<int:company_id>/collect-usage', methods=['POST'])
def collect_company_usage(company_id):
    """Coleta dados de uso de uma empresa específica"""
    success, message = collect_user_usage_from_mikrotik(company_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('companies'))

@app.route('/collect-all-usage', methods=['POST'])
def collect_all_usage():
    """Coleta dados de uso de todas as empresas"""
    conn = get_db_connection()
    companies = conn.execute('SELECT id, name FROM companies').fetchall()
    conn.close()
    
    total_updated = 0
    errors = []
    
    for company in companies:
        success, message = collect_user_usage_from_mikrotik(company['id'])
        if success:
            # Extrair número de usuários atualizados da mensagem
            import re
            match = re.search(r'(\d+)', message)
            if match:
                total_updated += int(match.group(1))
        else:
            errors.append(f"{company['name']}: {message}")
    
    if errors:
        flash(f"Coleta concluída com {len(errors)} erros. Total de usuários atualizados: {total_updated}", 'warning')
    else:
        flash(f"Coleta concluída com sucesso! Total de usuários atualizados: {total_updated}", 'success')
    
    return redirect(url_for('companies'))

@app.route('/companies/update-turma', methods=['POST'])
def update_company_turma():
    company_id = request.form['company_id']
    turma_ativa = request.form['turma_ativa']
    
    conn = get_db_connection()
    conn.execute('UPDATE companies SET turma_ativa = ? WHERE id = ?', (turma_ativa, company_id))
    conn.commit()
    conn.close()
    
    flash('Turma ativa atualizada com sucesso!', 'success')
    return redirect(url_for('companies'))

# Outras rotas existentes...
@app.route('/profiles')
def profiles():
    user = {'name': session.get('user_name', 'Usuário')}
    return render_template('profiles.html', user=user)

@app.route('/hotspot-users')
def hotspot_users():
    user = {'name': session.get('user_name', 'Usuário')}
    return render_template('hotspot_users.html', user=user)

@app.route('/credits')
def credits():
    user = {'name': session.get('user_name', 'Usuário')}
    return render_template('credits.html', user=user)

@app.route('/reports')
def reports():
    user = {'name': session.get('user_name', 'Usuário')}
    return render_template('reports.html', user=user)

@app.route('/mikrotik-logs')
def mikrotik_logs():
    user = {'name': session.get('user_name', 'Usuário')}
    return render_template('mikrotik_logs.html', user=user)

@app.route('/settings')
def settings():
    user = {'name': session.get('user_name', 'Usuário')}
    return render_template('settings.html', user=user)

@app.route('/users')
def users():
    user = {'name': session.get('user_name', 'Usuário')}
    return render_template('users.html', user=user)

if __name__ == '__main__':
    init_db()
    start_auto_collect()  # Iniciar coleta automática
    app.run(debug=True, host='0.0.0.0', port=5000)
