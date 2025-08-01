import sqlite3
import uuid
from config import Config

def get_db():
    """Conecta ao banco de dados SQLite"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa o banco de dados com as tabelas necessárias"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()
    
    # Tabela de usuários do sistema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            user_type TEXT DEFAULT 'admin',
            hotspot_user_id TEXT,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (hotspot_user_id) REFERENCES hotspot_users (id)
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
        INSERT OR IGNORE INTO system_users (id, email, password, name, role, user_type)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (str(uuid.uuid4()), 'admin@demo.com', 'admin123', 'Administrador Sistema', 'admin', 'admin'))
    
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
