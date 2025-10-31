import json
from datetime import datetime


def lambda_handler(event, context):
    """
    ユーザーの保有スタンプ一覧を取得
    GET /stamps?userId={userId}
    """
    try:
        # クエリパラメータの取得
        query_params = event.get('queryStringParameters') or {}
        user_id = query_params.get('userId')
        
        # バリデーション
        if not user_id:
            return create_response(400, {
                'error': 'Bad Request',
                'message': 'userId is required'
            })
        
        # TODO: DynamoDBからスタンプ一覧を取得
        # - UserStampsテーブルからuserIdでクエリ
        # - StampMastersテーブルと結合してスタンプ詳細を取得
        
        # 暫定的なレスポンス（実装後に削除）
        response_data = {
            'ok': True,
            'user_id': user_id,
            'stamps': [],
            'total': 0
        }
        
        return create_response(200, response_data)
        
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

