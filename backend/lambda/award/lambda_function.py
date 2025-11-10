import json
import os
import time
import boto3
from dynamodb_utils import get_stamp_master, check_stamp_exists, add_user_stamp
from response_utils import create_response, create_error_response

# Lambdaクライアント（通知送信用）
lambda_client = boto3.client('lambda')


def validate_award_request(body: dict) -> tuple[bool, str, dict]:
    """
    スタンプ授与リクエストのバリデーション
    
    Args:
        body (dict): リクエストボディ
    
    Returns:
        tuple: (is_valid, error_message, validated_data)
            is_valid: バリデーション成功時True
            error_message: エラーメッセージ（is_validがFalseの場合）
            validated_data: バリデーション済みデータ（is_validがTrueの場合）
    """
    # 必須パラメータのチェック
    user_id = body.get('user_id')
    stamp_id = body.get('stamp_id')
    method = body.get('method')
    
    if not user_id:
        return False, 'user_id is required', {}
    
    if not stamp_id:
        return False, 'stamp_id is required', {}
    
    if not method:
        return False, 'method is required', {}
    
    # methodの値チェック（GPSまたはIMAGEのみ許可）
    if method not in ['GPS', 'IMAGE']:
        return False, 'method must be either GPS or IMAGE', {}
    
    return True, '', {
        'user_id': user_id,
        'stamp_id': stamp_id,
        'method': method
    }


def lambda_handler(event, context):
    """
    スタンプを授与する
    POST /stamps/award
    
    リクエストボディ:
    {
        "user_id": "USER_ID",
        "stamp_id": "STAMP_ID",
        "method": "GPS" or "IMAGE"
    }
    
    レスポンス（成功時）:
    {
        "ok": true,
        "user_id": "USER_ID",
        "stamp_id": "STAMP_ID",
        "method": "GPS",
        "collected_at": 1234567890,
        "message": "Stamp awarded successfully"
    }
    
    レスポンス（エラー時）:
    {
        "error": "Error",
        "message": "Error message",
        "error_code": "ERROR_CODE" (optional)
    }
    """
    try:
        # OPTIONSリクエストの処理（CORS preflight）
        if event.get('httpMethod') == 'OPTIONS':
            return create_response(200, {})
        
        # リクエストボディの取得
        body = json.loads(event.get('body', '{}'))
        
        # バリデーション
        is_valid, error_message, validated_data = validate_award_request(body)
        if not is_valid:
            return create_error_response(400, error_message, 'VALIDATION_ERROR')
        
        user_id = validated_data['user_id']
        stamp_id = validated_data['stamp_id']
        method = validated_data['method']
        
        # スタンプマスタの存在確認
        try:
            stamp_master = get_stamp_master(stamp_id)
            if not stamp_master:
                return create_error_response(404, f'Stamp not found: {stamp_id}', 'STAMP_NOT_FOUND')
        except Exception as e:
            return create_error_response(500, f'Failed to check stamp master: {str(e)}', 'DATABASE_ERROR')
        
        # スタンプマスタの有効期間チェック（オプション）
        current_time = int(time.time())
        valid_from = stamp_master.get('ValidFrom')
        valid_to = stamp_master.get('ValidTo')
        
        if valid_from and current_time < valid_from:
            return create_error_response(400, f'Stamp is not yet valid. Valid from: {valid_from}', 'STAMP_NOT_VALID_YET')
        
        if valid_to and current_time > valid_to:
            return create_error_response(400, f'Stamp has expired. Valid until: {valid_to}', 'STAMP_EXPIRED')
        
        # スタンプタイプのチェック（GPS/IMAGEと一致しているか）
        # 注意: スタンプマスターのTypeが設定されている場合のみチェック
        # Typeが設定されていない場合は、GPS/IMAGEのどちらでも許可
        stamp_type = stamp_master.get('Type', '').upper()
        if stamp_type and stamp_type not in ['GPS', 'IMAGE']:
            # TypeがGPS/IMAGE以外の場合はエラー
            return create_error_response(400, 
                f'Invalid stamp type: {stamp_type}', 
                'INVALID_STAMP_TYPE')
        
        # Typeが設定されている場合、methodと一致することを確認
        # ただし、Typeが設定されていない場合は、GPS/IMAGEのどちらでも許可
        if stamp_type and stamp_type != method:
            # 警告ログを出力するが、エラーにはしない（両方の方法で取得可能にする）
            print(f'Warning: Stamp type mismatch. Expected: {stamp_type}, Got: {method}. Proceeding anyway.')
            # エラーにしない（両方の方法で取得可能にする）
            # return create_error_response(400, 
            #     f'Stamp type mismatch. Expected: {stamp_type}, Got: {method}', 
            #     'STAMP_TYPE_MISMATCH')
        
        # 重複チェック
        try:
            if check_stamp_exists(user_id, stamp_id):
                return create_error_response(409, 
                    f'User already has this stamp: {stamp_id}', 
                    'STAMP_ALREADY_EXISTS')
        except Exception as e:
            return create_error_response(500, f'Failed to check stamp existence: {str(e)}', 'DATABASE_ERROR')
        
        # スタンプを追加
        try:
            result = add_user_stamp(user_id, stamp_id, method)
            
            # スタンプ授与成功時に通知を送信（非同期）
            send_notification_async(user_id, stamp_id, stamp_master)
            
            # レスポンスの作成
            response_data = {
                'ok': True,
                'user_id': result['UserId'],
                'stamp_id': result['StampId'],
                'method': result['Method'],
                'collected_at': result['CollectedAt'],
                'message': 'Stamp awarded successfully'
            }
            
            return create_response(200, response_data)
            
        except Exception as e:
            return create_error_response(500, f'Failed to add stamp: {str(e)}', 'DATABASE_ERROR')
        
    except json.JSONDecodeError:
        return create_error_response(400, 'Invalid JSON format', 'INVALID_JSON')
    except Exception as e:
        return create_error_response(500, f'Internal Server Error: {str(e)}', 'INTERNAL_ERROR')


def send_notification_async(user_id: str, stamp_id: str, stamp_master: dict):
    """
    スタンプ取得通知を非同期で送信
    
    Args:
        user_id (str): ユーザーID
        stamp_id (str): スタンプID
        stamp_master (dict): スタンプマスタ情報
    """
    try:
        # notify関数の関数名を環境変数から取得（デフォルト: notify）
        notify_function_name = os.environ.get('NOTIFY_FUNCTION_NAME', 'notify')
        
        # 通知データの準備
        stamp_name = stamp_master.get('Name', 'スタンプ')
        stamp_image_url = stamp_master.get('ImageUrl', '')
        
        # notify関数を非同期で呼び出し
        lambda_client.invoke(
            FunctionName=notify_function_name,
            InvocationType='Event',  # 非同期実行
            Payload=json.dumps({
                'httpMethod': 'POST',
                'body': json.dumps({
                    'user_id': user_id,
                    'type': 'stamp_awarded',
                    'data': {
                        'stamp_id': stamp_id,
                        'stamp_name': stamp_name,
                        'stamp_image_url': stamp_image_url
                    }
                })
            })
        )
    except Exception as e:
        # 通知失敗はログのみ（スタンプ授与は成功）
        print(f'Failed to send notification: {str(e)}')

