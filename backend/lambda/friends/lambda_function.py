import json
import os
import boto3
from datetime import datetime
from response_utils import create_response, create_error_response

# DynamoDBクライアントの初期化
dynamodb = boto3.resource('dynamodb')


def get_table(table_name: str):
    """
    DynamoDBテーブルリソースを取得
    
    Args:
        table_name (str): テーブル名（環境変数から取得可）
    
    Returns:
        dynamodb.Table: テーブルリソース
    """
    env_table_name = os.environ.get(f'TABLE_{table_name.upper()}', table_name)
    return dynamodb.Table(env_table_name)


def lambda_handler(event, context):
    """
    友達関係管理API
    
    エンドポイント:
    - POST /friends/add - 友達関係を追加
    - GET /friends/list?user_id=XXX - 友達リストを取得
    """
    try:
        # OPTIONSリクエストの処理（CORS preflight）
        if event.get('httpMethod') == 'OPTIONS':
            return create_response(200, {})
        
        method = event.get('httpMethod')
        path = event.get('path', '')
        query_params = event.get('queryStringParameters') or {}
        
        if method == 'POST' and '/friends/add' in path:
            # 友達関係を追加
            body = json.loads(event.get('body', '{}'))
            user_id = body.get('user_id')
            friend_id = body.get('friend_id')
            if not user_id or not friend_id:
                return create_error_response(400, 'user_id and friend_id are required')
            return add_friend(user_id, friend_id)
        elif method == 'GET' and '/friends/list' in path:
            # 友達リストを取得
            user_id = query_params.get('user_id')
            if not user_id:
                return create_error_response(400, 'user_id is required')
            return get_friends(user_id)
        else:
            return create_error_response(404, 'Not Found')
            
    except Exception as e:
        error_msg = f'Internal Server Error: {str(e)}'
        print(error_msg)
        return create_error_response(500, error_msg)


def add_friend(user_id: str, friend_id: str):
    """
    友達関係を追加（双方向）
    
    Args:
        user_id (str): ユーザーID
        friend_id (str): 友達のユーザーID
    
    Returns:
        dict: API Gateway用のレスポンス
    """
    if not user_id or not friend_id:
        return create_error_response(400, 'user_id and friend_id are required')
    
    if user_id == friend_id:
        return create_error_response(400, 'Cannot add yourself as a friend')
    
    try:
        friends_table = get_table('Friends')
        timestamp = int(datetime.now().timestamp())
        
        # 双方向の友達関係を追加
        # user_id -> friend_id
        friends_table.put_item(
            Item={
                'UserId': user_id,
                'FriendId': friend_id,
                'CreatedAt': timestamp,
                'Status': 'active'
            }
        )
        
        # friend_id -> user_id（双方向）
        friends_table.put_item(
            Item={
                'UserId': friend_id,
                'FriendId': user_id,
                'CreatedAt': timestamp,
                'Status': 'active'
            }
        )
        
        return create_response(200, {
            'ok': True,
            'message': 'Friend relationship added successfully',
            'user_id': user_id,
            'friend_id': friend_id
        })
    except Exception as e:
        error_msg = f'Failed to add friend: {str(e)}'
        print(error_msg)
        return create_error_response(500, error_msg)


def get_friends(user_id: str):
    """
    友達リストを取得
    
    Args:
        user_id (str): ユーザーID
    
    Returns:
        dict: API Gateway用のレスポンス
    """
    if not user_id:
        return create_error_response(400, 'user_id is required')
    
    try:
        friends_table = get_table('Friends')
        
        response = friends_table.query(
            KeyConditionExpression='UserId = :user_id',
            ExpressionAttributeValues={':user_id': user_id}
        )
        
        # Statusが'active'の友達のみをフィルタリング
        friends = []
        for item in response.get('Items', []):
            if item.get('Status', 'active') == 'active':
                friends.append({
                    'friend_id': item['FriendId'],
                    'created_at': int(item.get('CreatedAt', 0))
                })
        
        return create_response(200, {
            'ok': True,
            'user_id': user_id,
            'friends': friends,
            'count': len(friends)
        })
    except Exception as e:
        error_msg = f'Failed to get friends: {str(e)}'
        print(error_msg)
        return create_error_response(500, error_msg)

