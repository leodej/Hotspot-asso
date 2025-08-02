from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_file
import sqlite3
import hashlib
import os
from datetime import datetime, timedelta
import requests
import json
from werkzeug.utils import secure_filename
import threading
import time
from routeros_api import RouterOsApiPool

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Database initialization
def init_db():
    conn = sqlite3.connect('mikrotik_manager.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Companies table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mikrotik_ip TEXT NOT NULL,
            mikrotik_username TEXT NOT NULL,
            mikrotik_password TEXT NOT NULL,
            mikrotik_port INTEGER DEFAULT 8728,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Profiles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            rate_limit TEXT,
            session_timeout INTEGER,
            idle_timeout INTEGER,
            shared_users INTEGER DEFAULT 1,
            company_id INTEGER,
            is_default INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    ''')
    
    # Hotspot users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hotspot_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            profile TEXT,
            company_id INTEGER,
            bytes_in INTEGER DEFAULT 0,
            bytes_out INTEGER DEFAULT 0,
            uptime TEXT DEFAULT '0s',
            status TEXT DEFAULT 'active',
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    ''')
    
    # Credits table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users_credits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            company_id INTEGER,
            amount DECIMAL(10,2),
            description TEXT,
            type TEXT DEFAULT 'credit',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES hotspot_users (id),
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    ''')
    
    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Connection logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS connection_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            company_id INTEGER,
            action TEXT,
            ip_address TEXT,
            mac_address TEXT,
            bytes_in INTEGER DEFAULT 0,
            bytes_out INTEGER DEFAULT 0,
            session_time INTEGER DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    ''')
    
    # Create default admin user
    cursor.execute('SELECT COUNT(*) FROM users WHERE role = "admin"')
    if cursor.fetchone()[0] == 0:
        admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                      ('admin', admin_password, 'admin'))
    
    # Insert default settings
    default_settings = [
        ('system_name', 'MikroTik Manager'),
        ('system_logo', '/static/images/logo.png'),
        ('data_collection_interval', '60')
    ]
    
    for key, value in default_settings:
        cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', (key, value))
    
    conn.commit()
    conn.close()

# MikroTik API connection
def connect_mikrotik(ip, username, password, port=8728):
    try:
        connection = RouterOsApiPool(ip, username=username, password=password, port=port, plaintext_login=True)
        api = connection.get_api()
        return api
    except Exception as e:
        print(f"Error connecting to MikroTik: {e}")
        return None

# Routes
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        
        conn = sqlite3.connect('mikrotik_manager.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, role FROM users WHERE username = ? AND password = ?', 
                      (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[2]
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('mikrotik_manager.db')
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) FROM companies WHERE status = "active"')
    total_companies = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM hotspot_users WHERE status = "active"')
    total_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM profiles')
    total_profiles = cursor.fetchone()[0]
    
    cursor.execute('SELECT SUM(amount) FROM users_credits WHERE type = "credit"')
    total_credits = cursor.fetchone()[0] or 0
    
    conn.close()
    
    stats = {
        'companies': total_companies,
        'users': total_users,
        'profiles': total_profiles,
        'credits': total_credits
    }
    
    return render_template('dashboard.html', stats=stats)

@app.route('/companies')
def companies():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('mikrotik_manager.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM companies ORDER BY created_at DESC')
    companies_list = cursor.fetchall()
    conn.close()
    
    return render_template('companies.html', companies=companies_list)

@app.route('/companies/add', methods=['POST'])
def add_company():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    conn = sqlite3.connect('mikrotik_manager.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO companies (name, mikrotik_ip, mikrotik_username, mikrotik_password, mikrotik_port)
        VALUES (?, ?, ?, ?, ?)
    ''', (data['name'], data['ip'], data['username'], data['password'], data.get('port', 8728)))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/companies/<int:company_id>/test')
def test_company_connection(company_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = sqlite3.connect('mikrotik_manager.db')
    cursor = conn.cursor()
    cursor.execute('SELECT mikrotik_ip, mikrotik_username, mikrotik_password, mikrotik_port FROM companies WHERE id = ?', (company_id,))
    company = cursor.fetchone()
    conn.close()
    
    if not company:
        return jsonify({'error': 'Company not found'}), 404
    
    api = connect_mikrotik(company[0], company[1], company[2], company[3])
    if api:
        try:
            # Test connection by getting system identity
            identity = api.get_resource('/system/identity').get()
            api.disconnect()
            return jsonify({'success': True, 'identity': identity[0]['name'] if identity else 'Unknown'})
        except:
            return jsonify({'error': 'Connection failed'})
    else:
        return jsonify({'error': 'Connection failed'})

@app.route('/companies/<int:company_id>/collect-usage')
def collect_company_usage(company_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        collect_usage_data(company_id)
        return jsonify({'success': True, 'message': 'Usage data collected successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/collect-all-usage')
def collect_all_usage():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        conn = sqlite3.connect('mikrotik_manager.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM companies WHERE status = "active"')
        companies = cursor.fetchall()
        conn.close()
        
        for company in companies:
            collect_usage_data(company[0])
        
        return jsonify({'success': True, 'message': f'Usage data collected for {len(companies)} companies'})
    except Exception as e:
        return jsonify({'error': str(e)})

def collect_usage_data(company_id):
    conn = sqlite3.connect('mikrotik_manager.db')
    cursor = conn.cursor()
    
    # Get company details
    cursor.execute('SELECT mikrotik_ip, mikrotik_username, mikrotik_password, mikrotik_port FROM companies WHERE id = ?', (company_id,))
    company = cursor.fetchone()
    
    if not company:
        conn.close()
        return
    
    api = connect_mikrotik(company[0], company[1], company[2], company[3])
    if not api:
        conn.close()
        return
    
    try:
        # Get active users
        active_users = api.get_resource('/ip/hotspot/active').get()
        
        for user in active_users:
            username = user.get('user', '')
            bytes_in = int(user.get('bytes-in', 0))
            bytes_out = int(user.get('bytes-out', 0))
            uptime = user.get('uptime', '0s')
            
            # Update user data in database
            cursor.execute('''
                UPDATE hotspot_users 
                SET bytes_in = ?, bytes_out = ?, uptime = ?, 
                    comment = ? 
                WHERE username = ? AND company_id = ?
            ''', (bytes_in, bytes_out, uptime, 
                  f'Total: {(bytes_in + bytes_out) / (1024*1024):.2f} MB', 
                  username, company_id))
            
            # Update comment in MikroTik
            try:
                users_resource = api.get_resource('/ip/hotspot/user')
                mikrotik_users = users_resource.get(name=username)
                if mikrotik_users:
                    user_id = mikrotik_users[0]['.id']
                    users_resource.set(id=user_id, comment=f'Total: {(bytes_in + bytes_out) / (1024*1024):.2f} MB')
            except:
                pass
        
        api.disconnect()
        conn.commit()
        
    except Exception as e:
        print(f"Error collecting usage data: {e}")
    finally:
        conn.close()

@app.route('/profiles')
def profiles():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('mikrotik_manager.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, c.name as company_name 
        FROM profiles p 
        LEFT JOIN companies c ON p.company_id = c.id 
        ORDER BY p.created_at DESC
    ''')
    profiles_list = cursor.fetchall()
    
    cursor.execute('SELECT id, name FROM companies WHERE status = "active"')
    companies_list = cursor.fetchall()
    
    conn.close()
    
    return render_template('profiles.html', profiles=profiles_list, companies=companies_list)

@app.route('/hotspot-users')
def hotspot_users():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    company_filter = request.args.get('company', '')
    
    conn = sqlite3.connect('mikrotik_manager.db')
    cursor = conn.cursor()
    
    base_query = '''
        SELECT hu.*, c.name as company_name, p.name as profile_name
        FROM hotspot_users hu 
        LEFT JOIN companies c ON hu.company_id = c.id 
        LEFT JOIN profiles p ON hu.profile = p.name AND hu.company_id = p.company_id
    '''
    params = []
    
    if company_filter:
        base_query += ' WHERE hu.company_id = ?'
        params.append(company_filter)
    
    base_query += ' ORDER BY hu.created_at DESC'
    
    cursor.execute(base_query, params)
    users_list = cursor.fetchall()
    
    cursor.execute('SELECT id, name FROM companies WHERE status = "active"')
    companies_list = cursor.fetchall()
    
    conn.close()
    
    return render_template('hotspot_users.html', users=users_list, companies=companies_list, selected_company=company_filter)

@app.route('/credits')
def credits():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    company_filter = request.args.get('company', '')
    month_filter = request.args.get('month', '')
    
    conn = sqlite3.connect('mikrotik_manager.db')
    cursor = conn.cursor()
    
    base_query = '''
        SELECT uc.*, hu.username, c.name as company_name
        FROM users_credits uc 
        LEFT JOIN hotspot_users hu ON uc.user_id = hu.id 
        LEFT JOIN companies c ON uc.company_id = c.id
        WHERE 1=1
    '''
    params = []
    
    if company_filter:
        base_query += ' AND uc.company_id = ?'
        params.append(company_filter)
    
    if month_filter:
        base_query += ' AND strftime("%Y-%m", uc.created_at) = ?'
        params.append(month_filter)
    
    base_query += ' ORDER BY uc.updated_at DESC'
    
    cursor.execute(base_query, params)
    credits_list = cursor.fetchall()
    
    cursor.execute('SELECT id, name FROM companies WHERE status = "active"')
    companies_list = cursor.fetchall()
    
    conn.close()
    
    return render_template('credits.html', credits=credits_list, companies=companies_list, 
                         selected_company=company_filter, selected_month=month_filter)

@app.route('/settings')
def settings():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('mikrotik_manager.db')
    cursor = conn.cursor()
    cursor.execute('SELECT key, value FROM settings')
    settings_data = dict(cursor.fetchall())
    conn.close()
    
    return render_template('settings.html', settings=settings_data)

@app.route('/settings/update', methods=['POST'])
def update_settings():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    conn = sqlite3.connect('mikrotik_manager.db')
    cursor = conn.cursor()
    
    for key, value in data.items():
        cursor.execute('UPDATE settings SET value = ?, updated_at = CURRENT_TIMESTAMP WHERE key = ?', (value, key))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/reports')
def reports():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('reports.html')

# Background task for automatic data collection
def background_data_collection():
    while True:
        try:
            conn = sqlite3.connect('mikrotik_manager.db')
            cursor = conn.cursor()
            
            # Get collection interval from settings
            cursor.execute('SELECT value FROM settings WHERE key = "data_collection_interval"')
            interval = int(cursor.fetchone()[0] or 60)
            
            # Get all active companies
            cursor.execute('SELECT id FROM companies WHERE status = "active"')
            companies = cursor.fetchall()
            conn.close()
            
            # Collect data for each company
            for company in companies:
                collect_usage_data(company[0])
            
            time.sleep(interval)
            
        except Exception as e:
            print(f"Background collection error: {e}")
            time.sleep(60)

if __name__ == '__main__':
    init_db()
    
    # Start background data collection thread
    collection_thread = threading.Thread(target=background_data_collection, daemon=True)
    collection_thread.start()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
