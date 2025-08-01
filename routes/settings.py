from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.auth import require_admin
from database import get_db

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings', methods=['GET', 'POST'])
@require_admin
def settings():
    """Página de configurações"""
    if request.method == 'POST':
        conn = get_db()
        
        # Atualizar configurações
        settings_to_update = [
            ('default_credit_mb', request.form.get('default_credit_mb')),
            ('credit_reset_time', request.form.get('credit_reset_time')),
            ('enable_cumulative', '1' if request.form.get('enable_cumulative') else '0'),
            ('system_timezone', request.form.get('system_timezone'))
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
        return redirect(url_for('settings.settings'))
    
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
