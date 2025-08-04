from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_from_directory
import os
import json
from datetime import datetime, timedelta
import hashlib
import sqlite3
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
import socket
import paramiko
import time
import re
import threading
from threading import Timer
import schedule
from datetime import timezone
import pytz
import locale
from datetime import timezone

app = Flask(__name__)
app.secret_key = 'mikrotik-manager-super-secret-key-2024'

# Configurar timezone do sistema
os.environ['TZ'] = 'America/Sao_Paulo'
time.tzset()

# Configurações
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Criar pasta de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Timer para coleta automática
usage_collection_timer = None

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
            connection_status TEXT DEFAULT 'disconnected',
            last_connection_test TIMESTAMP,
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
    
    # Tabela de logs de conexão MikroTik
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mikrotik_connection_logs (
            id TEXT PRIMARY KEY,
            company_id TEXT,
            action TEXT NOT NULL,
            status TEXT NOT NULL,
            message TEXT,
            response_time REAL,
            ip_address TEXT,
            port INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
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
        ('system_timezone', 'America/Sao_Paulo', 'Timezone do sistema'),
        ('system_name', 'MikroTik Manager', 'Nome do sistema'),
        ('system_logo', '', 'Logo do sistema'),
        ('auto_collect_usage', '1', 'Coleta automática de uso a cada minuto')
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

def allowed_file(filename):
    """Verifica se o arquivo é permitido"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'svg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_image(image_path, size=(64, 64)):
    """Redimensiona imagem mantendo proporção"""
    try:
        with Image.open(image_path) as img:
            # Converter para RGB se necessário
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Redimensionar mantendo proporção
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Criar nova imagem com fundo branco
            new_img = Image.new('RGB', size, (255, 255, 255))
            
            # Centralizar a imagem redimensionada
            x = (size[0] - img.width) // 2
            y = (size[1] - img.height) // 2
            new_img.paste(img, (x, y))
            
            # Salvar
            new_img.save(image_path, 'PNG', quality=95)
            return True
    except Exception as e:
        print(f"Erro ao redimensionar imagem: {e}")
        return False

def log_mikrotik_connection(company_id, action, status, message, response_time=None, ip_address=None, port=None):
    """Registra log de conexão com MikroTik"""
    conn = get_db()
    conn.execute('''
        INSERT INTO mikrotik_connection_logs (id, company_id, action, status, message, response_time, ip_address, port)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (str(uuid.uuid4()), company_id, action, status, message, response_time, ip_address, port))
    conn.commit()
    conn.close()

def test_mikrotik_connection(company_id, ip_address, port, username, password):
    """Testa conexão com MikroTik via SSH"""
    start_time = time.time()
    
    try:
        # Testar conexão TCP primeiro
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((ip_address, int(port)))
        sock.close()
        
        if result != 0:
            response_time = time.time() - start_time
            log_mikrotik_connection(
                company_id, 'test_connection', 'failed', 
                f'Porta {port} não está acessível', 
                response_time, ip_address, port
            )
            return False, f'Porta {port} não está acessível'
        
        # Testar conexão SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        ssh.connect(
            hostname=ip_address,
            port=int(port),
            username=username,
            password=password,
            timeout=10
        )
        
        # Executar comando simples para verificar se está funcionando
        stdin, stdout, stderr = ssh.exec_command('/system identity print')
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        ssh.close()
        
        response_time = time.time() - start_time
        
        if error:
            log_mikrotik_connection(
                company_id, 'test_connection', 'failed', 
                f'Erro na execução do comando: {error}', 
                response_time, ip_address, port
            )
            return False, f'Erro na execução do comando: {error}'
        
        log_mikrotik_connection(
            company_id, 'test_connection', 'success', 
            'Conexão estabelecida com sucesso', 
            response_time, ip_address, port
        )
        
        # Atualizar status da empresa
        conn = get_db()
        conn.execute('''
            UPDATE companies 
            SET connection_status = 'connected', last_connection_test = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (company_id,))
        conn.commit()
        conn.close()
        
        return True, 'Conexão estabelecida com sucesso'
        
    except paramiko.AuthenticationException:
        response_time = time.time() - start_time
        log_mikrotik_connection(
            company_id, 'test_connection', 'failed', 
            'Falha na autenticação - usuário ou senha incorretos', 
            response_time, ip_address, port
        )
        return False, 'Falha na autenticação - usuário ou senha incorretos'
        
    except paramiko.SSHException as e:
        response_time = time.time() - start_time
        log_mikrotik_connection(
            company_id, 'test_connection', 'failed', 
            f'Erro SSH: {str(e)}', 
            response_time, ip_address, port
        )
        return False, f'Erro SSH: {str(e)}'
        
    except socket.timeout:
        response_time = time.time() - start_time
        log_mikrotik_connection(
            company_id, 'test_connection', 'failed', 
            'Timeout na conexão', 
            response_time, ip_address, port
        )
        return False, 'Timeout na conexão'
        
    except Exception as e:
        response_time = time.time() - start_time
        log_mikrotik_connection(
            company_id, 'test_connection', 'failed', 
            f'Erro inesperado: {str(e)}', 
            response_time, ip_address, port
        )
        return False, f'Erro inesperado: {str(e)}'

def collect_user_usage_from_mikrotik(company_id):
    """Coleta dados de uso dos usuários do MikroTik"""
    conn = get_db()
    company = conn.execute('SELECT * FROM companies WHERE id = ?', (company_id,)).fetchone()
    
    if not company:
        return False, 'Empresa não encontrada'
    
    start_time = time.time()
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        ssh.connect(
            hostname=company['mikrotik_ip'],
            port=int(company['mikrotik_port']),
            username=company['mikrotik_user'],
            password=company['mikrotik_password'],
            timeout=10
        )
        
        # Executar comando para listar usuários hotspot com detalhes
        stdin, stdout, stderr = ssh.exec_command('/ip hotspot user print where comment~".*"')
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        ssh.close()
        
        if error:
            response_time = time.time() - start_time
            log_mikrotik_connection(
                company_id, 'collect_usage', 'failed', 
                f'Erro ao coletar dados: {error}', 
                response_time, company['mikrotik_ip'], company['mikrotik_port']
            )
            return False, f'Erro ao coletar dados: {error}'
        
        # Parse dos dados de usuários
        users_data = parse_mikrotik_users_usage(output)
        
        # Atualizar dados no banco
        updated_count = 0
        
        for user_data in users_data:
            username = user_data.get('name', '')
            comment = user_data.get('comment', '')
            
            if not username:
                continue
            
            # Buscar usuário no sistema
            local_user = conn.execute(
                'SELECT id FROM hotspot_users WHERE username = ? AND company_id = ?', 
                (username, company_id)
            ).fetchone()
            
            if local_user:
                # Extrair dados de uso do comment
                used_mb = parse_usage_from_comment(comment)
                
                if used_mb is not None:
                    # Buscar crédito do usuário
                    credit = conn.execute(
                        'SELECT * FROM user_credits WHERE hotspot_user_id = ?', 
                        (local_user['id'],)
                    ).fetchone()
                    
                    if credit:
                        # Calcular remaining_mb
                        remaining_mb = max(0, credit['total_mb'] - used_mb)
                        
                        # Atualizar créditos usados
                        conn.execute('''
                            UPDATE user_credits 
                            SET used_mb = ?, remaining_mb = ?, updated_at = CURRENT_TIMESTAMP
                            WHERE hotspot_user_id = ?
                        ''', (used_mb, remaining_mb, local_user['id']))
                    else:
                        # Criar registro de crédito se não existir
                        default_credit = int(get_setting('default_credit_mb', 1024))
                        remaining_mb = max(0, default_credit - used_mb)
                        conn.execute('''
                            INSERT INTO user_credits (id, hotspot_user_id, total_mb, used_mb, remaining_mb, last_reset)
                            VALUES (?, ?, ?, ?, ?, DATE('now'))
                        ''', (str(uuid.uuid4()), local_user['id'], default_credit, used_mb, remaining_mb))
                    
                    updated_count += 1
        
        conn.commit()
        conn.close()
        
        response_time = time.time() - start_time
        message = f'Coletados dados de uso de {updated_count} usuários'
        
        log_mikrotik_connection(
            company_id, 'collect_usage', 'success', 
            message, response_time, company['mikrotik_ip'], company['mikrotik_port']
        )
        
        return True, message
        
    except Exception as e:
        response_time = time.time() - start_time
        error_message = f'Erro na coleta de uso: {str(e)}'
        
        log_mikrotik_connection(
            company_id, 'collect_usage', 'failed', 
            error_message, response_time, company['mikrotik_ip'], company['mikrotik_port']
        )
        
        return False, error_message

def parse_mikrotik_users_usage(output):
    """Faz parsing da saída do comando /ip hotspot user print where comment~".*" """
    users = []
    lines = output.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Procurar por linha de consumo que começa com ";;; Consumo total:"
        if line.startswith(';;; Consumo total:'):
            # Extrair o valor de consumo
            consumption_line = line
            
            # Próxima linha deve conter os dados do usuário
            if i + 1 < len(lines):
                user_line = lines[i + 1].strip()
                
                # Parse da linha do usuário: número, nome, perfil, tempo
                # Exemplo: "6             eng.geirkvig    default        4h52s"
                parts = user_line.split()
                if len(parts) >= 2:
                    # O nome do usuário é sempre a segunda parte
                    username = parts[1]
                    
                    user_data = {
                        'name': username,
                        'comment': consumption_line
                    }
                    users.append(user_data)
                
                i += 2  # Pular as duas linhas processadas
            else:
                i += 1
        else:
            i += 1
    
    return users

def parse_usage_from_comment(comment):
    """Extrai o total de uso em MB do campo comment"""
    if not comment:
        return None
    
    try:
        # Procurar por padrão ";;; Consumo total: XXX.XX MB" ou ";;; Consumo total: X.XX GB"
        if ';;; Consumo total:' in comment:
            # Extrair a parte após "Consumo total:"
            consumption_part = comment.split('Consumo total:')[1].strip()
            
            # Procurar por MB
            mb_match = re.search(r'(\d+(?:\.\d+)?)\s*MB', consumption_part, re.IGNORECASE)
            if mb_match:
                return int(float(mb_match.group(1)))
            
            # Procurar por GB
            gb_match = re.search(r'(\d+(?:\.\d+)?)\s*GB', consumption_part, re.IGNORECASE)
            if gb_match:
                return int(float(gb_match.group(1)) * 1024)
        
        # Fallback para outros formatos
        # Primeiro tentar MB
        mb_match = re.search(r'(\d+(?:\.\d+)?)\s*MB', comment, re.IGNORECASE)
        if mb_match:
            return int(float(mb_match.group(1)))
        
        # Tentar GB
        gb_match = re.search(r'(\d+(?:\.\d+)?)\s*GB', comment, re.IGNORECASE)
        if gb_match:
            return int(float(gb_match.group(1)) * 1024)
        
        # Tentar KB
        kb_match = re.search(r'(\d+(?:\.\d+)?)\s*KB', comment, re.IGNORECASE)
        if kb_match:
            return int(float(kb_match.group(1)) / 1024)
            
    except (ValueError, AttributeError):
        pass
    
    return None

def collect_all_companies_usage():
    """Coleta dados de uso de todas as empresas ativas"""
    conn = get_db()
    companies = conn.execute('SELECT id FROM companies WHERE active = 1').fetchall()
    conn.close()
    
    for company in companies:
        try:
            collect_user_usage_from_mikrotik(company['id'])
        except Exception as e:
            print(f"Erro ao coletar dados da empresa {company['id']}: {e}")

def schedule_usage_collection():
    """Agenda a próxima coleta de uso"""
    global usage_collection_timer
    
    # Verificar se a coleta automática está habilitada
    auto_collect = get_setting('auto_collect_usage', '1') == '1'
    
    if auto_collect:
        # Executar coleta
        collect_all_companies_usage()
    
    # Agendar próxima execução em 60 segundos
    usage_collection_timer = Timer(60.0, schedule_usage_collection)
    usage_collection_timer.daemon = True
    usage_collection_timer.start()

def create_mikrotik_profile(company_id, profile_name, download_limit, upload_limit, time_limit=None):
    """Cria perfil no MikroTik"""
    conn = get_db()
    company = conn.execute('SELECT * FROM companies WHERE id = ?', (company_id,)).fetchone()
    conn.close()
    
    if not company:
        return False, 'Empresa não encontrada'
    
    start_time = time.time()
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        ssh.connect(
            hostname=company['mikrotik_ip'],
            port=int(company['mikrotik_port']),
            username=company['mikrotik_user'],
            password=company['mikrotik_password'],
            timeout=10
        )
        
        # Construir comando para criar perfil
        rate_limit = f"{upload_limit}M/{download_limit}M"
        command = f'/ip hotspot user profile add name="{profile_name}" rate-limit="{rate_limit}"'
        
        # Adicionar limite de tempo se especificado
        if time_limit:
            command += f' session-timeout="{time_limit}m"'
        
        stdin, stdout, stderr = ssh.exec_command(command)
        error = stderr.read().decode('utf-8')
        
        ssh.close()
        
        response_time = time.time() - start_time
        
        if error and 'already exists' not in error:
            log_mikrotik_connection(
                company_id, 'create_profile', 'failed', 
                f'Erro ao criar perfil {profile_name}: {error}', 
                response_time, company['mikrotik_ip'], company['mikrotik_port']
            )
            return False, f'Erro ao criar perfil: {error}'
        
        message = f'Perfil {profile_name} criado com sucesso'
        if 'already exists' in error:
            message = f'Perfil {profile_name} já existe no MikroTik'
        
        log_mikrotik_connection(
            company_id, 'create_profile', 'success', 
            message, response_time, company['mikrotik_ip'], company['mikrotik_port']
        )
        
        return True, message
        
    except Exception as e:
        response_time = time.time() - start_time
        error_message = f'Erro ao criar perfil {profile_name}: {str(e)}'
        
        log_mikrotik_connection(
            company_id, 'create_profile', 'failed', 
            error_message, response_time, company['mikrotik_ip'], company['mikrotik_port']
        )
        
        return False, error_message

def import_mikrotik_users(company_id):
    """Importa usuários hotspot do MikroTik para o sistema"""
    conn = get_db()
    company = conn.execute('SELECT * FROM companies WHERE id = ?', (company_id,)).fetchone()
    
    if not company:
        return False, 'Empresa não encontrada'
    
    start_time = time.time()
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        ssh.connect(
            hostname=company['mikrotik_ip'],
            port=int(company['mikrotik_port']),
            username=company['mikrotik_user'],
            password=company['mikrotik_password'],
            timeout=10
        )
        
        # Executar comando para listar usuários hotspot
        stdin, stdout, stderr = ssh.exec_command('/ip hotspot user print detail')
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        ssh.close()
        
        if error:
            response_time = time.time() - start_time
            log_mikrotik_connection(
                company_id, 'import_users', 'failed', 
                f'Erro ao listar usuários: {error}', 
                response_time, company['mikrotik_ip'], company['mikrotik_port']
            )
            return False, f'Erro ao listar usuários: {error}'
        
        # Fazer parsing da saída
        users_data = parse_mikrotik_users(output)
        
        imported_count = 0
        skipped_count = 0
        default_credit = int(get_setting('default_credit_mb', 1024))
        
        for user_data in users_data:
            username = user_data.get('name', '')
            password = user_data.get('password', 'imported123')  # Senha padrão para importados
            profile_name = user_data.get('profile', 'default')
            disabled = user_data.get('disabled', 'false') == 'true'
            
            if not username:
                continue
            
            # Verificar se usuário já existe
            existing_user = conn.execute(
                'SELECT id FROM hotspot_users WHERE username = ? AND company_id = ?', 
                (username, company_id)
            ).fetchone()
            
            if existing_user:
                skipped_count += 1
                continue
            
            # Buscar perfil no sistema (se existir)
            profile_id = None
            if profile_name != 'default':
                profile = conn.execute(
                    'SELECT id FROM hotspot_profiles WHERE name = ? AND company_id = ?', 
                    (profile_name, company_id)
                ).fetchone()
                if profile:
                    profile_id = profile['id']
            
            # Inserir usuário
            user_id = str(uuid.uuid4())
            user_active = 0 if disabled else 1
            
            conn.execute('''
                INSERT INTO hotspot_users (id, company_id, profile_id, username, password, turma, active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, company_id, profile_id, username, password, company['turma_ativa'], user_active))
            
            # Criar crédito inicial
            conn.execute('''
                INSERT INTO user_credits (id, hotspot_user_id, total_mb, remaining_mb, last_reset)
                VALUES (?, ?, ?, ?, DATE('now'))
            ''', (str(uuid.uuid4()), user_id, default_credit, default_credit))
            
            imported_count += 1
        
        conn.commit()
        conn.close()
        
        response_time = time.time() - start_time
        message = f'Importados {imported_count} usuários, {skipped_count} já existiam'
        
        log_mikrotik_connection(
            company_id, 'import_users', 'success', 
            message, response_time, company['mikrotik_ip'], company['mikrotik_port']
        )
        
        return True, message
        
    except Exception as e:
        response_time = time.time() - start_time
        error_message = f'Erro na importação: {str(e)}'
        
        log_mikrotik_connection(
            company_id, 'import_users', 'failed', 
            error_message, response_time, company['mikrotik_ip'], company['mikrotik_port']
        )
        
        return False, error_message

def parse_mikrotik_users(output):
    """Faz parsing da saída do comando /ip hotspot user print detail"""
    users = []
    current_user = {}
    
    lines = output.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Nova entrada de usuário (começa com número)
        if re.match(r'^\d+', line):
            if current_user:
                users.append(current_user)
            current_user = {}
            continue
        
        # Parsing dos campos usando regex para extrair valores corretos
        if 'name=' in line:
            # Extrair nome: name="valor" ou name=valor
            name_match = re.search(r'name=(?:"([^"]+)"|([^\s]+))', line)
            if name_match:
                current_user['name'] = name_match.group(1) or name_match.group(2)
        
        if 'password=' in line:
            # Extrair senha: password="valor" ou password=valor
            password_match = re.search(r'password=(?:"([^"]+)"|([^\s]+))', line)
            if password_match:
                current_user['password'] = password_match.group(1) or password_match.group(2)
        
        if 'profile=' in line:
            # Extrair perfil: profile="valor" ou profile=valor
            profile_match = re.search(r'profile=(?:"([^"]+)"|([^\s]+))', line)
            if profile_match:
                current_user['profile'] = profile_match.group(1) or profile_match.group(2)
        
        if 'disabled=' in line:
            # Extrair status disabled: disabled=true ou disabled=false
            disabled_match = re.search(r'disabled=([^\s]+)', line)
            if disabled_match:
                current_user['disabled'] = disabled_match.group(1)
    
    # Adicionar último usuário
    if current_user:
        users.append(current_user)
    
    return users

def sync_credits_to_mikrotik_total_bytes():
    """Sincroniza créditos disponíveis com total-bytes no MikroTik"""
    print("🔄 Iniciando sincronização de créditos para MikroTik...")
    
    conn = get_db()
    
    # Buscar todas as empresas ativas
    companies = conn.execute('SELECT * FROM companies WHERE active = 1').fetchall()
    
    total_synced = 0
    total_errors = 0
    
    for company in companies:
        try:
            # Buscar usuários ativos da turma ativa com seus créditos
            users_with_credits = conn.execute('''
                SELECT hu.username, uc.remaining_mb
                FROM hotspot_users hu
                JOIN user_credits uc ON hu.id = uc.hotspot_user_id
                WHERE hu.company_id = ? AND hu.active = 1 AND hu.turma = ?
                AND uc.remaining_mb > 0
            ''', (company['id'], company['turma_ativa'])).fetchall()
            
            if not users_with_credits:
                continue
            
            # Conectar no MikroTik
            start_time = time.time()
            
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            ssh.connect(
                hostname=company['mikrotik_ip'],
                port=int(company['mikrotik_port']),
                username=company['mikrotik_user'],
                password=company['mikrotik_password'],
                timeout=15
            )
            
            company_synced = 0
            
            for user in users_with_credits:
                try:
                    # Converter MB para bytes (MikroTik usa bytes)
                    total_bytes = int(user['remaining_mb'] * 1024 * 1024)
                    
                    # Comando para definir total-bytes do usuário
                    command = f'/ip hotspot user set [find name="{user["username"]}"] bytes-total={total_bytes}'
                    
                    stdin, stdout, stderr = ssh.exec_command(command)
                    error = stderr.read().decode('utf-8')
                    
                    if not error:
                        company_synced += 1
                        total_synced += 1
                    else:
                        print(f"❌ Erro ao sincronizar {user['username']}: {error}")
                        total_errors += 1
                        
                except Exception as e:
                    print(f"❌ Erro ao processar usuário {user['username']}: {e}")
                    total_errors += 1
            
            ssh.close()
            
            response_time = time.time() - start_time
            message = f'Sincronizados {company_synced} usuários com total-bytes'
            
            log_mikrotik_connection(
                company['id'], 'sync_credits_to_bytes', 'success', 
                message, response_time, company['mikrotik_ip'], company['mikrotik_port']
            )
            
            print(f"✅ {company['name']}: {message}")
            
        except Exception as e:
            error_message = f'Erro na sincronização de créditos: {str(e)}'
            print(f"❌ {company['name']}: {error_message}")
            
            log_mikrotik_connection(
                company['id'], 'sync_credits_to_bytes', 'failed', 
                error_message, 0, company['mikrotik_ip'], company['mikrotik_port']
            )
            total_errors += 1
    
    conn.close()
    
    print(f"🎯 Sincronização concluída: {total_synced} sucessos, {total_errors} erros")
    return total_synced, total_errors

def schedule_daily_credit_sync():
    """Agenda a sincronização diária de créditos às 00:00 (horário do Brasil)"""
    
    # Usar timezone do sistema
    import time
    time.tzset()
    
    def run_credit_accumulation():
        try:
            print("🇧🇷 Executando acúmulo diário de créditos (23:58 Brasil)...")
            update_credits_cumulative()
            print("✅ Acúmulo de créditos concluído com sucesso!")
        except Exception as e:
            print(f"❌ Erro no acúmulo de créditos: {e}")
    
    def run_sync():
        try:
            print("🇧🇷 Executando sincronização diária de créditos (00:00 Brasil)...")
            sync_credits_to_mikrotik_total_bytes()
        except Exception as e:
            print(f"❌ Erro na sincronização diária: {e}")
    
    # Agendar acúmulo de créditos às 23:58 (2 minutos antes da sincronização)
    schedule.every().day.at("23:58").do(run_credit_accumulation)
    
    # Agendar sincronização para MikroTik às 00:00 (horário do Brasil)
    schedule.every().day.at("00:00").do(run_sync)
    
    print("📅 Agendamentos diários configurados:")
    print("   - Acúmulo de créditos: 23:58 (Brasil)")
    print("   - Sincronização MikroTik: 00:00 (Brasil)")
    
    # Thread para executar o schedule
    def run_scheduler():
        while True:
            # Verificar se há tarefas agendadas para executar
            schedule.run_pending()
            time.sleep(60)  # Verificar a cada minuto
    
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

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

def create_database_backup():
    """Cria backup completo do banco de dados"""
    try:
        import tempfile
        import shutil
        from datetime import datetime
        
        # Criar arquivo temporário para o backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"mikrotik_manager_backup_{timestamp}.db"
        
        # Copiar banco atual para arquivo temporário
        temp_backup_path = os.path.join(tempfile.gettempdir(), backup_filename)
        shutil.copy2('mikrotik_manager.db', temp_backup_path)
        
        return temp_backup_path, backup_filename
        
    except Exception as e:
        return None, str(e)

def restore_database_backup(backup_file_path):
    """Restaura backup do banco de dados"""
    try:
        import shutil
        
        # Fazer backup do banco atual antes de restaurar
        current_backup = f"mikrotik_manager_backup_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2('mikrotik_manager.db', current_backup)
        
        # Restaurar o backup
        shutil.copy2(backup_file_path, 'mikrotik_manager.db')
        
        return True, f"Backup restaurado com sucesso. Backup anterior salvo como: {current_backup}"
        
    except Exception as e:
        return False, f"Erro ao restaurar backup: {str(e)}"

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
        mikrotik_port = request.form.get('mikrotik_port', 22)
        mikrotik_user = request.form.get('mikrotik_user')
        mikrotik_password = request.form.get('mikrotik_password')
        turma_ativa = request.form.get('turma_ativa', 'A')
        
        if not all([name, mikrotik_ip, mikrotik_user, mikrotik_password]):
            flash('Todos os campos são obrigatórios', 'error')
        else:
            conn = get_db()
            company_id = str(uuid.uuid4())
            conn.execute('''
                INSERT INTO companies (id, name, mikrotik_ip, mikrotik_port, mikrotik_user, mikrotik_password, turma_ativa)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (company_id, name, mikrotik_ip, int(mikrotik_port), mikrotik_user, mikrotik_password, turma_ativa))
            conn.commit()
            conn.close()
            
            # Testar conexão automaticamente
            success, message = test_mikrotik_connection(company_id, mikrotik_ip, mikrotik_port, mikrotik_user, mikrotik_password)
            
            if success:
                flash(f'Empresa cadastrada e conexão testada com sucesso!', 'success')
            else:
                flash(f'Empresa cadastrada, mas falha na conexão: {message}', 'warning')
        
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
    
    # Buscar configurações atuais
    current_settings = {}
    settings_rows = conn.execute('SELECT key, value FROM system_settings').fetchall()
    for row in settings_rows:
        current_settings[row['key']] = row['value']
    
    conn.close()

    return render_template('companies.html', 
                         user={'name': session.get('name')}, 
                         companies_list=companies_list,
                         settings=current_settings)

@app.route('/companies/<company_id>/edit', methods=['POST'])
@require_auth
def edit_company(company_id):
    """Editar empresa"""
    name = request.form.get('name')
    mikrotik_ip = request.form.get('mikrotik_ip')
    mikrotik_port = request.form.get('mikrotik_port', 22)
    mikrotik_user = request.form.get('mikrotik_user')
    mikrotik_password = request.form.get('mikrotik_password')
    turma_ativa = request.form.get('turma_ativa', 'A')
    
    if not all([name, mikrotik_ip, mikrotik_user, mikrotik_password]):
        flash('Todos os campos são obrigatórios', 'error')
    else:
        conn = get_db()
        conn.execute('''
            UPDATE companies 
            SET name = ?, mikrotik_ip = ?, mikrotik_port = ?, mikrotik_user = ?, mikrotik_password = ?, turma_ativa = ?
            WHERE id = ?
        ''', (name, mikrotik_ip, int(mikrotik_port), mikrotik_user, mikrotik_password, turma_ativa, company_id))
        conn.commit()
        conn.close()
        
        flash('Empresa atualizada com sucesso!', 'success')
    
    return redirect(url_for('companies'))

@app.route('/companies/<company_id>/test-connection', methods=['POST'])
@require_auth
def test_company_connection(company_id):
    """Testar conexão com MikroTik de uma empresa"""
    conn = get_db()
    company = conn.execute('SELECT * FROM companies WHERE id = ?', (company_id,)).fetchone()
    conn.close()
    
    if not company:
        flash('Empresa não encontrada', 'error')
        return redirect(url_for('companies'))
    
    success, message = test_mikrotik_connection(
        company_id, 
        company['mikrotik_ip'], 
        company['mikrotik_port'], 
        company['mikrotik_user'], 
        company['mikrotik_password']
    )
    
    if success:
        flash(f'Conexão com {company["name"]}: {message}', 'success')
    else:
        flash(f'Falha na conexão com {company["name"]}: {message}', 'error')
    
    return redirect(url_for('companies'))

@app.route('/companies/<company_id>/sync-users', methods=['POST'])
@require_auth
def sync_company_users(company_id):
    """Sincronizar usuários com MikroTik"""
    conn = get_db()
    company = conn.execute('SELECT name FROM companies WHERE id = ?', (company_id,)).fetchone()
    conn.close()
    
    if not company:
        flash('Empresa não encontrada', 'error')
        return redirect(url_for('companies'))
    
    success, message = sync_hotspot_users_to_mikrotik(company_id)
    
    if success:
        flash(f'Sincronização com {company["name"]}: {message}', 'success')
    else:
        flash(f'Falha na sincronização com {company["name"]}: {message}', 'error')
    
    return redirect(url_for('companies'))

@app.route('/companies/<company_id>/import-users', methods=['POST'])
@require_auth
def import_company_users(company_id):
    """Importar usuários do MikroTik"""
    conn = get_db()
    company = conn.execute('SELECT name FROM companies WHERE id = ?', (company_id,)).fetchone()
    conn.close()
    
    if not company:
        flash('Empresa não encontrada', 'error')
        return redirect(url_for('companies'))
    
    success, message = import_mikrotik_users(company_id)
    
    if success:
        flash(f'Importação de {company["name"]}: {message}', 'success')
    else:
        flash(f'Falha na importação de {company["name"]}: {message}', 'error')
    
    return redirect(url_for('companies'))

@app.route('/companies/<company_id>/collect-usage', methods=['POST'])
@require_auth
def collect_company_usage(company_id):
    """Coletar dados de uso de uma empresa específica"""
    conn = get_db()
    company = conn.execute('SELECT name FROM companies WHERE id = ?', (company_id,)).fetchone()
    conn.close()
    
    if not company:
        flash('Empresa não encontrada', 'error')
        return redirect(url_for('companies'))
    
    success, message = collect_user_usage_from_mikrotik(company_id)
    
    if success:
        flash(f'Coleta de uso de {company["name"]}: {message}', 'success')
    else:
        flash(f'Falha na coleta de uso de {company["name"]}: {message}', 'error')
    
    return redirect(url_for('companies'))

@app.route('/collect-all-usage', methods=['POST'])
@require_auth
def collect_all_usage():
    """Coletar dados de uso de todas as empresas"""
    try:
        collect_all_companies_usage()
        flash('Coleta de uso de todas as empresas executada com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro na coleta de uso: {str(e)}', 'error')
    
    return redirect(url_for('companies'))

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
        
        # Sincronizar automaticamente com MikroTik
        sync_hotspot_users_to_mikrotik(company_id)
        
        flash(f'Turma ativa atualizada para {turma_ativa} e sincronizada!', 'success')
    
    return redirect(url_for('companies'))

@app.route('/mikrotik-logs')
@require_auth
def mikrotik_logs():
    """Página de logs de conexão MikroTik"""
    # Obter filtros da URL
    company_filter = request.args.get('company', '')
    action_filter = request.args.get('action', '')
    status_filter = request.args.get('status', '')
    
    conn = get_db()
    
    # Construir query base
    base_query = '''
        SELECT ml.*, c.name as company_name
        FROM mikrotik_connection_logs ml
        JOIN companies c ON ml.company_id = c.id
        WHERE 1=1
    '''
    
    params = []
    
    # Aplicar filtros
    if company_filter:
        base_query += ' AND c.id = ?'
        params.append(company_filter)
    
    if action_filter:
        base_query += ' AND ml.action = ?'
        params.append(action_filter)
    
    if status_filter:
        base_query += ' AND ml.status = ?'
        params.append(status_filter)
    
    base_query += ' ORDER BY ml.created_at DESC LIMIT 500'
    
    # Buscar logs
    logs_list = conn.execute(base_query, params).fetchall()
    
    # Buscar empresas para o filtro
    companies_list = conn.execute('SELECT * FROM companies WHERE active = 1 ORDER BY name').fetchall()
    
    # Estatísticas dos logs
    stats = conn.execute('''
        SELECT 
            COUNT(*) as total_logs,
            COUNT(CASE WHEN status = 'success' THEN 1 END) as success_count,
            COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_count,
            AVG(response_time) as avg_response_time
        FROM mikrotik_connection_logs
        WHERE created_at >= datetime('now', '-24 hours')
    ''').fetchone()
    
    conn.close()
    
    return render_template('mikrotik_logs.html', 
                         user={'name': session.get('name')},
                         logs_list=logs_list,
                         companies_list=companies_list,
                         stats=stats,
                         selected_company=company_filter,
                         selected_action=action_filter,
                         selected_status=status_filter)

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
            profile_id = str(uuid.uuid4())
            conn.execute('''
                INSERT INTO hotspot_profiles (id, company_id, name, download_limit, upload_limit, time_limit)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (profile_id, company_id, name, int(download_limit), int(upload_limit), 
                  int(time_limit) if time_limit else None))
            conn.commit()
            conn.close()
            
            # Criar perfil no MikroTik
            success, message = create_mikrotik_profile(
                company_id, name, int(download_limit), int(upload_limit), 
                int(time_limit) if time_limit else None
            )
            
            if success:
                flash(f'Perfil criado no sistema e no MikroTik: {message}', 'success')
            else:
                flash(f'Perfil criado no sistema, mas erro no MikroTik: {message}', 'warning')
        
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
                conn.close()
                
                # Sincronizar com MikroTik se usuário estiver ativo
                if user_active:
                    sync_hotspot_users_to_mikrotik(company_id)
                
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
            conn.close()
            
            # Sincronizar com MikroTik
            sync_hotspot_users_to_mikrotik(company_id)
            
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
    # Obter filtros da URL
    company_filter = request.args.get('company', '')
    month_filter = request.args.get('month', '')
    
    conn = get_db()
    
    # Construir query base
    base_query = '''
        SELECT hu.username, hu.full_name, c.name as company_name,
               uc.total_mb, uc.used_mb, uc.remaining_mb, uc.last_reset, uc.updated_at,
               c.id as company_id, strftime('%Y-%m', uc.created_at) as month_year
        FROM user_credits uc
        JOIN hotspot_users hu ON uc.hotspot_user_id = hu.id
        JOIN companies c ON hu.company_id = c.id
        WHERE hu.active = 1
    '''
    
    params = []
    
    # Aplicar filtro de empresa
    if company_filter:
        base_query += ' AND c.id = ?'
        params.append(company_filter)
    
    # Aplicar filtro de mês
    if month_filter:
        base_query += ' AND strftime("%Y-%m", uc.created_at) = ?'
        params.append(month_filter)
    
    base_query += ' ORDER BY uc.updated_at DESC'
    
    # Buscar créditos filtrados
    credits_list = conn.execute(base_query, params).fetchall()
    
    # Calcular estatísticas baseadas nos filtros
    stats_query = '''
        SELECT 
            SUM(uc.total_mb) as total_credits_mb,
            SUM(uc.used_mb) as used_credits_mb,
            SUM(uc.remaining_mb) as remaining_credits_mb,
            COUNT(DISTINCT hu.id) as active_users
        FROM user_credits uc
        JOIN hotspot_users hu ON uc.hotspot_user_id = hu.id
        JOIN companies c ON hu.company_id = hu.company_id
        WHERE hu.active = 1
    '''
    
    stats_params = []
    if company_filter:
        stats_query += ' AND c.id = ?'
        stats_params.append(company_filter)
    
    if month_filter:
        stats_query += ' AND strftime("%Y-%m", uc.created_at) = ?'
        stats_params.append(month_filter)
    
    stats_result = conn.execute(stats_query, stats_params).fetchone()
    
    stats = {
        'total_credits_mb': stats_result['total_credits_mb'] or 0,
        'used_credits_mb': stats_result['used_credits_mb'] or 0,
        'remaining_credits_mb': stats_result['remaining_credits_mb'] or 0,
        'active_users': stats_result['active_users'] or 0
    }
    
    # Buscar empresas para o filtro
    companies_list = conn.execute('SELECT * FROM companies WHERE active = 1 ORDER BY name').fetchall()
    
    # Buscar meses disponíveis para o filtro
    months_list = conn.execute('''
        SELECT DISTINCT strftime('%Y-%m', uc.created_at) as month_year
        FROM user_credits uc
        JOIN hotspot_users hu ON uc.hotspot_user_id = hu.id
        WHERE hu.active = 1 AND uc.created_at IS NOT NULL
        ORDER BY month_year DESC
    ''').fetchall()
    
    conn.close()
    
    return render_template('credits.html', 
                         user={'name': session.get('name')}, 
                         stats=stats,
                         credits_list=credits_list,
                         companies_list=companies_list,
                         months_list=months_list,
                         selected_company=company_filter,
                         selected_month=month_filter)

@app.route('/reports')
@require_auth
def reports():
    """Página de relatórios"""
    # Obter filtros da URL
    period = request.args.get('period', '7')
    company_filter = request.args.get('company', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    conn = get_db()
    
    # Calcular período baseado na seleção
    if period == 'custom' and start_date and end_date:
        date_filter = f"DATE(uc.created_at) BETWEEN '{start_date}' AND '{end_date}'"
    elif period == '7':
        date_filter = "DATE(uc.created_at) >= DATE('now', '-7 days')"
    elif period == '30':
        date_filter = "DATE(uc.created_at) >= DATE('now', '-30 days')"
    elif period == '90':
        date_filter = "DATE(uc.created_at) >= DATE('now', '-90 days')"
    else:
        date_filter = "1=1"  # Sem filtro de data
    
    # Query base para estatísticas
    stats_query = f'''
        SELECT 
            COUNT(DISTINCT hu.id) as total_users,
            COUNT(DISTINCT CASE WHEN hu.active = 1 THEN hu.id END) as active_users,
            COUNT(DISTINCT c.id) as total_companies,
            SUM(uc.total_mb) as total_data_mb,
            SUM(uc.used_mb) as used_data_mb,
            SUM(uc.remaining_mb) as remaining_data_mb
        FROM user_credits uc
        JOIN hotspot_users hu ON uc.hotspot_user_id = hu.id
        JOIN companies c ON hu.company_id = c.id
        WHERE {date_filter}
    '''
    
    params = []
    if company_filter:
        stats_query += ' AND c.id = ?'
        params.append(company_filter)
    
    stats_result = conn.execute(stats_query, params).fetchone()
    
    # Dados para gráfico de uso por empresa
    usage_by_company_query = f'''
        SELECT c.name as company_name, 
               SUM(uc.used_mb) as used_mb,
               COUNT(hu.id) as user_count
        FROM user_credits uc
        JOIN hotspot_users hu ON uc.hotspot_user_id = hu.id
        JOIN companies c ON hu.company_id = c.id
        WHERE {date_filter}
    '''
    
    usage_params = []
    if company_filter:
        usage_by_company_query += ' AND c.id = ?'
        usage_params.append(company_filter)
    
    usage_by_company_query += ' GROUP BY c.id, c.name ORDER BY used_mb DESC'
    usage_by_company = conn.execute(usage_by_company_query, usage_params).fetchall()
    
    # Dados para gráfico de usuários por turma
    users_by_turma_query = f'''
        SELECT hu.turma, 
               COUNT(hu.id) as user_count,
               COUNT(CASE WHEN hu.active = 1 THEN 1 END) as active_count
        FROM hotspot_users hu
        JOIN companies c ON hu.company_id = c.id
        JOIN user_credits uc ON hu.id = uc.hotspot_user_id
        WHERE {date_filter}
    '''
    
    turma_params = []
    if company_filter:
        users_by_turma_query += ' AND c.id = ?'
        turma_params.append(company_filter)
    
    users_by_turma_query += ' GROUP BY hu.turma ORDER BY hu.turma'
    users_by_turma = conn.execute(users_by_turma_query, turma_params).fetchall()
    
    # Dados para gráfico de créditos ao longo do tempo
    credits_timeline_query = f'''
        SELECT DATE(uc.created_at) as date,
               SUM(uc.total_mb) as total_mb,
               SUM(uc.used_mb) as used_mb
        FROM user_credits uc
        JOIN hotspot_users hu ON uc.hotspot_user_id = hu.id
        JOIN companies c ON hu.company_id = c.id
        WHERE {date_filter}
    '''
    
    timeline_params = []
    if company_filter:
        credits_timeline_query += ' AND c.id = ?'
        timeline_params.append(company_filter)
    
    credits_timeline_query += ' GROUP BY DATE(uc.created_at) ORDER BY date DESC LIMIT 30'
    credits_timeline = conn.execute(credits_timeline_query, timeline_params).fetchall()
    
    # Buscar empresas para o filtro
    companies_list = conn.execute('SELECT * FROM companies WHERE active = 1 ORDER BY name').fetchall()
    
    conn.close()
    
    # Preparar dados para os gráficos
    chart_data = {
        'usage_by_company': {
            'labels': [row['company_name'] for row in usage_by_company],
            'data': [row['used_mb'] for row in usage_by_company]
        },
        'users_by_turma': {
            'labels': [f"Turma {row['turma']}" for row in users_by_turma],
            'data': [row['user_count'] for row in users_by_turma],
            'active_data': [row['active_count'] for row in users_by_turma]
        },
        'credits_timeline': {
            'labels': [row['date'] for row in reversed(credits_timeline)],
            'total_data': [row['total_mb'] for row in reversed(credits_timeline)],
            'used_data': [row['used_mb'] for row in reversed(credits_timeline)]
        }
    }
    
    return render_template('reports.html', 
                         user={'name': session.get('name')},
                         stats=stats_result,
                         chart_data=chart_data,
                         companies_list=companies_list,
                         selected_period=period,
                         selected_company=company_filter,
                         selected_start_date=start_date,
                         selected_end_date=end_date)

@app.route('/settings', methods=['GET', 'POST'])
@require_auth
def settings():
    """Página de configurações"""
    if request.method == 'POST':
        conn = get_db()
        
        # Verificar se é upload de logo
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Gerar nome único para o arquivo
                unique_filename = f"logo_{uuid.uuid4().hex[:8]}.png"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                
                try:
                    file.save(file_path)
                    
                    # Redimensionar imagem
                    if resize_image(file_path):
                        # Atualizar configuração do logo
                        conn.execute('''
                            UPDATE system_settings 
                            SET value = ? 
                            WHERE key = 'system_logo'
                        ''', (unique_filename,))
                        flash('Logo atualizado com sucesso!', 'success')
                    else:
                        os.remove(file_path)
                        flash('Erro ao processar imagem', 'error')
                except Exception as e:
                    flash(f'Erro ao salvar logo: {str(e)}', 'error')
        
        # Atualizar outras configurações
        settings_to_update = [
            ('default_credit_mb', request.form.get('default_credit_mb')),
            ('credit_reset_time', request.form.get('credit_reset_time')),
            ('enable_cumulative', '1' if request.form.get('enable_cumulative') else '0'),
            ('system_timezone', request.form.get('system_timezone')),
            ('system_name', request.form.get('system_name')),
            ('auto_collect_usage', '1' if request.form.get('auto_collect_usage') else '0')
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

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Servir arquivos de upload"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/backup/download')
@require_auth
def download_backup():
    """Download do backup do banco de dados"""
    backup_path, backup_filename = create_database_backup()
    
    if backup_path:
        try:
            return send_from_directory(
                os.path.dirname(backup_path), 
                os.path.basename(backup_path),
                as_attachment=True,
                download_name=backup_filename
            )
        except Exception as e:
            flash(f'Erro ao gerar backup: {str(e)}', 'error')
            return redirect(url_for('settings'))
    else:
        flash(f'Erro ao criar backup: {backup_filename}', 'error')
        return redirect(url_for('settings'))

@app.route('/backup/restore', methods=['POST'])
@require_auth
def restore_backup():
    """Restaurar backup do banco de dados"""
    if 'backup_file' not in request.files:
        flash('Nenhum arquivo selecionado', 'error')
        return redirect(url_for('settings'))
    
    file = request.files['backup_file']
    if file.filename == '':
        flash('Nenhum arquivo selecionado', 'error')
        return redirect(url_for('settings'))
    
    if file and file.filename.endswith('.db'):
        try:
            import tempfile
            
            # Salvar arquivo temporariamente
            temp_path = os.path.join(tempfile.gettempdir(), secure_filename(file.filename))
            file.save(temp_path)
            
            # Restaurar backup
            success, message = restore_database_backup(temp_path)
            
            # Limpar arquivo temporário
            os.remove(temp_path)
            
            if success:
                flash(message, 'success')
                # Reinicializar banco após restauração
                init_db()
            else:
                flash(message, 'error')
                
        except Exception as e:
            flash(f'Erro ao processar arquivo de backup: {str(e)}', 'error')
    else:
        flash('Arquivo deve ter extensão .db', 'error')
    
    return redirect(url_for('settings'))

@app.route('/consulta')
def consulta_publica():
    """Página pública para consulta de consumo"""
    return render_template('consulta_publica.html')

@app.route('/consulta/usuario', methods=['POST'])
def consulta_usuario():
    """Consulta dados de consumo de um usuário específico"""
    username = request.form.get('username', '').strip()
    
    if not username:
        flash('Digite um nome de usuário', 'error')
        return redirect(url_for('consulta_publica'))
    
    conn = get_db()
    
    # Buscar usuário e seus dados de crédito
    user_data = conn.execute('''
        SELECT hu.username, hu.full_name, c.name as company_name,
               uc.total_mb, uc.used_mb, uc.remaining_mb, uc.last_reset, uc.updated_at
        FROM hotspot_users hu
        JOIN companies c ON hu.company_id = c.id
        LEFT JOIN user_credits uc ON hu.id = uc.hotspot_user_id
        WHERE hu.username = ? AND hu.active = 1
        LIMIT 1
    ''', (username,)).fetchone()
    
    if not user_data:
        flash('Usuário não encontrado ou inativo', 'error')
        return redirect(url_for('consulta_publica'))
    
    # Buscar histórico dos últimos 30 dias (simulado baseado na última atualização)
    historico = conn.execute('''
        SELECT DATE(ml.created_at) as data, 
               'Coleta de dados' as acao,
               ml.created_at
        FROM mikrotik_connection_logs ml
        JOIN companies c ON ml.company_id = c.id
        JOIN hotspot_users hu ON hu.company_id = c.id
        WHERE hu.username = ? AND ml.action = 'collect_usage' AND ml.status = 'success'
        AND DATE(ml.created_at) >= DATE('now', '-30 days')
        GROUP BY DATE(ml.created_at)
        ORDER BY ml.created_at DESC
        LIMIT 30
    ''', (username,)).fetchall()
    
    conn.close()
    
    return render_template('consulta_resultado.html', user_data=user_data, historico=historico)

# API Routes
@app.route('/api/health')
def api_health():
    """Health check da API"""
    return jsonify({
        'status': 'ok',
        'message': 'MikroTik Manager API funcionando',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/collect-usage', methods=['POST'])
@require_auth
def api_collect_usage():
    """API para coletar dados de uso manualmente"""
    try:
        collect_all_companies_usage()
        return jsonify({'status': 'success', 'message': 'Coleta de dados de uso executada com sucesso'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/update-credits', methods=['POST'])
@require_auth
def api_update_credits():
    """API para atualizar créditos cumulativos"""
    try:
        update_credits_cumulative()
        return jsonify({'status': 'success', 'message': 'Créditos atualizados'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/sync-credits-to-mikrotik', methods=['POST'])
@require_auth
def api_sync_credits_to_mikrotik():
    """API para sincronizar créditos com MikroTik manualmente"""
    try:
        synced, errors = sync_credits_to_mikrotik_total_bytes()
        return jsonify({
            'status': 'success', 
            'message': f'Sincronização concluída: {synced} sucessos, {errors} erros',
            'synced': synced,
            'errors': errors
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    init_db()
    
    # Iniciar coleta automática de uso
    schedule_usage_collection()
    
    # Iniciar agendamento diário de sincronização de créditos
    schedule_daily_credit_sync()
    
    print("🚀 Iniciando MikroTik Manager Flask...")
    print("📧 Login: admin@demo.com")
    print("🔑 Senha: admin123")
    print("🌐 URL: http://localhost:5000")
    print("💾 Banco: mikrotik_manager.db")
    print("📊 Coleta automática de uso: ATIVADA (a cada 1 minuto)")
    print("💰 Acúmulo diário de créditos: ATIVADO (23:58 Brasil)")
    print("🇧🇷 Sincronização diária de créditos: ATIVADA (00:00 Brasil)")
    app.run(host='0.0.0.0', port=5000, debug=True)
