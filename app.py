from flask import Flask
from config import Config
from database import init_db

# Importar blueprints
from routes.auth import auth_bp
from routes.main import main_bp
from routes.users import users_bp
from routes.companies import companies_bp
from routes.profiles import profiles_bp
from routes.hotspot_users import hotspot_users_bp
from routes.credits import credits_bp
from routes.settings import settings_bp
from routes.api import api_bp

def create_app():
    """Factory para criar a aplicação Flask"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(companies_bp)
    app.register_blueprint(profiles_bp)
    app.register_blueprint(hotspot_users_bp)
    app.register_blueprint(credits_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(api_bp)
    
    return app

if __name__ == '__main__':
    # Inicializar banco de dados
    init_db()
    
    # Criar aplicação
    app = create_app()
    
    print("🚀 Iniciando MikroTik Manager Flask...")
    print("📧 Login Admin: admin@demo.com")
    print("🔑 Senha Admin: admin123")
    print("🌐 URL: http://localhost:5000")
    print("💾 Banco: mikrotik_manager.db")
    print("👤 Usuários hotspot podem fazer login com email/senha")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
