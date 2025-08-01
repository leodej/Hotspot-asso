from database import get_db

def get_setting(key, default=None):
    """Busca uma configuração do sistema"""
    conn = get_db()
    setting = conn.execute('SELECT value FROM system_settings WHERE key = ?', (key,)).fetchone()
    conn.close()
    return setting['value'] if setting else default

def format_bytes(bytes_value):
    """Converte bytes para formato legível"""
    if bytes_value >= 1024 * 1024 * 1024:  # GB
        return f"{bytes_value / (1024 * 1024 * 1024):.2f} GB"
    elif bytes_value >= 1024 * 1024:  # MB
        return f"{bytes_value / (1024 * 1024):.2f} MB"
    elif bytes_value >= 1024:  # KB
        return f"{bytes_value / 1024:.2f} KB"
    else:
        return f"{bytes_value} B"

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
