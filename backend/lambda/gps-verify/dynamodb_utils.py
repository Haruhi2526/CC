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

