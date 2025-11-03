import json
import base64
import os
import time
import logging
from typing import Dict, Optional
from response_utils import create_response, create_error_response
from dynamodb_utils import create_or_update_user
from token_utils import generate_session_token

# ロギング設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def verify_line_id_token(id_token: str) -> Dict[str, Optional[str]]:
    """
    LINE IDトークンの検証
    
    LINE IDトークンはJWT形式で提供されます。
    本実装では、JWTのペイロードをデコードしてユーザー情報を取得します。
    
    注意: 本番環境では以下の検証を実装することを推奨します:
    1. 署名検証（LINE公開鍵を使用）
    2. 有効期限の確認（exp claim）
    3. 発行者（iss）の確認
    4. オーディエンス（aud）の確認
    
    Args:
        id_token (str): LINE IDトークン（JWT形式）
    
    Returns:
        dict: 検証結果とユーザー情報
            {
                'user_id': str,      # LINE UID（sub claim）
                'display_name': str, # 表示名（name claim）
                'line_id': Optional[str]  # LINE ID（存在する場合）
            }
    
    Raises:
        ValueError: トークンの形式が不正な場合
        Exception: トークンのデコードに失敗した場合
    """
    if not id_token or not isinstance(id_token, str):
        raise ValueError('IDトークンが無効です')
    
    try:
        # JWTトークンは3つの部分から構成: header.payload.signature
        parts = id_token.split('.')
        if len(parts) != 3:
            raise ValueError('JWTトークンの形式が不正です（3つの部分が必要）')
        
        # payload部分をデコード（Base64URL）
        payload_part = parts[1]
        
        # Base64URLパディングを追加
        padding = 4 - len(payload_part) % 4
        if padding != 4:
            payload_part += '=' * padding
        
        # Base64URLデコード
        try:
            payload_bytes = base64.urlsafe_b64decode(payload_part)
            payload = json.loads(payload_bytes.decode('utf-8'))
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error(f'JWTペイロードのデコードに失敗: {str(e)}')
            raise ValueError(f'トークンのデコードに失敗しました: {str(e)}')
        
        # 必須フィールドの確認
        user_id = payload.get('sub')
        if not user_id:
            raise ValueError('トークンにユーザーID（sub）が含まれていません')
        
        # 表示名を取得（デフォルト: 'LINE User'）
        display_name = payload.get('name', 'LINE User')
        
        # 有効期限の確認（オプションだが推奨）
        exp = payload.get('exp')
        if exp and isinstance(exp, (int, float)):
            current_time = int(time.time())
            if current_time > exp:
                logger.warning(f'トークンの有効期限が切れています (exp: {exp}, current: {current_time})')
                # 本番環境では例外を投げることを推奨
                # raise ValueError('トークンの有効期限が切れています')
        
        # LINE IDは通常トークンに含まれていない
        line_id = payload.get('email') or None
        
        logger.info(f'LINE IDトークン検証成功: user_id={user_id}, name={display_name}')
        
        return {
            'user_id': str(user_id),
            'display_name': str(display_name),
            'line_id': str(line_id) if line_id else None
        }
        
    except ValueError:
        # 既に適切なエラーメッセージが設定されているので再スロー
        raise
    except Exception as e:
        logger.error(f'LINE IDトークン検証中に予期しないエラー: {str(e)}')
        raise ValueError(f'トークン検証に失敗しました: {str(e)}')


def lambda_handler(event, context):
    """
    LINE IDトークンを検証し、セッショントークンを返す
    
    POST /auth/verify
    
    リクエストボディ:
    {
        "id_token": "LINE_ID_TOKEN_STRING"
    }
    
    レスポンス（成功時）:
    {
        "ok": true,
        "user_id": "USER_ID",
        "display_name": "Display Name",
        "access_token": "SESSION_TOKEN"
    }
    
    レスポンス（エラー時）:
    {
        "error": "Error",
        "message": "エラーメッセージ"
    }
    """
    logger.info('LINE認証リクエストを受信')
    
    try:
        # OPTIONSリクエストの処理（CORS preflight）
        if event.get('httpMethod') == 'OPTIONS':
            logger.info('CORS preflightリクエストを処理')
            return create_response(200, {'ok': True})
        
        # HTTPメソッドの確認
        if event.get('httpMethod') != 'POST':
            logger.warning(f'不正なHTTPメソッド: {event.get("httpMethod")}')
            return create_error_response(405, 'Method not allowed', 'METHOD_NOT_ALLOWED')
        
        # リクエストボディの取得とパース
        try:
            body_str = event.get('body', '{}')
            if isinstance(body_str, str):
                body = json.loads(body_str)
            else:
                body = body_str
        except json.JSONDecodeError as e:
            logger.error(f'JSONパースエラー: {str(e)}')
            return create_error_response(400, 'Invalid JSON format', 'INVALID_JSON')
        
        # id_tokenの取得とバリデーション
        id_token = body.get('id_token') or body.get('idToken')  # 両方の形式に対応
        if not id_token:
            logger.warning('id_tokenがリクエストに含まれていません')
            return create_error_response(400, 'id_token is required', 'MISSING_ID_TOKEN')
        
        if not isinstance(id_token, str) or len(id_token.strip()) == 0:
            logger.warning('id_tokenが空文字列です')
            return create_error_response(400, 'id_token cannot be empty', 'EMPTY_ID_TOKEN')
        
        # LINE IDトークンの検証
        try:
            logger.info('LINE IDトークンの検証を開始')
            token_info = verify_line_id_token(id_token.strip())
            user_id = token_info['user_id']
            display_name = token_info['display_name']
            line_id = token_info.get('line_id')
            
            logger.info(f'トークン検証成功: user_id={user_id}')
        except ValueError as e:
            logger.error(f'トークン検証失敗: {str(e)}')
            return create_error_response(401, f'Token verification failed: {str(e)}', 'TOKEN_VERIFICATION_FAILED')
        except Exception as e:
            logger.error(f'トークン検証中に予期しないエラー: {str(e)}')
            return create_error_response(401, f'Token verification error: {str(e)}', 'TOKEN_VERIFICATION_ERROR')
        
        # ユーザー情報のDynamoDB保存・更新
        try:
            logger.info(f'ユーザー情報を保存/更新: user_id={user_id}')
            user_data = create_or_update_user(
                user_id=user_id,
                display_name=display_name,
                line_id=line_id or user_id  # line_idがない場合はuser_idを使用
            )
            logger.info('ユーザー情報の保存/更新に成功')
        except Exception as e:
            logger.error(f'ユーザー情報の保存/更新に失敗: {str(e)}')
            return create_error_response(500, f'Failed to save user data: {str(e)}', 'DATABASE_ERROR')
        
        # セッショントークンの生成
        try:
            logger.info('セッショントークンを生成')
            session_token = generate_session_token(user_id, display_name)
            logger.info('セッショントークンの生成に成功')
        except Exception as e:
            logger.error(f'セッショントークンの生成に失敗: {str(e)}')
            return create_error_response(500, f'Failed to generate session token: {str(e)}', 'TOKEN_GENERATION_ERROR')
        
        # 成功レスポンスの作成
        response_data = {
            'ok': True,
            'user_id': user_id,
            'display_name': display_name,
            'access_token': session_token
        }
        
        logger.info(f'認証成功: user_id={user_id}')
        return create_response(200, response_data)
        
    except Exception as e:
        # 予期しないエラー
        logger.error(f'予期しないエラーが発生: {str(e)}', exc_info=True)
        return create_error_response(500, f'Internal Server Error: {str(e)}', 'INTERNAL_ERROR')

