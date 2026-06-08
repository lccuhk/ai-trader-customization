from flask import Blueprint, request, jsonify
from middleware.auth import require_auth
from middleware.rate_limit import rate_limit
from services import security_service

security_bp = Blueprint('security', __name__, url_prefix='/api/security')


@security_bp.route('/2fa/setup', methods=['POST'])
@require_auth
@rate_limit('strict')
def setup_2fa():
    user_id = request.current_user_id
    data = request.get_json() or {}
    method = data.get('method', 'totp')
    result = security_service.setup_2fa(user_id, method)
    return jsonify(result), result.get('code', 200)


@security_bp.route('/2fa/verify', methods=['POST'])
@require_auth
@rate_limit('strict')
def verify_2fa():
    user_id = request.current_user_id
    data = request.get_json() or {}
    code = data.get('code', '')
    
    if not code:
        return jsonify({'success': False, 'message': '请输入验证码', 'code': 400}), 400
    
    result = security_service.verify_2fa(user_id, code)
    return jsonify(result), result.get('code', 200)


@security_bp.route('/2fa/disable', methods=['POST'])
@require_auth
@rate_limit('strict')
def disable_2fa():
    user_id = request.current_user_id
    data = request.get_json() or {}
    code = data.get('code', '')
    
    if not code:
        return jsonify({'success': False, 'message': '请输入验证码', 'code': 400}), 400
    
    result = security_service.disable_2fa(user_id, code)
    return jsonify(result), result.get('code', 200)


@security_bp.route('/2fa/status', methods=['GET'])
@require_auth
def get_2fa_status():
    user_id = request.current_user_id
    result = security_service.get_2fa_status(user_id)
    return jsonify(result), result.get('code', 200)


@security_bp.route('/oauth/<provider>', methods=['POST'])
@rate_limit('auth')
def oauth_login(provider):
    data = request.get_json() or {}
    code = data.get('code')
    redirect_uri = data.get('redirect_uri', '')
    
    if not code:
        return jsonify({'success': False, 'message': '缺少授权码', 'code': 400}), 400
    
    result = security_service.oauth_login(provider, code, redirect_uri)
    return jsonify(result), result.get('code', 200)


@security_bp.route('/audit-logs', methods=['GET'])
@require_auth
def get_audit_logs():
    user_id = request.current_user_id
    params = request.args.to_dict()
    result = security_service.get_audit_logs(user_id, params)
    return jsonify(result), result.get('code', 200)


@security_bp.route('/settings', methods=['GET'])
@require_auth
def get_security_settings():
    user_id = request.current_user_id
    result = security_service.get_security_settings(user_id)
    return jsonify(result), result.get('code', 200)


@security_bp.route('/password/validate', methods=['POST'])
def validate_password():
    data = request.get_json() or {}
    password = data.get('password', '')
    
    if not password:
        return jsonify({'success': False, 'message': '请输入密码', 'code': 400}), 400
    
    is_valid, errors = security_service.validate_password_strength(password)
    
    return jsonify({
        'success': True,
        'code': 200,
        'data': {
            'valid': is_valid,
            'errors': errors
        }
    })
