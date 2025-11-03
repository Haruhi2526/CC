import json
import base64
from response_utils import create_response, create_error_response
from dynamodb_utils import create_or_update_user
from token_utils import generate_session_token


def verify_line_id_token_mock(id_token: str) -> dict:
    """
    LINE IDトークンの検証（モック実装）
    
    注意: 本番環境では実際のLINE IDトークン検証を実装してください。
    LINE Messaging API SDKやJWT検証ライブラリを使用する必要があります。
    Mac環境でビルドしたライブラリをLinux環境で動作させる場合は、
    Dockerを使用してビルドすることを推奨します。
    
    Args:
        id_token (str): LINE IDトークン
    
    Returns:
        dict: 検証結果とユーザー情報
            {
                'user_id': str,  # LINE UID
                'display_name': str,  # 表示名
                'line_id': str  # LINE ID（存在する場合）
            }
    """
    # TODO: 実際のLINE IDトークン検証を実装
    # 現在はモック実装として、トークンから情報を取得できないため
    # 開発用のダミーデータを返す
    # 
    # 実装時の注意点:
    # 1. LINE Messaging API SDKの使用
    # 2. トークンの署名検証
    # 3. 有効期限の確認
    # 4. 環境変数からChannel Secretを取得
    
    # モック実装: JWTトークンからユーザー情報を取得（開発用）
    # 注意: 署名検証は行っていないため、本番環境では必ず検証を実装してください
    try:
        # JWTトークンは3つの部分から構成: header.payload.signature
        parts = id_token.split('.')
        if len(parts) != 3:
            # JWT形式でない場合はフォールバック
            return {
                'user_id': id_token[:32] if len(id_token) > 32 else id_token,
                'display_name': 'LINE User',
                'line_id': None
            }
        
        # payload部分をデコード（Base64URL）
        payload_part = parts[1]
        # Base64URLパディングを追加
        padding = 4 - len(payload_part) % 4
        if padding != 4:
            payload_part += '=' * padding
        
        payload_bytes = base64.urlsafe_b64decode(payload_part)
        payload = json.loads(payload_bytes.decode('utf-8'))
        
        # sub（ユーザーID）を取得
        user_id = payload.get('sub', id_token[:32] if len(id_token) > 32 else id_token)
        display_name = payload.get('name', 'LINE User')
        
        return {
            'user_id': user_id,
            'display_name': display_name,
            'line_id': None  # LINE IDは取得できない場合がある
        }
    except Exception as e:
        # デコードに失敗した場合はフォールバック
        return {
            'user_id': id_token[:32] if len(id_token) > 32 else id_token,
            'display_name': 'LINE User',
            'line_id': None
        }


def lambda_handler(event, context):
    """
    LINE IDトークンを検証し、セッショントークンを返す
    POST /auth/verify
    
    リクエストボディ:
    {
        "id_token": "LINE_ID_TOKEN_STRING"
    }
    
    レスポンス:
    {
        "ok": true,
        "user_id": "USER_ID",
        "display_name": "Display Name",
        "access_token": "SESSION_TOKEN"
    }
    """
    try:
        # OPTIONSリクエストの処理（CORS preflight）
        if event.get('httpMethod') == 'OPTIONS':
            return create_response(200, {})
        
        # リクエストボディの取得
        body = json.loads(event.get('body', '{}'))
        id_token = body.get('id_token')
        
        # バリデーション
        if not id_token:
            return create_error_response(400, 'id_token is required')
        
        # LINE IDトークンの検証（現在はモック実装）
        try:
            token_info = verify_line_id_token_mock(id_token)
            user_id = token_info['user_id']
            display_name = token_info['display_name']
            line_id = token_info.get('line_id', '')
        except Exception as e:
            return create_error_response(401, f'Token verification failed: {str(e)}')
        
        # ユーザー情報のDynamoDB保存・更新
        try:
            user_data = create_or_update_user(
                user_id=user_id,
                display_name=display_name,
                line_id=line_id or user_id  # line_idがない場合はuser_idを使用
            )
        except Exception as e:
            return create_error_response(500, f'Failed to save user data: {str(e)}')
        
        # セッショントークンの生成
        try:
            session_token = generate_session_token(user_id, display_name)
        except Exception as e:
            return create_error_response(500, f'Failed to generate session token: {str(e)}')
        
        # レスポンスの作成
        response_data = {
            'ok': True,
            'user_id': user_id,
            'display_name': display_name,
            'access_token': session_token
        }
        
        return create_response(200, response_data)
        
    except json.JSONDecodeError:
        return create_error_response(400, 'Invalid JSON format')
    except Exception as e:
        return create_error_response(500, f'Internal Server Error: {str(e)}')

