from flask import Blueprint, jsonify
from datetime import datetime
from utils.auth import require_auth
from utils.helpers import update_credits_cumulative

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/health')
def api_health():
    """Health check da API"""
    return jsonify({
        'status': 'ok',
        'message': 'MikroTik Manager API funcionando',
        'timestamp': datetime.now().isoformat()
    })

@api_bp.route('/api/update-credits', methods=['POST'])
@require_auth
def api_update_credits():
    """API para atualizar créditos cumulativos"""
    try:
        update_credits_cumulative()
        return jsonify({'status': 'success', 'message': 'Créditos atualizados'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
