import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mikrotik-manager-super-secret-key-2024'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    DATABASE_PATH = 'mikrotik_manager.db'
    
    # Configurações de crédito
    DEFAULT_CREDIT_MB = 1024  # 1GB padrão
    ENABLE_CUMULATIVE = True
    CREDIT_RESET_TIME = '00:00'
    SYSTEM_TIMEZONE = 'America/Sao_Paulo'
