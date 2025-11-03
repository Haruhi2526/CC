import json
from dynamodb_utils import get_user_stamps, get_stamp_master
from response_utils import create_response


def lambda_handler(event, context):
    """
    ユーザーの保有スタンプ一覧を取得
    GET /stamps?userId={userId}
    """
    try:
        # OPTIONSリクエストの処理（CORS preflight）
        if event.get('httpMethod') == 'OPTIONS':
            return create_response(200, {})
        
        # クエリパラメータの取得
        # Lambdaプロキシ統合の場合、queryStringParametersはNoneの可能性がある
        query_params = event.get('queryStringParameters') or {}
        
        # デバッグログ（CloudWatch Logsで確認）
        print(f"Event: {json.dumps(event)}")
        print(f"Query params: {query_params}")
        
        user_id = query_params.get('userId') if query_params else None
        
        # クエリパラメータがNoneの場合の処理
        if query_params is None or not user_id:
            return create_response(400, {
                'error': 'Bad Request',
                'message': f'userId is required. queryStringParameters: {query_params}'
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

