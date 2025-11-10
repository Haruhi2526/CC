import json
import os
import requests
from response_utils import create_response, create_error_response

# LINE Messaging API設定
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
LINE_API_BASE_URL = 'https://api.line.me/v2/bot'
LIFF_BASE_URL = os.environ.get('LIFF_BASE_URL', '')


def lambda_handler(event, context):
    """
    プッシュ通知を送信
    
    POST /notify
    {
        "user_id": "USER_ID",
        "type": "stamp_awarded" | "event_started" | "reminder",
        "data": {
            "stamp_id": "STAMP_ID",
            "stamp_name": "スタンプ名",
            "stamp_image_url": "https://...",
            ...
        }
    }
    """
    try:
        # OPTIONSリクエストの処理（CORS preflight）
        if event.get('httpMethod') == 'OPTIONS':
            return create_response(200, {})
        
        # Channel Access Tokenの確認
        if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_ACCESS_TOKEN.strip():
            error_msg = 'LINE_CHANNEL_ACCESS_TOKEN is not configured or is empty. Please set it in Lambda environment variables.'
            print(error_msg)
            return create_error_response(500, error_msg)
        
        # リクエストボディの取得
        body = json.loads(event.get('body', '{}'))
        user_id = body.get('user_id')
        notify_type = body.get('type', 'stamp_awarded')
        data = body.get('data', {})
        
        if not user_id:
            return create_error_response(400, 'user_id is required')
        
        # 通知タイプに応じてメッセージを生成
        if notify_type == 'stamp_awarded':
            message = create_stamp_flex_message(
                data.get('stamp_name', 'スタンプ'),
                data.get('stamp_id', ''),
                data.get('stamp_image_url', '')
            )
        elif notify_type == 'event_started':
            message = create_event_text_message(data.get('event_name', 'イベント'))
        elif notify_type == 'reminder':
            message = create_reminder_text_message(data.get('stamp_name', 'スタンプ'))
        else:
            return create_error_response(400, f'Invalid notification type: {notify_type}')
        
        # プッシュ通知送信
        try:
            send_push_message(user_id, message)
            return create_response(200, {
                'ok': True,
                'message': 'Notification sent successfully',
                'user_id': user_id,
                'type': notify_type
            })
        except Exception as e:
            # 通知失敗の詳細をログに記録
            error_msg = f'Notification failed: {str(e)}'
            print(f'Error details: {error_msg}')
            print(f'User ID: {user_id}')
            print(f'Message type: {notify_type}')
            
            # エラーレスポンスを返す（デバッグ用に詳細情報を含める）
            return create_response(200, {
                'ok': False,
                'error': error_msg,
                'user_id': user_id,
                'type': notify_type,
                'hint': 'Check if user_id is valid and Channel Access Token is configured correctly'
            })
        
    except json.JSONDecodeError:
        return create_error_response(400, 'Invalid JSON format')
    except Exception as e:
        error_msg = f'Internal Server Error: {str(e)}'
        print(error_msg)
        return create_error_response(500, error_msg)


def send_push_message(user_id: str, message: dict):
    """
    LINEプッシュ通知を送信
    
    Args:
        user_id (str): LINEユーザーID
        message (dict): 送信するメッセージ（Flex MessageまたはText Message）
    
    Raises:
        Exception: LINE APIからのエラーレスポンスを含む例外
    """
    # Channel Access Tokenの再確認
    if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_ACCESS_TOKEN.strip():
        raise Exception('LINE_CHANNEL_ACCESS_TOKEN is not configured. Please set it in Lambda environment variables.')
    
    url = f'{LINE_API_BASE_URL}/message/push'
    
    # トークンをトリムして使用
    token = LINE_CHANNEL_ACCESS_TOKEN.strip()
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # デバッグ用（トークンの先頭数文字のみログに記録）
    token_preview = token[:10] + '...' if len(token) > 10 else '***'
    print(f'Using Channel Access Token: {token_preview} (length: {len(token)})')
    
    payload = {
        'to': user_id,
        'messages': [message]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        # エラーレスポンスの詳細を取得
        if not response.ok:
            error_detail = {}
            try:
                error_detail = response.json()
            except:
                error_detail = {'message': response.text}
            
            error_msg = f'LINE API Error ({response.status_code}): {error_detail.get("message", "Unknown error")}'
            if 'details' in error_detail:
                error_msg += f' Details: {error_detail["details"]}'
            
            print(f'LINE API Error Response: {json.dumps(error_detail)}')
            raise Exception(error_msg)
        
        return response.json()
    except requests.exceptions.RequestException as e:
        # ネットワークエラーなどの場合
        raise Exception(f'Request failed: {str(e)}')


def create_stamp_flex_message(stamp_name: str, stamp_id: str = '', image_url: str = ''):
    """
    スタンプ取得通知用のFlex Messageを生成
    
    Args:
        stamp_name (str): スタンプ名
        stamp_id (str): スタンプID
        image_url (str): スタンプ画像URL
    
    Returns:
        dict: Flex Message形式のメッセージ
    """
    # デフォルト画像URL（画像URLが指定されていない場合）
    if not image_url:
        image_url = 'https://via.placeholder.com/800x520/1DB446/FFFFFF?text=🎉'
    
    # LIFF URL（スタンプ一覧ページ）
    liff_url = f'{LIFF_BASE_URL}/index.html' if LIFF_BASE_URL else ''
    
    return {
        'type': 'flex',
        'altText': f'{stamp_name}を獲得しました！',
        'contents': {
            'type': 'bubble',
            'hero': {
                'type': 'image',
                'url': image_url,
                'size': 'full',
                'aspectRatio': '20:13',
                'aspectMode': 'cover'
            },
            'body': {
                'type': 'box',
                'layout': 'vertical',
                'contents': [
                    {
                        'type': 'text',
                        'text': '🎉 スタンプ獲得！',
                        'weight': 'bold',
                        'size': 'xl',
                        'color': '#1DB446',
                        'margin': 'md'
                    },
                    {
                        'type': 'text',
                        'text': stamp_name,
                        'size': 'md',
                        'margin': 'md',
                        'wrap': True
                    }
                ]
            },
            'footer': {
                'type': 'box',
                'layout': 'vertical',
                'spacing': 'sm',
                'contents': [
                    {
                        'type': 'button',
                        'style': 'primary',
                        'height': 'sm',
                        'action': {
                            'type': 'uri',
                            'label': 'スタンプ一覧を見る',
                            'uri': liff_url if liff_url else 'https://line.me'
                        },
                        'color': '#1DB446'
                    }
                ],
                'flex': 0
            }
        }
    }


def create_event_text_message(event_name: str):
    """
    イベント開始通知用のテキストメッセージを生成
    
    Args:
        event_name (str): イベント名
    
    Returns:
        dict: Text Message形式のメッセージ
    """
    return {
        'type': 'text',
        'text': f'📢 新イベント開始！\n{event_name}\n\nスタンプラリーアプリを開いて確認しましょう！'
    }


def create_reminder_text_message(stamp_name: str):
    """
    リマインド通知用のテキストメッセージを生成
    
    Args:
        stamp_name (str): スタンプ名
    
    Returns:
        dict: Text Message形式のメッセージ
    """
    return {
        'type': 'text',
        'text': f'⏰ まだ取得していないスタンプがあります\n\n{stamp_name}\n\nスタンプラリーアプリを開いて確認しましょう！'
    }

