from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone, timedelta
import secrets
import string
import re
import hashlib
import hmac
import base64
import os

from sqlalchemy import desc
from database import get_db
from models import User, TwoFactorAuth, OAuthAccount, AuditLog, PasswordHistory
from middleware.error_handler import success_response, error_response

try:
    import pyotp
    import qrcode
    import io
    TOTP_AVAILABLE = True
except ImportError:
    TOTP_AVAILABLE = False


def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
    errors = []
    
    if len(password) < 8:
        errors.append('密码长度至少8位')
    
    if not re.search(r'[A-Z]', password):
        errors.append('密码需要包含至少一个大写字母')
    
    if not re.search(r'[a-z]', password):
        errors.append('密码需要包含至少一个小写字母')
    
    if not re.search(r'[0-9]', password):
        errors.append('密码需要包含至少一个数字')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append('密码需要包含至少一个特殊字符')
    
    common_passwords = ['password', '123456', 'qwerty', 'abc123', 'password1']
    if password.lower() in common_passwords:
        errors.append('密码过于常见，请使用更复杂的密码')
    
    return len(errors) == 0, errors


def check_password_history(user_id: int, new_password: str, db) -> bool:
    from werkzeug.security import check_password_hash
    
    recent_passwords = db.query(PasswordHistory).filter(
        PasswordHistory.user_id == user_id
    ).order_by(desc(PasswordHistory.created_at)).limit(5).all()
    
    for ph in recent_passwords:
        if check_password_hash(ph.password_hash, new_password):
            return False
    
    return True


def save_password_history(user_id: int, password_hash: str, db) -> None:
    history = PasswordHistory(
        user_id=user_id,
        password_hash=password_hash
    )
    db.add(history)


def setup_2fa(user_id: int, method: str = 'totp') -> Dict[str, Any]:
    if not TOTP_AVAILABLE:
        return error_response('2FA功能不可用，请安装pyotp和qrcode库', 500)

    if method not in ['totp', 'sms', 'email']:
        return error_response('不支持的2FA方法', 400)

    db = next(get_db())
    try:
        existing = db.query(TwoFactorAuth).filter(
            TwoFactorAuth.user_id == user_id
        ).first()

        if existing and existing.is_enabled:
            return error_response('2FA已启用，请先禁用再重新设置', 400)

        secret = pyotp.random_base32()
        backup_codes = _generate_backup_codes()

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return error_response('用户不存在', 404)

        if existing:
            existing.secret = secret
            existing.method = method
            existing.backup_codes = backup_codes
            existing.is_enabled = False
        else:
            tfa = TwoFactorAuth(
                user_id=user_id,
                secret=secret,
                method=method,
                backup_codes=backup_codes,
                is_enabled=False
            )
            db.add(tfa)

        db.commit()

        issuer = 'TradingAgent'
        account_name = user.email or user.username
        provisioning_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=account_name,
            issuer_name=issuer
        )

        qr_code = _generate_qr_code(provisioning_uri)

        return success_response({
            'secret': secret,
            'provisioning_uri': provisioning_uri,
            'qr_code': qr_code,
            'backup_codes': backup_codes,
            'method': method
        })

    except Exception as e:
        db.rollback()
        return error_response(f'设置2FA失败: {str(e)}', 500)
    finally:
        db.close()


def _generate_backup_codes(count: int = 10) -> List[str]:
    codes = []
    for _ in range(count):
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        codes.append(code)
    return codes


def _generate_qr_code(data: str) -> str:
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        print(f"[Security] Error generating QR code: {e}")
        return ''


def verify_2fa(user_id: int, code: str) -> Dict[str, Any]:
    if not TOTP_AVAILABLE:
        return error_response('2FA功能不可用', 500)

    db = next(get_db())
    try:
        tfa = db.query(TwoFactorAuth).filter(
            TwoFactorAuth.user_id == user_id
        ).first()

        if not tfa:
            return error_response('2FA未设置', 400)

        totp = pyotp.TOTP(tfa.secret)
        
        if totp.verify(code):
            if not tfa.is_enabled:
                tfa.is_enabled = True
                db.commit()
            
            return success_response({'verified': True, 'method': tfa.method})

        if code in tfa.backup_codes:
            tfa.backup_codes = [c for c in tfa.backup_codes if c != code]
            db.commit()
            return success_response({'verified': True, 'method': 'backup_code'})

        return success_response({'verified': False, 'method': None})

    except Exception as e:
        db.rollback()
        return error_response(f'验证2FA失败: {str(e)}', 500)
    finally:
        db.close()


def disable_2fa(user_id: int, code: str) -> Dict[str, Any]:
    if not TOTP_AVAILABLE:
        return error_response('2FA功能不可用', 500)

    db = next(get_db())
    try:
        tfa = db.query(TwoFactorAuth).filter(
            TwoFactorAuth.user_id == user_id
        ).first()

        if not tfa or not tfa.is_enabled:
            return error_response('2FA未启用', 400)

        totp = pyotp.TOTP(tfa.secret)
        if not totp.verify(code) and code not in tfa.backup_codes:
            return error_response('验证码错误', 400)

        db.delete(tfa)
        db.commit()

        return success_response({'message': '2FA已禁用'})

    except Exception as e:
        db.rollback()
        return error_response(f'禁用2FA失败: {str(e)}', 500)
    finally:
        db.close()


def get_2fa_status(user_id: int) -> Dict[str, Any]:
    db = next(get_db())
    try:
        tfa = db.query(TwoFactorAuth).filter(
            TwoFactorAuth.user_id == user_id
        ).first()

        return success_response({
            'enabled': tfa.is_enabled if tfa else False,
            'method': tfa.method if tfa else None
        })

    except Exception as e:
        return error_response(f'获取2FA状态失败: {str(e)}', 500)
    finally:
        db.close()


def oauth_login(provider: str, code: str, redirect_uri: str) -> Dict[str, Any]:
    if provider not in ['google', 'github', 'telegram']:
        return error_response('不支持的OAuth提供商', 400)

    try:
        user_info = _exchange_oauth_code(provider, code, redirect_uri)
        
        db = next(get_db())
        try:
            oauth_account = db.query(OAuthAccount).filter(
                OAuthAccount.provider == provider,
                OAuthAccount.provider_user_id == user_info['id']
            ).first()

            if oauth_account:
                user = db.query(User).filter(User.id == oauth_account.user_id).first()
                oauth_account.access_token = user_info.get('access_token')
                oauth_account.refresh_token = user_info.get('refresh_token')
                db.commit()
            else:
                user = User(
                    username=user_info.get('username', f"{provider}_{user_info['id']}"),
                    email=user_info.get('email'),
                    display_name=user_info.get('name', user_info.get('username')),
                    avatar_url=user_info.get('avatar_url'),
                    is_verified=True
                )
                db.add(user)
                db.flush()

                oauth_account = OAuthAccount(
                    user_id=user.id,
                    provider=provider,
                    provider_user_id=user_info['id'],
                    access_token=user_info.get('access_token'),
                    refresh_token=user_info.get('refresh_token')
                )
                db.add(oauth_account)
                db.commit()
                db.refresh(user)

            from services.auth_service import _generate_tokens
            access_token, refresh_token = _generate_tokens(user.id)

            return success_response({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'display_name': user.display_name,
                    'avatar_url': user.avatar_url
                }
            })

        except Exception as e:
            db.rollback()
            return error_response(f'OAuth登录失败: {str(e)}', 500)
        finally:
            db.close()

    except Exception as e:
        return error_response(f'OAuth认证失败: {str(e)}', 500)


def _exchange_oauth_code(provider: str, code: str, redirect_uri: str) -> Dict[str, Any]:
    if provider == 'google':
        return {
            'id': f'google_{secrets.token_hex(8)}',
            'email': f'user_{secrets.token_hex(4)}@gmail.com',
            'name': 'Google User',
            'avatar_url': None,
            'access_token': secrets.token_hex(32),
            'refresh_token': secrets.token_hex(32)
        }
    elif provider == 'github':
        return {
            'id': f'github_{secrets.token_hex(8)}',
            'username': f'github_user_{secrets.token_hex(4)}',
            'name': 'GitHub User',
            'avatar_url': None,
            'access_token': secrets.token_hex(32),
            'refresh_token': secrets.token_hex(32)
        }
    elif provider == 'telegram':
        return {
            'id': f'telegram_{secrets.token_hex(8)}',
            'username': f'tg_user_{secrets.token_hex(4)}',
            'name': 'Telegram User',
            'avatar_url': None,
            'access_token': secrets.token_hex(32)
        }
    
    raise ValueError(f"Unsupported provider: {provider}")


def create_audit_log(user_id: Optional[int], action: str, resource_type: Optional[str] = None,
                     resource_id: Optional[int] = None, old_values: Optional[Dict] = None,
                     new_values: Optional[Dict] = None, ip_address: Optional[str] = None,
                     user_agent: Optional[str] = None) -> None:
    db = next(get_db())
    try:
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(log)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[Security] Failed to create audit log: {e}")
    finally:
        db.close()


def get_audit_logs(user_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
    action = params.get('action')
    resource_type = params.get('resource_type')
    start_date = params.get('start_date')
    end_date = params.get('end_date')
    page = int(params.get('page', 1))
    per_page = int(params.get('per_page', 20))

    db = next(get_db())
    try:
        query = db.query(AuditLog).filter(AuditLog.user_id == user_id)

        if action:
            query = query.filter(AuditLog.action == action)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if start_date:
            query = query.filter(AuditLog.created_at >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(AuditLog.created_at <= datetime.fromisoformat(end_date))

        total = query.count()
        logs = query.order_by(desc(AuditLog.created_at)).offset((page - 1) * per_page).limit(per_page).all()

        return success_response({
            'items': [{
                'id': log.id,
                'action': log.action,
                'resource_type': log.resource_type,
                'resource_id': log.resource_id,
                'old_values': log.old_values,
                'new_values': log.new_values,
                'ip_address': log.ip_address,
                'created_at': log.created_at.isoformat() if log.created_at else None
            } for log in logs],
            'total': total,
            'page': page,
            'per_page': per_page
        })

    except Exception as e:
        return error_response(f'获取审计日志失败: {str(e)}', 500)
    finally:
        db.close()


def verify_request_signature(request_data: str, signature: str, secret: str, timestamp: str) -> bool:
    try:
        timestamp_int = int(timestamp)
        now = int(datetime.now(timezone.utc).timestamp())
        
        if abs(now - timestamp_int) > 300:
            return False

        message = f"{timestamp}:{request_data}"
        expected_signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected_signature, signature)
    except Exception as e:
        print(f"[Security] Signature verification failed: {e}")
        return False


def generate_csrf_token() -> str:
    return secrets.token_hex(32)


def verify_csrf_token(token: str, expected_token: str) -> bool:
    return hmac.compare_digest(token, expected_token)


def get_security_settings(user_id: int) -> Dict[str, Any]:
    db = next(get_db())
    try:
        tfa = db.query(TwoFactorAuth).filter(
            TwoFactorAuth.user_id == user_id
        ).first()

        oauth_accounts = db.query(OAuthAccount).filter(
            OAuthAccount.user_id == user_id
        ).all()

        return success_response({
            'two_factor': {
                'enabled': tfa.is_enabled if tfa else False,
                'method': tfa.method if tfa else None
            },
            'oauth_accounts': [{
                'id': oa.id,
                'provider': oa.provider,
                'created_at': oa.created_at.isoformat() if oa.created_at else None
            } for oa in oauth_accounts],
            'password_last_changed': None
        })

    except Exception as e:
        return error_response(f'获取安全设置失败: {str(e)}', 500)
    finally:
        db.close()
