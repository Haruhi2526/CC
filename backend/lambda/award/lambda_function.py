import json
import time
from dynamodb_utils import get_stamp_master, check_stamp_exists, add_user_stamp
from response_utils import create_response, create_error_response


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
        stamp_type = stamp_master.get('Type', '').upper()
        if stamp_type and stamp_type != method:
            return create_error_response(400, 
                f'Stamp type mismatch. Expected: {stamp_type}, Got: {method}', 
                'STAMP_TYPE_MISMATCH')
        
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

