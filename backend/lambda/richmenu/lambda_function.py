import json
import os
import requests
from response_utils import create_response, create_error_response

# LINE Messaging API設定
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
LINE_API_BASE_URL = 'https://api.line.me/v2/bot'


def lambda_handler(event, context):
    """
    リッチメニュー管理API
    
    エンドポイント:
    - GET /richmenu/list: リッチメニュー一覧取得
    - POST /richmenu/set: ユーザーにリッチメニューを設定
    - DELETE /richmenu/unset: ユーザーからリッチメニューを削除
    """
    try:
        # OPTIONSリクエストの処理（CORS preflight）
        if event.get('httpMethod') == 'OPTIONS':
            return create_response(200, {})
        
        # Channel Access Tokenの確認
        if not LINE_CHANNEL_ACCESS_TOKEN:
            return create_error_response(500, 'LINE_CHANNEL_ACCESS_TOKEN is not configured')
        
        method = event.get('httpMethod')
        path = event.get('path', '')
        
        # リクエストボディの取得
        body_str = event.get('body', '{}')
        body = json.loads(body_str) if body_str else {}
        
        # エンドポイント別の処理
        if method == 'GET' and '/richmenu/list' in path:
            # リッチメニュー一覧取得
            return get_richmenu_list()
        elif method == 'POST' and '/richmenu/set' in path:
            # リッチメニュー設定
            user_id = body.get('user_id')
            richmenu_id = body.get('richmenu_id')
            if not user_id or not richmenu_id:
                return create_error_response(400, 'user_id and richmenu_id are required')
            return set_richmenu(user_id, richmenu_id)
        elif method == 'DELETE' and '/richmenu/unset' in path:
            # リッチメニュー削除
            user_id = body.get('user_id')
            if not user_id:
                return create_error_response(400, 'user_id is required')
            return unset_richmenu(user_id)
        elif method == 'GET' and '/richmenu/default' in path:
            # デフォルトリッチメニューID取得
            return get_default_richmenu()
        else:
            return create_error_response(404, 'Not Found')
            
    except json.JSONDecodeError:
        return create_error_response(400, 'Invalid JSON format')
    except Exception as e:
        print(f'Error: {str(e)}')
        return create_error_response(500, f'Internal Server Error: {str(e)}')


def get_richmenu_list():
    """
    リッチメニュー一覧を取得
    
    Returns:
        dict: API Gateway用のレスポンス
    """
    try:
        url = f'{LINE_API_BASE_URL}/richmenu/list'
        headers = {
            'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        return create_response(200, {
            'ok': True,
            'richmenus': data.get('richmenus', [])
        })
        
    except requests.exceptions.RequestException as e:
        error_msg = f'Failed to get richmenu list: {str(e)}'
        print(error_msg)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f'LINE API Error: {error_detail}')
            except:
                print(f'Response status: {e.response.status_code}')
        return create_error_response(500, error_msg)


def set_richmenu(user_id: str, richmenu_id: str):
    """
    ユーザーにリッチメニューを設定
    
    Args:
        user_id (str): LINEユーザーID
        richmenu_id (str): リッチメニューID
    
    Returns:
        dict: API Gateway用のレスポンス
    """
    try:
        url = f'{LINE_API_BASE_URL}/user/{user_id}/richmenu/{richmenu_id}'
        headers = {
            'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        return create_response(200, {
            'ok': True,
            'message': 'Richmenu set successfully',
            'user_id': user_id,
            'richmenu_id': richmenu_id
        })
        
    except requests.exceptions.RequestException as e:
        error_msg = f'Failed to set richmenu: {str(e)}'
        print(error_msg)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f'LINE API Error: {error_detail}')
                # LINE APIのエラーメッセージを返す
                if 'message' in error_detail:
                    error_msg = error_detail['message']
            except:
                print(f'Response status: {e.response.status_code}')
        return create_error_response(500, error_msg)


def unset_richmenu(user_id: str):
    """
    ユーザーからリッチメニューを削除
    
    Args:
        user_id (str): LINEユーザーID
    
    Returns:
        dict: API Gateway用のレスポンス
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
            'message': 'Richmenu unset successfully',
            'user_id': user_id
        })
        
    except requests.exceptions.RequestException as e:
        error_msg = f'Failed to unset richmenu: {str(e)}'
        print(error_msg)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f'LINE API Error: {error_detail}')
                if 'message' in error_detail:
                    error_msg = error_detail['message']
            except:
                print(f'Response status: {e.response.status_code}')
        return create_error_response(500, error_msg)


def get_default_richmenu():
    """
    デフォルトリッチメニューIDを取得
    
    Returns:
        dict: API Gateway用のレスポンス
    """
    try:
        url = f'{LINE_API_BASE_URL}/richmenu/default'
        headers = {
            'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        return create_response(200, {
            'ok': True,
            'richmenuId': data.get('richmenuId')
        })
        
    except requests.exceptions.RequestException as e:
        error_msg = f'Failed to get default richmenu: {str(e)}'
        print(error_msg)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f'LINE API Error: {error_detail}')
            except:
                print(f'Response status: {e.response.status_code}')
        return create_error_response(500, error_msg)

