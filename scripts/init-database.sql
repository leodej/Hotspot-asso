-- Criação do banco de dados MikroTik Manager
-- Execute este script para inicializar o banco de dados

-- Tabela de usuários do sistema
CREATE TABLE IF NOT EXISTS system_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP
);

-- Tabela de empresas
CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    mikrotik_ip INET NOT NULL,
    mikrotik_port INTEGER DEFAULT 8728,
    mikrotik_user VARCHAR(255) NOT NULL,
    mikrotik_password VARCHAR(255) NOT NULL,
    default_download INTEGER DEFAULT 10,
    default_upload INTEGER DEFAULT 5,
    default_time INTEGER DEFAULT 60,
    active BOOLEAN DEFAULT true,
    connection_status VARCHAR(50) DEFAULT 'disconnected',
    last_connection_test TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de perfis hotspot
CREATE TABLE IF NOT EXISTS hotspot_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    download_limit INTEGER NOT NULL,
    upload_limit INTEGER NOT NULL,
    time_limit INTEGER,
    idle_timeout INTEGER DEFAULT 300,
    session_timeout INTEGER,
    keepalive_timeout INTEGER DEFAULT 120,
    active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, name)
);

-- Tabela de usuários hotspot
CREATE TABLE IF NOT EXISTS hotspot_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    profile_id UUID REFERENCES hotspot_profiles(id),
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    full_name VARCHAR(255),
    phone VARCHAR(50),
    mac_address MACADDR,
    ip_address INET,
    active BOOLEAN DEFAULT true,
    blocked BOOLEAN DEFAULT false,
    block_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    expires_at TIMESTAMP,
    UNIQUE(company_id, username)
);

-- Tabela de créditos
CREATE TABLE IF NOT EXISTS user_credits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hotspot_user_id UUID REFERENCES hotspot_users(id) ON DELETE CASCADE,
    credit_type VARCHAR(50) NOT NULL, -- 'data', 'time', 'unlimited', 'accumulative'
    initial_amount BIGINT NOT NULL,
    current_amount BIGINT NOT NULL,
    unit VARCHAR(20) NOT NULL, -- 'bytes', 'minutes', 'days'
    valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP,
    auto_reset BOOLEAN DEFAULT false,
    reset_period VARCHAR(20), -- 'daily', 'weekly', 'monthly'
    accumulative BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de sessões de usuário
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hotspot_user_id UUID REFERENCES hotspot_users(id) ON DELETE CASCADE,
    session_id VARCHAR(255),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    bytes_in BIGINT DEFAULT 0,
    bytes_out BIGINT DEFAULT 0,
    packets_in BIGINT DEFAULT 0,
    packets_out BIGINT DEFAULT 0,
    ip_address INET,
    mac_address MACADDR,
    nas_ip INET,
    terminate_cause VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de logs de auditoria
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES system_users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(255),
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de configurações do sistema
CREATE TABLE IF NOT EXISTS system_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(255) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    category VARCHAR(100),
    data_type VARCHAR(50) DEFAULT 'string',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de backups
CREATE TABLE IF NOT EXISTS system_backups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT,
    backup_type VARCHAR(50) NOT NULL, -- 'manual', 'automatic'
    status VARCHAR(50) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- Tabela de associação usuários-empresas (many-to-many)
CREATE TABLE IF NOT EXISTS user_company_associations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES system_users(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, company_id)
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_hotspot_users_company ON hotspot_users(company_id);
CREATE INDEX IF NOT EXISTS idx_hotspot_users_username ON hotspot_users(username);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user ON user_sessions(hotspot_user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_start_time ON user_sessions(start_time);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_user_credits_user ON user_credits(hotspot_user_id);

-- Inserir configurações padrão
INSERT INTO system_settings (key, value, description, category) VALUES
('system.timezone', 'America/Sao_Paulo', 'Timezone do sistema', 'general'),
('session.timeout', '3600', 'Timeout de sessão em segundos', 'security'),
('mikrotik.default_port', '8728', 'Porta padrão para conexão MikroTik', 'mikrotik'),
('mikrotik.connection_timeout', '10', 'Timeout de conexão em segundos', 'mikrotik'),
('monitoring.interval', '300', 'Intervalo de coleta de dados em segundos', 'monitoring'),
('backup.retention_days', '30', 'Dias de retenção de backups', 'backup'),
('email.smtp_host', '', 'Servidor SMTP', 'email'),
('email.smtp_port', '587', 'Porta SMTP', 'email'),
('email.smtp_user', '', 'Usuário SMTP', 'email'),
('email.smtp_password', '', 'Senha SMTP', 'email')
ON CONFLICT (key) DO NOTHING;

-- Inserir usuário administrador padrão
INSERT INTO system_users (email, password_hash, name, role) VALUES
('admin@mikrotik-manager.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.PJ/..G', 'Administrador', 'admin')
ON CONFLICT (email) DO NOTHING;

-- Função para atualizar timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para atualizar updated_at automaticamente
CREATE TRIGGER update_system_users_updated_at BEFORE UPDATE ON system_users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_hotspot_profiles_updated_at BEFORE UPDATE ON hotspot_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_hotspot_users_updated_at BEFORE UPDATE ON hotspot_users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_credits_updated_at BEFORE UPDATE ON user_credits FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_system_settings_updated_at BEFORE UPDATE ON system_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
