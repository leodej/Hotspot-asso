from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import hashlib
import os
from datetime import datetime, timedelta
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Database configuration
DATABASE = 'mikrotik_manager.db'

def get_db():
    """Get database connection"""
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def init_db():
    """Initialize database with tables"""
    conn = get_db()
    if not conn:
        return False
    
    try:
        # Create system_users table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS system_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'admin',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create companies table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                mikrotik_ip TEXT NOT NULL,
                mikrotik_username TEXT NOT NULL,
                mikrotik_password TEXT NOT NULL,
                api_port INTEGER DEFAULT 8728,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create hotspot_profiles table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS hotspot_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                company_id INTEGER,
                rate_limit TEXT,
                session_timeout INTEGER,
                idle_timeout INTEGER,
                shared_users INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies (id)
            )
        ''')

        # Create hotspot_users table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS hotspot_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                profile_id INTEGER,
                company_id INTEGER,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (profile_id) REFERENCES hotspot_profiles (id),
                FOREIGN KEY (company_id) REFERENCES companies (id)
            )
        ''')

        # Create user_credits table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_credits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                credits_mb INTEGER DEFAULT 0,
                used_mb INTEGER DEFAULT 0,
                last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES hotspot_users (id)
            )
        ''')

        # Create system_settings table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS system_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Insert default admin user if not exists
        admin_exists = conn.execute(
            'SELECT id FROM system_users WHERE email = ?', 
            ('admin@demo.com',)
        ).fetchone()

        if not admin_exists:
            password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
            conn.execute('''
                INSERT INTO system_users (name, email, password, role)
                VALUES (?, ?, ?, ?)
            ''', ('Admin', 'admin@demo.com', password_hash, 'admin'))

        # Insert default settings if not exist
        default_settings = [
            ('default_credits_mb', '1024'),
            ('credits_reset_time', '00:00'),
            ('cumulative_credits', 'true'),
            ('system_timezone', 'America/Sao_Paulo')
        ]

        for key, value in default_settings:
            existing = conn.execute(
                'SELECT id FROM system_settings WHERE setting_key = ?', 
                (key,)
            ).fetchone()
            
            if not existing:
                conn.execute('''
                    INSERT INTO system_settings (setting_key, setting_value)
                    VALUES (?, ?)
                ''', (key, value))

        conn.commit()
        print("Database initialized successfully!")
        return True

    except Exception as e:
        print(f"Database initialization error: {e}")
        return False
    finally:
        conn.close()

def login_required(f):
    """Decorator to require login"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = get_db()
        if not conn:
            flash('Erro de conexão com banco de dados', 'error')
            return render_template('login.html')
        
        try:
            user = conn.execute(
                'SELECT * FROM system_users WHERE email = ? AND password = ?',
                (email, password_hash)
            ).fetchone()
            
            if user:
                session['user_id'] = user['id']
                session['name'] = user['name']
                session['email'] = user['email']
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Email ou senha incorretos', 'error')
        except Exception as e:
            flash(f'Erro no login: {str(e)}', 'error')
        finally:
            conn.close()
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    if not conn:
        flash('Erro de conexão com banco de dados', 'error')
        return render_template('dashboard.html', user={'name': session.get('name')}, stats={}, activities=[])
    
    try:
        # Get statistics
        stats = {}
        
        # Total users
        result = conn.execute('SELECT COUNT(*) as count FROM hotspot_users').fetchone()
        stats['total_users'] = result['count'] if result else 0
        
        # Total companies
        result = conn.execute('SELECT COUNT(*) as count FROM companies').fetchone()
        stats['total_companies'] = result['count'] if result else 0
        
        # Total credits
        result = conn.execute('SELECT SUM(credits_mb) as total FROM user_credits').fetchone()
        stats['total_credits_mb'] = result['total'] if result and result['total'] else 0
        
        # Total profiles
        result = conn.execute('SELECT COUNT(*) as count FROM hotspot_profiles').fetchone()
        stats['total_profiles'] = result['count'] if result else 0
        
        # Get recent activities (mock data for now)
        activities = [
            {
                'type': 'user',
                'description': 'Novo usuário hotspot criado',
                'time': 'Há 2 horas'
            },
            {
                'type': 'company',
                'description': 'Empresa conectada com sucesso',
                'time': 'Há 4 horas'
            },
            {
                'type': 'credit',
                'description': 'Créditos atualizados',
                'time': 'Há 6 horas'
            }
        ]
        
        user_data = {'name': session.get('name')}
        
        return render_template('dashboard.html', user=user_data, stats=stats, activities=activities)
        
    except Exception as e:
        flash(f'Erro ao carregar dashboard: {str(e)}', 'error')
        return render_template('dashboard.html', user={'name': session.get('name')}, stats={}, activities=[])
    finally:
        conn.close()

@app.route('/users')
@login_required
def users():
    conn = get_db()
    if not conn:
        flash('Erro de conexão com banco de dados', 'error')
        return render_template('users.html', users=[], user={'name': session.get('name')})
    
    try:
        users_list = conn.execute('''
            SELECT su.*, 
                   (SELECT COUNT(*) FROM hotspot_users hu WHERE hu.company_id IN 
                    (SELECT c.id FROM companies c)) as total_hotspot_users
            FROM system_users su
            ORDER BY su.created_at DESC
        ''').fetchall()
        
        return render_template('users.html', users=users_list, user={'name': session.get('name')})
    except Exception as e:
        flash(f'Erro ao carregar usuários: {str(e)}', 'error')
        return render_template('users.html', users=[], user={'name': session.get('name')})
    finally:
        conn.close()

@app.route('/companies')
@login_required
def companies():
    conn = get_db()
    if not conn:
        flash('Erro de conexão com banco de dados', 'error')
        return render_template('companies.html', companies=[], user={'name': session.get('name')})
    
    try:
        companies_list = conn.execute('''
            SELECT c.*,
                   (SELECT COUNT(*) FROM hotspot_users hu WHERE hu.company_id = c.id) as user_count
            FROM companies c
            ORDER BY c.created_at DESC
        ''').fetchall()
        
        return render_template('companies.html', companies=companies_list, user={'name': session.get('name')})
    except Exception as e:
        flash(f'Erro ao carregar empresas: {str(e)}', 'error')
        return render_template('companies.html', companies=[], user={'name': session.get('name')})
    finally:
        conn.close()

@app.route('/profiles')
@login_required
def profiles():
    conn = get_db()
    if not conn:
        flash('Erro de conexão com banco de dados', 'error')
        return render_template('profiles.html', profiles=[], companies=[], user={'name': session.get('name')})
    
    try:
        profiles_list = conn.execute('''
            SELECT p.*, c.name as company_name,
                   (SELECT COUNT(*) FROM hotspot_users hu WHERE hu.profile_id = p.id) as user_count
            FROM hotspot_profiles p
            LEFT JOIN companies c ON p.company_id = c.id
            ORDER BY p.created_at DESC
        ''').fetchall()
        
        companies_list = conn.execute('SELECT * FROM companies ORDER BY name').fetchall()
        
        return render_template('profiles.html', profiles=profiles_list, companies=companies_list, user={'name': session.get('name')})
    except Exception as e:
        flash(f'Erro ao carregar perfis: {str(e)}', 'error')
        return render_template('profiles.html', profiles=[], companies=[], user={'name': session.get('name')})
    finally:
        conn.close()

@app.route('/hotspot-users')
@login_required
def hotspot_users():
    conn = get_db()
    if not conn:
        flash('Erro de conexão com banco de dados', 'error')
        return render_template('hotspot_users.html', hotspot_users=[], companies=[], profiles=[], user={'name': session.get('name')})
    
    try:
        hotspot_users_list = conn.execute('''
            SELECT hu.*, c.name as company_name, p.name as profile_name,
                   uc.credits_mb, uc.used_mb
            FROM hotspot_users hu
            LEFT JOIN companies c ON hu.company_id = c.id
            LEFT JOIN hotspot_profiles p ON hu.profile_id = p.id
            LEFT JOIN user_credits uc ON uc.user_id = hu.id
            ORDER BY hu.created_at DESC
        ''').fetchall()
        
        companies_list = conn.execute('SELECT * FROM companies ORDER BY name').fetchall()
        profiles_list = conn.execute('SELECT * FROM hotspot_profiles ORDER BY name').fetchall()
        
        return render_template('hotspot_users.html', 
                             hotspot_users=hotspot_users_list, 
                             companies=companies_list, 
                             profiles=profiles_list,
                             user={'name': session.get('name')})
    except Exception as e:
        flash(f'Erro ao carregar usuários hotspot: {str(e)}', 'error')
        return render_template('hotspot_users.html', hotspot_users=[], companies=[], profiles=[], user={'name': session.get('name')})
    finally:
        conn.close()

@app.route('/credits')
@login_required
def credits():
    conn = get_db()
    if not conn:
        flash('Erro de conexão com banco de dados', 'error')
        return render_template('credits.html', credits=[], user={'name': session.get('name')})
    
    try:
        credits_list = conn.execute('''
            SELECT uc.*, hu.username, c.name as company_name
            FROM user_credits uc
            LEFT JOIN hotspot_users hu ON uc.user_id = hu.id
            LEFT JOIN companies c ON hu.company_id = c.id
            ORDER BY uc.created_at DESC
        ''').fetchall()
        
        return render_template('credits.html', credits=credits_list, user={'name': session.get('name')})
    except Exception as e:
        flash(f'Erro ao carregar créditos: {str(e)}', 'error')
        return render_template('credits.html', credits=[], user={'name': session.get('name')})
    finally:
        conn.close()

@app.route('/reports')
@login_required
def reports():
    return render_template('reports.html', user={'name': session.get('name')})

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    conn = get_db()
    if not conn:
        flash('Erro de conexão com banco de dados', 'error')
        return render_template('settings.html', settings={}, user={'name': session.get('name')})
    
    if request.method == 'POST':
        try:
            # Update settings
            settings_data = {
                'default_credits_mb': request.form.get('default_credits_mb', '1024'),
                'credits_reset_time': request.form.get('credits_reset_time', '00:00'),
                'cumulative_credits': 'true' if request.form.get('cumulative_credits') else 'false',
                'system_timezone': request.form.get('system_timezone', 'America/Sao_Paulo')
            }
            
            for key, value in settings_data.items():
                conn.execute('''
                    INSERT OR REPLACE INTO system_settings (setting_key, setting_value)
                    VALUES (?, ?)
                ''', (key, value))
            
            conn.commit()
            flash('Configurações salvas com sucesso!', 'success')
        except Exception as e:
            flash(f'Erro ao salvar configurações: {str(e)}', 'error')
    
    try:
        # Get current settings
        settings_rows = conn.execute('SELECT setting_key, setting_value FROM system_settings').fetchall()
        settings = {row['setting_key']: row['setting_value'] for row in settings_rows}
        
        return render_template('settings.html', settings=settings, user={'name': session.get('name')})
    except Exception as e:
        flash(f'Erro ao carregar configurações: {str(e)}', 'error')
        return render_template('settings.html', settings={}, user={'name': session.get('name')})
    finally:
        conn.close()

# API Routes for AJAX operations
@app.route('/api/companies', methods=['POST'])
@login_required
def api_add_company():
    conn = get_db()
    if not conn:
        return jsonify({'success': False, 'message': 'Erro de conexão com banco de dados'})
    
    try:
        data = request.get_json()
        conn.execute('''
            INSERT INTO companies (name, mikrotik_ip, mikrotik_username, mikrotik_password, api_port)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['name'], data['mikrotik_ip'], data['mikrotik_username'], 
              data['mikrotik_password'], data.get('api_port', 8728)))
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Empresa adicionada com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao adicionar empresa: {str(e)}'})
    finally:
        conn.close()

@app.route('/api/profiles', methods=['POST'])
@login_required
def api_add_profile():
    conn = get_db()
    if not conn:
        return jsonify({'success': False, 'message': 'Erro de conexão com banco de dados'})
    
    try:
        data = request.get_json()
        conn.execute('''
            INSERT INTO hotspot_profiles (name, company_id, rate_limit, session_timeout, idle_timeout, shared_users)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['name'], data['company_id'], data['rate_limit'], 
              data.get('session_timeout'), data.get('idle_timeout'), data.get('shared_users', 1)))
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Perfil adicionado com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao adicionar perfil: {str(e)}'})
    finally:
        conn.close()

@app.route('/api/hotspot-users', methods=['POST'])
@login_required
def api_add_hotspot_user():
    conn = get_db()
    if not conn:
        return jsonify({'success': False, 'message': 'Erro de conexão com banco de dados'})
    
    try:
        data = request.get_json()
        
        # Insert hotspot user
        cursor = conn.execute('''
            INSERT INTO hotspot_users (username, password, profile_id, company_id)
            VALUES (?, ?, ?, ?)
        ''', (data['username'], data['password'], data['profile_id'], data['company_id']))
        
        user_id = cursor.lastrowid
        
        # Get default credits from settings
        default_credits = conn.execute(
            'SELECT setting_value FROM system_settings WHERE setting_key = ?',
            ('default_credits_mb',)
        ).fetchone()
        
        credits_mb = int(default_credits['setting_value']) if default_credits else 1024
        
        # Insert user credits
        conn.execute('''
            INSERT INTO user_credits (user_id, credits_mb, used_mb)
            VALUES (?, ?, 0)
        ''', (user_id, credits_mb))
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Usuário hotspot adicionado com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao adicionar usuário hotspot: {str(e)}'})
    finally:
        conn.close()

@app.route('/api/credits/update', methods=['POST'])
@login_required
def api_update_credits():
    conn = get_db()
    if not conn:
        return jsonify({'success': False, 'message': 'Erro de conexão com banco de dados'})
    
    try:
        data = request.get_json()
        user_id = data['user_id']
        credits_mb = data['credits_mb']
        
        # Update or insert credits
        conn.execute('''
            INSERT OR REPLACE INTO user_credits (user_id, credits_mb, used_mb, last_reset)
            VALUES (?, ?, COALESCE((SELECT used_mb FROM user_credits WHERE user_id = ?), 0), CURRENT_TIMESTAMP)
        ''', (user_id, credits_mb, user_id))
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Créditos atualizados com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao atualizar créditos: {str(e)}'})
    finally:
        conn.close()

if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
