import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mikrotik-manager-super-secret-key-2024'
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or 'mikrotik_manager.db'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Configurações padrão do sistema
    DEFAULT_SETTINGS = {
        'default_credit_mb': '1024',
        'credit_reset_time': '00:00',
        'enable_cumulative': '1',
        'system_timezone': 'America/Sao_Paulo'
    }
