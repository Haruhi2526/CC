import json
from dynamodb_utils import get_user_stamps, get_stamp_master
from response_utils import create_response


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
        
        # DynamoDBからスタンプ一覧を取得
        user_stamps = get_user_stamps(user_id)
        
        # スタンプマスタ情報を取得して結合
        stamps_detail = []
        for user_stamp in user_stamps:
            stamp_id = user_stamp.get('StampId')
            stamp_master = get_stamp_master(stamp_id)
            
            if stamp_master:
                # スタンプ情報を結合
                stamp_info = {
                    'stamp_id': stamp_id,
                    'name': stamp_master.get('Name'),
                    'description': stamp_master.get('Description'),
                    'type': stamp_master.get('Type'),
                    'collected_at': user_stamp.get('CollectedAt'),
                    'method': user_stamp.get('Method')
                }
                stamps_detail.append(stamp_info)
        
        response_data = {
            'ok': True,
            'user_id': user_id,
            'stamps': stamps_detail,
            'total': len(stamps_detail)
        }
        
        return create_response(200, response_data)
        
    except Exception as e:
        return create_response(500, {
            'error': 'Internal Server Error',
            'message': str(e)
        })

