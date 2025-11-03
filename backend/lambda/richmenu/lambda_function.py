import json
import os
import requests
from response_utils import create_response, create_error_response

# LINE Messaging API設定
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
LINE_API_BASE_URL = 'https://api.line.me/v2/bot'

# Secrets Managerからトークンを取得する場合（将来の拡張用）
# import boto3
# def get_channel_access_token():
#     secrets_manager = boto3.client('secretsmanager')
#     secret = secrets_manager.get_secret_value(SecretId='line-channel-access-token')
#     return json.loads(secret['SecretString'])['token']


def lambda_handler(event, context):
    """
    リッチメニュー管理API
    GET /richmenu/list - リッチメニュー一覧取得
    POST /richmenu/set - ユーザーにリッチメニューを設定
    DELETE /richmenu/unset/{userId} - ユーザーのリッチメニューを削除
    GET /richmenu/{richmenuId} - リッチメニュー詳細取得
    """
    try:
        # OPTIONSリクエストの処理（CORS preflight）
        if event.get('httpMethod') == 'OPTIONS':
            return create_response(200, {})
        
        # チャンネルアクセストークンの確認
        if not LINE_CHANNEL_ACCESS_TOKEN:
            return create_error_response(
                500, 
                'LINE_CHANNEL_ACCESS_TOKEN environment variable is not set',
                'CONFIG_ERROR'
            )
        
        method = event.get('httpMethod')
        path = event.get('path', '')
        path_parameters = event.get('pathParameters') or {}
        query_params = event.get('queryStringParameters') or {}
        
        # リクエストルーティング
        if method == 'GET' and '/richmenu/list' in path:
            # リッチメニュー一覧取得
            return get_richmenu_list()
        
        elif method == 'GET' and path_parameters.get('richmenuId'):
            # リッチメニュー詳細取得
            richmenu_id = path_parameters.get('richmenuId')
            return get_richmenu(richmenu_id)
        
        elif method == 'POST' and '/richmenu/set' in path:
            # リッチメニュー設定
            body = json.loads(event.get('body', '{}'))
            user_id = body.get('user_id')
            richmenu_id = body.get('richmenu_id')
            
            if not user_id:
                return create_error_response(400, 'user_id is required', 'VALIDATION_ERROR')
            if not richmenu_id:
                return create_error_response(400, 'richmenu_id is required', 'VALIDATION_ERROR')
            
            # リッチメニューIDの形式チェック（推奨形式: richmenu-...）
            # ただし、数字のみの場合も許可（LINE APIの仕様により）
            print(f'Setting richmenu: user_id={user_id}, richmenu_id={richmenu_id}')
            
            return set_richmenu(user_id, richmenu_id)
        
        elif method == 'DELETE' and path_parameters.get('userId'):
            # ユーザーのリッチメニューを削除
            user_id = path_parameters.get('userId')
            return unset_richmenu(user_id)
        
        else:
            return create_error_response(404, 'Not Found', 'NOT_FOUND')
            
    except json.JSONDecodeError:
        return create_error_response(400, 'Invalid JSON format', 'INVALID_JSON')
    except Exception as e:
        print(f'Error in richmenu lambda: {str(e)}')
        return create_error_response(500, f'Internal Server Error: {str(e)}', 'INTERNAL_ERROR')


def get_richmenu_list():
    """
    リッチメニュー一覧を取得
    LINE Messaging API: GET /richmenu/list
    """
    try:
        url = f'{LINE_API_BASE_URL}/richmenu/list'
        headers = {
            'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        print(f'Requesting richmenu list from: {url}')
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        print(f'Richmenu list response: {result}')
        
        # リッチメニューが0件の場合も正常なレスポンスとして返す
        return create_response(200, result)
        
    except requests.exceptions.RequestException as e:
        error_message = f'Failed to get richmenu list: {str(e)}'
        status_code = 500
        
        if hasattr(e, 'response') and e.response is not None:
            status_code = e.response.status_code
            try:
                error_detail = e.response.json()
                error_message = f'{error_message} - {json.dumps(error_detail)}'
                print(f'LINE API error detail: {error_detail}')
            except:
                error_message = f'{error_message} - Status: {e.response.status_code}'
                print(f'LINE API error status: {e.response.status_code}')
                print(f'Response text: {e.response.text}')
        
        print(f'Error: {error_message}')
        return create_error_response(status_code, error_message, 'LINE_API_ERROR')


def get_richmenu(richmenu_id):
    """
    リッチメニューの詳細を取得
    LINE Messaging API: GET /richmenu/{richmenuId}
    """
    try:
        url = f'{LINE_API_BASE_URL}/richmenu/{richmenu_id}'
        headers = {
            'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        return create_response(200, response.json())
        
    except requests.exceptions.RequestException as e:
        error_message = f'Failed to get richmenu: {str(e)}'
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                error_message += f' - {error_detail}'
            except:
                error_message += f' - Status: {e.response.status_code}'
        print(error_message)
        return create_error_response(500, error_message, 'LINE_API_ERROR')


def set_richmenu(user_id, richmenu_id):
    """
    ユーザーにリッチメニューを設定
    LINE Messaging API: POST /user/{userId}/richmenu/{richmenuId}
    
    Args:
        user_id (str): LINEユーザーID
        richmenu_id (str): リッチメニューID
    """
    try:
        url = f'{LINE_API_BASE_URL}/user/{user_id}/richmenu/{richmenu_id}'
        headers = {
            'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        print(f'Setting richmenu - URL: {url}')
        print(f'User ID: {user_id}, Richmenu ID: {richmenu_id}')
        
        response = requests.post(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        print(f'Richmenu set successfully')
        return create_response(200, {
            'ok': True,
            'user_id': user_id,
            'richmenu_id': richmenu_id,
            'message': 'Rich menu set successfully'
        })
        
    except requests.exceptions.RequestException as e:
        error_message = f'Failed to set richmenu: {str(e)}'
        status_code = 500
        line_api_error = None
        
        if hasattr(e, 'response') and e.response is not None:
            status_code = e.response.status_code
            print(f'LINE API response status: {status_code}')
            print(f'LINE API response text: {e.response.text}')
            
            try:
                error_detail = e.response.json()
                print(f'LINE API error detail: {error_detail}')
                
                # LINE APIのエラーメッセージを解析
                if 'message' in error_detail:
                    line_api_error = error_detail['message']
                    error_message = f'{error_detail["message"]} (richmenu_id: {richmenu_id})'
                else:
                    error_message = f'{error_message} - {json.dumps(error_detail)}'
                    
            except Exception as parse_error:
                error_message = f'{error_message} - Status: {e.response.status_code}, Response: {e.response.text[:200]}'
                print(f'Failed to parse error response: {parse_error}')
        
        print(f'Error setting richmenu: {error_message}')
        
        # 404エラーの場合は、より詳細なメッセージを返す
        if status_code == 404:
            if line_api_error:
                error_message = f'Rich menu not found: {richmenu_id}. {line_api_error}'
            else:
                error_message = f'Rich menu not found: {richmenu_id}. Please check if the rich menu exists and is published in LINE Developers Console.'
        
        return create_error_response(status_code, error_message, 'LINE_API_ERROR')


def unset_richmenu(user_id):
    """
    ユーザーのリッチメニューを削除
    LINE Messaging API: DELETE /user/{userId}/richmenu
    
    Args:
        user_id (str): LINEユーザーID
    """
    try:
        url = f'{LINE_API_BASE_URL}/user/{user_id}/richmenu'
        headers = {
            'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        response = requests.delete(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        return create_response(200, {
            'ok': True,
            'user_id': user_id,
            'message': 'Rich menu unset successfully'
        })
        
    except requests.exceptions.RequestException as e:
        error_message = f'Failed to unset richmenu: {str(e)}'
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                error_message += f' - {error_detail}'
            except:
                error_message += f' - Status: {e.response.status_code}'
        print(error_message)
        return create_error_response(500, error_message, 'LINE_API_ERROR')

