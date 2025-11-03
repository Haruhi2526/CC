import boto3
import os
from decimal import Decimal
from typing import Dict, List, Optional, Any


# DynamoDBクライアントの初期化
dynamodb = boto3.resource('dynamodb')
dynamodb_client = boto3.client('dynamodb')


def get_table(table_name: str):
    """
    DynamoDBテーブルリソースを取得
    
    Args:
        table_name (str): テーブル名（環境変数から取得可）
    
    Returns:
        dynamodb.Table: テーブルリソース
    """
    # 環境変数からテーブル名を取得（プレフィックス付き）
    env_table_name = os.environ.get(f'TABLE_{table_name.upper()}', table_name)
    return dynamodb.Table(env_table_name)


def decimal_default(obj):
    """
    Decimal型をfloat/intに変換（JSONシリアライズ用）
    """
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError


def get_user_stamps(user_id: str) -> List[Dict[str, Any]]:
    """
    ユーザーのスタンプ収集状況を取得
    
    Args:
        user_id (str): ユーザーID（LINE UID）
    
    Returns:
        List[Dict]: スタンプ収集情報のリスト
    """
    table = get_table('UserStamps')
    
    try:
        response = table.query(
            KeyConditionExpression='UserId = :user_id',
            ExpressionAttributeValues={
                ':user_id': user_id
            }
        )
        
        # Decimal型を変換
        items = response.get('Items', [])
        result = []
        for item in items:
            # Decimalを変換
            converted_item = {}
            for key, value in item.items():
                if isinstance(value, Decimal):
                    converted_item[key] = int(value) if value % 1 == 0 else float(value)
                else:
                    converted_item[key] = value
            result.append(converted_item)
        
        return result
    except Exception as e:
        raise Exception(f"Failed to get user stamps: {str(e)}")


def get_stamp_master(stamp_id: str) -> Optional[Dict[str, Any]]:
    """
    スタンプマスタ情報を取得
    
    Args:
        stamp_id (str): スタンプID
    
    Returns:
        Optional[Dict]: スタンプマスタ情報（存在しない場合はNone）
    """
    table = get_table('StampMasters')
    
    try:
        response = table.get_item(
            Key={
                'StampId': stamp_id
            }
        )
        
        if 'Item' not in response:
            return None
        
        item = response['Item']
        # Decimal型を変換
        converted_item = {}
        for key, value in item.items():
            if isinstance(value, Decimal):
                converted_item[key] = int(value) if value % 1 == 0 else float(value)
            elif isinstance(value, dict):
                # Map型のLocationなども変換
                converted_item[key] = {k: (int(v) if isinstance(v, Decimal) and v % 1 == 0 else float(v) if isinstance(v, Decimal) else v) for k, v in value.items()}
            else:
                converted_item[key] = value
        
        return converted_item
    except Exception as e:
        raise Exception(f"Failed to get stamp master: {str(e)}")


def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """
    ユーザー情報を取得
    
    Args:
        user_id (str): ユーザーID（LINE UID）
    
    Returns:
        Optional[Dict]: ユーザー情報（存在しない場合はNone）
    """
    table = get_table('Users')
    
    try:
        response = table.get_item(
            Key={
                'UserId': user_id
            }
        )
        
        if 'Item' not in response:
            return None
        
        item = response['Item']
        # Decimal型を変換
        converted_item = {}
        for key, value in item.items():
            if isinstance(value, Decimal):
                converted_item[key] = int(value) if value % 1 == 0 else float(value)
            else:
                converted_item[key] = value
        
        return converted_item
    except Exception as e:
        raise Exception(f"Failed to get user: {str(e)}")


def create_or_update_user(user_id: str, display_name: str, line_id: str) -> Dict[str, Any]:
    """
    ユーザーを作成または更新
    
    Args:
        user_id (str): ユーザーID（LINE UID）
        display_name (str): 表示名
        line_id (str): LINE ID
    
    Returns:
        Dict: 作成/更新されたユーザー情報
    """
    table = get_table('Users')
    import time
    
    current_time = int(time.time())
    
    try:
        response = table.update_item(
            Key={
                'UserId': user_id
            },
            UpdateExpression='SET DisplayName = :name, LineId = :line_id, LastLoginAt = :login_time ADD CreatedAt :zero',
            ExpressionAttributeValues={
                ':name': display_name,
                ':line_id': line_id,
                ':login_time': current_time,
                ':zero': 0  # CreatedAtが存在しない場合のみ0を追加
            },
            ReturnValues='ALL_NEW'
        )
        
        item = response['Attributes']
        # Decimal型を変換
        converted_item = {}
        for key, value in item.items():
            if isinstance(value, Decimal):
                converted_item[key] = int(value) if value % 1 == 0 else float(value)
            else:
                converted_item[key] = value
        
        # CreatedAtが0の場合は現在時刻を設定
        if converted_item.get('CreatedAt') == 0:
            table.update_item(
                Key={'UserId': user_id},
                UpdateExpression='SET CreatedAt = :created',
                ExpressionAttributeValues={':created': current_time}
            )
            converted_item['CreatedAt'] = current_time
        
        return converted_item
    except Exception as e:
        raise Exception(f"Failed to create/update user: {str(e)}")


def add_user_stamp(user_id: str, stamp_id: str, method: str) -> Dict[str, Any]:
    """
    ユーザーにスタンプを追加
    
    Args:
        user_id (str): ユーザーID（LINE UID）
        stamp_id (str): スタンプID
        method (str): 収集方法（GPS/IMAGE）
    
    Returns:
        Dict: 追加されたスタンプ情報
    """
    table = get_table('UserStamps')
    import time
    
    current_time = int(time.time())
    
    try:
        item = {
            'UserId': user_id,
            'StampId': stamp_id,
            'CollectedAt': current_time,
            'Method': method
        }
        
        response = table.put_item(Item=item)
        
        return {
            'UserId': user_id,
            'StampId': stamp_id,
            'CollectedAt': current_time,
            'Method': method
        }
    except Exception as e:
        raise Exception(f"Failed to add user stamp: {str(e)}")

