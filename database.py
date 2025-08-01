import sqlite3
import hashlib
from datetime import datetime
from config import Config

def get_db_connection():
    """Conecta ao banco de dados SQLite"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa o banco de dados com as tabelas necessárias"""
    conn = get_db_connection()
    
    # Tabela de usuários do sistema
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'admin',
            user_type TEXT DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de empresas
    conn.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mikrotik_ip TEXT NOT NULL,
            mikrotik_user TEXT NOT NULL,
            mikrotik_password TEXT NOT NULL,
            mikrotik_port INTEGER DEFAULT 8728,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de perfis hotspot
    conn.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            rate_limit TEXT,
            session_timeout INTEGER,
            idle_timeout INTEGER,
            shared_users INTEGER DEFAULT 1,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    ''')
    
    # Tabela de usuários hotspot
    conn.execute('''
        CREATE TABLE IF NOT EXISTS hotspot_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            profile_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            name TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            credit_mb INTEGER DEFAULT 0,
            used_mb INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id),
            FOREIGN KEY (profile_id) REFERENCES profiles (id)
        )
    ''')
    
    # Tabela de configurações
    conn.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Inserir usuário admin padrão
    admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
    conn.execute('''
        INSERT OR IGNORE INTO users (name, email, password, role, user_type)
        VALUES (?, ?, ?, ?, ?)
    ''', ('Administrador', 'admin@demo.com', admin_password, 'admin', 'admin'))
    
    # Inserir configurações padrão
    default_settings = [
        ('default_credit_mb', '1024', 'Crédito padrão em MB'),
        ('credit_reset_time', '00:00', 'Horário de reset dos créditos'),
        ('enable_cumulative', '1', 'Habilitar sistema cumulativo'),
        ('system_timezone', 'America/Sao_Paulo', 'Fuso horário do sistema')
    ]
    
    for key, value, description in default_settings:
        conn.execute('''
            INSERT OR IGNORE INTO settings (key, value, description)
            VALUES (?, ?, ?)
        ''', (key, value, description))
    
    # Inserir empresa demo
    conn.execute('''
        INSERT OR IGNORE INTO companies (id, name, mikrotik_ip, mikrotik_user, mikrotik_password)
        VALUES (1, 'Empresa Demo', '192.168.1.1', 'admin', 'admin')
    ''')
    
    # Inserir perfil demo
    conn.execute('''
        INSERT OR IGNORE INTO profiles (id, company_id, name, rate_limit, session_timeout)
        VALUES (1, 1, 'Perfil Padrão', '10M/10M', 3600)
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Banco de dados inicializado com sucesso!")
