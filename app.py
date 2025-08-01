from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import hashlib
import os
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'mikrotik-manager-secret-key-2024'

# Configuração do banco de dados
DATABASE_PATH = 'data/mikrotik_manager.db'

def get_db():
    """Conecta ao banco de dados SQLite"""
    try:
        # Criar diretório data se não existir
        os.makedirs('data', exist_ok=True)
        
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar com o banco: {e}")
        raise

def init_db():
    """Inicializa o banco de dados com as tabelas necessárias"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT,
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
                mikrotik_username TEXT NOT NULL,
                mikrotik_password TEXT NOT NULL,
                api_port INTEGER DEFAULT 8728,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de perfis hotspot
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hotspot_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                name TEXT NOT NULL,
                rate_limit TEXT,
                session_timeout INTEGER,
                idle_timeout INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies (id)
            )
        ''')
        
        # Tabela de usuários hotspot
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hotspot_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                profile_id INTEGER,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                credits_mb INTEGER DEFAULT 0,
                expiry_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies (id),
                FOREIGN KEY (profile_id) REFERENCES hotspot_profiles (id)
            )
        ''')
        
        # Tabela de créditos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS credits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hotspot_user_id INTEGER,
                amount_mb INTEGER NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (hotspot_user_id) REFERENCES hotspot_users (id)
            )
        ''')
        
        # Inserir usuário admin padrão se não existir
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
            cursor.execute('''
                INSERT INTO users (username, password, name, email, role)
                VALUES (?, ?, ?, ?, ?)
            ''', ('admin', admin_password, 'Administrador', 'admin@mikrotik.local', 'admin'))
        
        conn.commit()
        conn.close()
        logger.info("Banco de dados inicializado com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {e}")
        raise

# Decorador para verificar login
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # Hash da senha
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            cursor.execute('''
                SELECT id, username, name, role FROM users 
                WHERE username = ? AND password = ?
            ''', (username, password_hash))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['name'] = user['name']
                session['role'] = user['role']
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Usuário ou senha inválidos!', 'error')
                
        except Exception as e:
            logger.error(f"Erro no login: {e}")
            flash('Erro interno do servidor!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Estatísticas gerais
        cursor.execute("SELECT COUNT(*) as total FROM companies")
        total_companies = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM hotspot_users")
        total_hotspot_users = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM hotspot_profiles")
        total_profiles = cursor.fetchone()['total']
        
        cursor.execute("SELECT COALESCE(SUM(credits_mb), 0) as total FROM hotspot_users")
        total_credits = cursor.fetchone()['total']
        
        conn.close()
        
        stats = {
            'total_companies': total_companies,
            'total_hotspot_users': total_hotspot_users,
            'total_profiles': total_profiles,
            'total_credits_mb': total_credits
        }
        
        return render_template('dashboard.html', stats=stats, user={'name': session.get('name')})
        
    except Exception as e:
        logger.error(f"Erro no dashboard: {e}")
        flash('Erro ao carregar dashboard!', 'error')
        return render_template('dashboard.html', stats={}, user={'name': session.get('name')})

@app.route('/companies', methods=['GET', 'POST'])
@login_required
def companies():
    if request.method == 'POST':
        try:
            # Obter dados do formulário
            name = request.form.get('name', '').strip()
            mikrotik_ip = request.form.get('mikrotik_ip', '').strip()
            mikrotik_username = request.form.get('mikrotik_username', '').strip()
            mikrotik_password = request.form.get('mikrotik_password', '').strip()
            api_port = request.form.get('api_port', '8728').strip()
            
            logger.debug(f"Dados recebidos: name={name}, ip={mikrotik_ip}, user={mikrotik_username}, port={api_port}")
            
            # Validar campos obrigatórios
            if not all([name, mikrotik_ip, mikrotik_username, mikrotik_password]):
                flash('Todos os campos são obrigatórios!', 'error')
                return redirect(url_for('companies'))
            
            # Validar porta
            try:
                api_port = int(api_port)
            except ValueError:
                flash('Porta da API deve ser um número válido!', 'error')
                return redirect(url_for('companies'))
            
            conn = get_db()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO companies (name, mikrotik_ip, mikrotik_username, mikrotik_password, api_port)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, mikrotik_ip, mikrotik_username, mikrotik_password, api_port))
            
            conn.commit()
            conn.close()
            
            flash('Empresa cadastrada com sucesso!', 'success')
            return redirect(url_for('companies'))
            
        except Exception as e:
            logger.error(f"Erro ao cadastrar empresa: {e}")
            flash('Erro ao cadastrar empresa!', 'error')
    
    # Listar empresas
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM companies ORDER BY created_at DESC')
        companies_list = cursor.fetchall()
        conn.close()
        
        return render_template('companies.html', companies=companies_list, user={'name': session.get('name')})
        
    except Exception as e:
        logger.error(f"Erro ao listar empresas: {e}")
        return render_template('companies.html', companies=[], user={'name': session.get('name')})

@app.route('/profiles', methods=['GET', 'POST'])
@login_required
def profiles():
    if request.method == 'POST':
        try:
            company_id = request.form.get('company_id')
            name = request.form.get('name')
            rate_limit = request.form.get('rate_limit')
            session_timeout = request.form.get('session_timeout')
            idle_timeout = request.form.get('idle_timeout')
            
            if not all([company_id, name]):
                flash('Empresa e nome são obrigatórios!', 'error')
                return redirect(url_for('profiles'))
            
            conn = get_db()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO hotspot_profiles (company_id, name, rate_limit, session_timeout, idle_timeout)
                VALUES (?, ?, ?, ?, ?)
            ''', (company_id, name, rate_limit, session_timeout or None, idle_timeout or None))
            
            conn.commit()
            conn.close()
            
            flash('Perfil criado com sucesso!', 'success')
            return redirect(url_for('profiles'))
            
        except Exception as e:
            logger.error(f"Erro ao criar perfil: {e}")
            flash('Erro ao criar perfil!', 'error')
    
    # Listar perfis e empresas
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.*, c.name as company_name 
            FROM hotspot_profiles p 
            JOIN companies c ON p.company_id = c.id 
            ORDER BY p.created_at DESC
        ''')
        profiles_list = cursor.fetchall()
        
        cursor.execute('SELECT * FROM companies ORDER BY name')
        companies_list = cursor.fetchall()
        
        conn.close()
        
        return render_template('profiles.html', profiles=profiles_list, companies=companies_list, user={'name': session.get('name')})
        
    except Exception as e:
        logger.error(f"Erro ao listar perfis: {e}")
        return render_template('profiles.html', profiles=[], companies=[], user={'name': session.get('name')})

@app.route('/hotspot-users', methods=['GET', 'POST'])
@login_required
def hotspot_users():
    if request.method == 'POST':
        try:
            company_id = request.form.get('company_id')
            profile_id = request.form.get('profile_id')
            username = request.form.get('username')
            password = request.form.get('password')
            credits_mb = request.form.get('credits_mb', '0')
            expiry_date = request.form.get('expiry_date')
            
            if not all([company_id, username, password]):
                flash('Empresa, usuário e senha são obrigatórios!', 'error')
                return redirect(url_for('hotspot_users'))
            
            conn = get_db()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO hotspot_users (company_id, profile_id, username, password, credits_mb, expiry_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (company_id, profile_id or None, username, password, int(credits_mb or 0), expiry_date or None))
            
            conn.commit()
            conn.close()
            
            flash('Usuário hotspot criado com sucesso!', 'success')
            return redirect(url_for('hotspot_users'))
            
        except Exception as e:
            logger.error(f"Erro ao criar usuário hotspot: {e}")
            flash('Erro ao criar usuário hotspot!', 'error')
    
    # Listar usuários hotspot
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT h.*, c.name as company_name, p.name as profile_name 
            FROM hotspot_users h 
            JOIN companies c ON h.company_id = c.id 
            LEFT JOIN hotspot_profiles p ON h.profile_id = p.id 
            ORDER BY h.created_at DESC
        ''')
        hotspot_users_list = cursor.fetchall()
        
        cursor.execute('SELECT * FROM companies ORDER BY name')
        companies_list = cursor.fetchall()
        
        cursor.execute('SELECT * FROM hotspot_profiles ORDER BY name')
        profiles_list = cursor.fetchall()
        
        conn.close()
        
        return render_template('hotspot_users.html', 
                             hotspot_users=hotspot_users_list, 
                             companies=companies_list, 
                             profiles=profiles_list,
                             user={'name': session.get('name')})
        
    except Exception as e:
        logger.error(f"Erro ao listar usuários hotspot: {e}")
        return render_template('hotspot_users.html', hotspot_users=[], companies=[], profiles=[], user={'name': session.get('name')})

@app.route('/credits', methods=['GET', 'POST'])
@login_required
def credits():
    if request.method == 'POST':
        try:
            hotspot_user_id = request.form.get('hotspot_user_id')
            amount_mb = request.form.get('amount_mb')
            description = request.form.get('description', '')
            
            if not all([hotspot_user_id, amount_mb]):
                flash('Usuário e quantidade são obrigatórios!', 'error')
                return redirect(url_for('credits'))
            
            conn = get_db()
            cursor = conn.cursor()
            
            # Adicionar crédito
            cursor.execute('''
                INSERT INTO credits (hotspot_user_id, amount_mb, description)
                VALUES (?, ?, ?)
            ''', (hotspot_user_id, int(amount_mb), description))
            
            # Atualizar total de créditos do usuário
            cursor.execute('''
                UPDATE hotspot_users 
                SET credits_mb = credits_mb + ? 
                WHERE id = ?
            ''', (int(amount_mb), hotspot_user_id))
            
            conn.commit()
            conn.close()
            
            flash('Créditos adicionados com sucesso!', 'success')
            return redirect(url_for('credits'))
            
        except Exception as e:
            logger.error(f"Erro ao adicionar créditos: {e}")
            flash('Erro ao adicionar créditos!', 'error')
    
    # Listar créditos
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.*, h.username, comp.name as company_name 
            FROM credits c 
            JOIN hotspot_users h ON c.hotspot_user_id = h.id 
            JOIN companies comp ON h.company_id = comp.id 
            ORDER BY c.created_at DESC
        ''')
        credits_list = cursor.fetchall()
        
        cursor.execute('''
            SELECT h.*, c.name as company_name 
            FROM hotspot_users h 
            JOIN companies c ON h.company_id = c.id 
            ORDER BY h.username
        ''')
        hotspot_users_list = cursor.fetchall()
        
        # Calcular estatísticas
        cursor.execute("SELECT COALESCE(SUM(credits_mb), 0) as total FROM hotspot_users")
        total_credits = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM credits")
        total_transactions = cursor.fetchone()['total']
        
        conn.close()
        
        stats = {
            'total_credits_mb': total_credits,
            'total_transactions': total_transactions
        }
        
        return render_template('credits.html', 
                             credits=credits_list, 
                             hotspot_users=hotspot_users_list,
                             stats=stats,
                             user={'name': session.get('name')})
        
    except Exception as e:
        logger.error(f"Erro ao listar créditos: {e}")
        return render_template('credits.html', credits=[], hotspot_users=[], stats={}, user={'name': session.get('name')})

@app.route('/reports')
@login_required
def reports():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Relatório de empresas
        cursor.execute('''
            SELECT c.name, COUNT(h.id) as total_users, COALESCE(SUM(h.credits_mb), 0) as total_credits
            FROM companies c
            LEFT JOIN hotspot_users h ON c.id = h.company_id
            GROUP BY c.id, c.name
            ORDER BY total_users DESC
        ''')
        companies_report = cursor.fetchall()
        
        # Relatório de perfis mais usados
        cursor.execute('''
            SELECT p.name, COUNT(h.id) as usage_count
            FROM hotspot_profiles p
            LEFT JOIN hotspot_users h ON p.id = h.profile_id
            GROUP BY p.id, p.name
            ORDER BY usage_count DESC
            LIMIT 10
        ''')
        profiles_report = cursor.fetchall()
        
        # Relatório de créditos por mês
        cursor.execute('''
            SELECT strftime('%Y-%m', created_at) as month, SUM(amount_mb) as total_credits
            FROM credits
            GROUP BY strftime('%Y-%m', created_at)
            ORDER BY month DESC
            LIMIT 12
        ''')
        credits_monthly = cursor.fetchall()
        
        conn.close()
        
        return render_template('reports.html', 
                             companies_report=companies_report,
                             profiles_report=profiles_report,
                             credits_monthly=credits_monthly,
                             user={'name': session.get('name')})
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatórios: {e}")
        return render_template('reports.html', 
                             companies_report=[], 
                             profiles_report=[], 
                             credits_monthly=[],
                             user={'name': session.get('name')})

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html', user={'name': session.get('name')})

@app.route('/users')
@login_required
def users():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, name, email, role, created_at FROM users ORDER BY created_at DESC')
        users_list = cursor.fetchall()
        conn.close()
        
        return render_template('users.html', users=users_list, user={'name': session.get('name')})
        
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {e}")
        return render_template('users.html', users=[], user={'name': session.get('name')})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
