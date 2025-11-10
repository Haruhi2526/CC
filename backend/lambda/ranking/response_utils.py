import json


def create_response(status_code, body):
    """
    標準的なHTTPレスポンスを作成（共通ユーティリティ）
    
    Args:
        status_code (int): HTTPステータスコード
        body (dict): レスポンスボディ
    
    Returns:
        dict: API Gateway用のレスポンス形式
    """
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


def create_error_response(status_code, error_message, error_code=None):
    """
    エラーレスポンスを作成
    
    Args:
        status_code (int): HTTPステータスコード
        error_message (str): エラーメッセージ
        error_code (str, optional): エラーコード
    
    Returns:
        dict: API Gateway用のレスポンス形式
    """
    body = {
        'ok': False,
        'error': 'Error',
        'message': error_message
    }
    if error_code:
        body['error_code'] = error_code
    
    return create_response(status_code, body)

