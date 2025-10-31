import json
from datetime import datetime


def lambda_handler(event, context):
    """
    LINE IDトークンを検証し、セッショントークンを返す
    POST /auth/verify
    """
    try:
        # リクエストボディの取得
        body = json.loads(event.get('body', '{}'))
        id_token = body.get('id_token')
        
        # バリデーション
        if not id_token:
            return create_response(400, {
                'error': 'Bad Request',
                'message': 'id_token is required'
            })
        
        # TODO: LINE IDトークンの検証実装
        # - LINE Messaging API SDKを使用
        # - トークンの有効性確認
        # - ユーザー情報の取得
        
        # TODO: ユーザー情報のDynamoDB保存・更新
        # - Usersテーブルにユーザー情報を保存
        # - 存在しない場合は新規作成
        
        # 暫定的なレスポンス（実装後に削除）
        response_data = {
            'ok': True,
            'message': 'Authentication successful (temporary)',
            'user_id': 'temp_user_id',
            'access_token': 'temp_access_token'
        }
        
        return create_response(200, response_data)
        
    except json.JSONDecodeError:
        return create_response(400, {
            'error': 'Bad Request',
            'message': 'Invalid JSON format'
        })
    except Exception as e:
        return create_response(500, {
            'error': 'Internal Server Error',
            'message': str(e)
        })


def create_response(status_code, body):
    """標準的なHTTPレスポンスを作成"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  # 後でCORS設定に置き換え
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
        },
        'body': json.dumps(body, ensure_ascii=False)
    }

