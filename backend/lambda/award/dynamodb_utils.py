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


def check_stamp_exists(user_id: str, stamp_id: str) -> bool:
    """
    ユーザーが既に特定のスタンプを持っているかチェック
    
    Args:
        user_id (str): ユーザーID（LINE UID）
        stamp_id (str): スタンプID
    
    Returns:
        bool: スタンプが存在する場合はTrue、存在しない場合はFalse
    """
    table = get_table('UserStamps')
    
    try:
        response = table.get_item(
            Key={
                'UserId': user_id,
                'StampId': stamp_id
            }
        )
        
        return 'Item' in response
    except Exception as e:
        raise Exception(f"Failed to check stamp existence: {str(e)}")


def add_user_stamp(user_id: str, stamp_id: str, method: str) -> Dict[str, Any]:
    """
    ユーザーにスタンプを追加
    
    注意: この関数は重複チェックを行いません。
    呼び出し側で事前にcheck_stamp_exists()を使用してチェックしてください。
    
    Args:
        user_id (str): ユーザーID（LINE UID）
        stamp_id (str): スタンプID
        method (str): 収集方法（GPS/IMAGE）
    
    Returns:
        Dict: 追加されたスタンプ情報
    
    Raises:
        Exception: DynamoDBへの書き込みに失敗した場合
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
        
        # put_itemを使用してスタンプを追加
        # 既に存在する場合は上書きされるが、呼び出し側でチェック済みであることを前提とする
        table.put_item(Item=item)
        
        return {
            'UserId': user_id,
            'StampId': stamp_id,
            'CollectedAt': current_time,
            'Method': method
        }
    except Exception as e:
        raise Exception(f"Failed to add user stamp: {str(e)}")

