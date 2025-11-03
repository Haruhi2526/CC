#!/usr/bin/env python3
"""
DynamoDBのStampMastersテーブルにスタンプマスターデータを追加するスクリプト

使用方法:
    python3 add_stamp_masters.py

環境変数:
    TABLE_STAMPMASTERS: テーブル名（デフォルト: StampMasters）
    AWS_REGION: AWSリージョン（デフォルト: us-east-1）
"""

import json
import os
import sys
import boto3
from decimal import Decimal
from typing import List, Dict, Any


def decimal_default(obj):
    """Decimal型をfloat/intに変換"""
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError


def convert_dynamodb_format_to_normal(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    DynamoDBネイティブ形式（{"S": "value"}, {"N": "123"}など）を通常のJSON形式に変換
    """
    result = {}
    for key, value in item.items():
        if isinstance(value, dict):
            if 'S' in value:
                # String型
                result[key] = value['S']
            elif 'N' in value:
                # Number型
                num_str = value['N']
                # 整数か小数かを判定
                if '.' in num_str or 'e' in num_str.lower():
                    result[key] = float(num_str)
                else:
                    result[key] = int(num_str)
            elif 'M' in value:
                # Map型（再帰的に変換）
                result[key] = convert_dynamodb_format_to_normal(value['M'])
            else:
                result[key] = value
        else:
            result[key] = value
    return result


def load_stamp_masters(file_path: str) -> List[Dict[str, Any]]:
    """
    JSONファイルからスタンプマスターデータを読み込む
    DynamoDBネイティブ形式と通常のJSON形式の両方に対応
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # DynamoDBネイティブ形式かどうかをチェック（最初のアイテムで判定）
        if data and isinstance(data, list) and len(data) > 0:
            first_item = data[0]
            # DynamoDBネイティブ形式の場合、値が{"S": "..."}などの形式
            is_dynamodb_format = any(
                isinstance(v, dict) and any(k in v for k in ['S', 'N', 'M', 'L', 'BOOL', 'NULL', 'SS', 'NS', 'MS'])
                for v in first_item.values()
            )
            
            if is_dynamodb_format:
                # DynamoDBネイティブ形式を通常形式に変換
                print("DynamoDBネイティブ形式を検出しました。通常形式に変換します...")
                data = [convert_dynamodb_format_to_normal(item) for item in data]
        
        return data
    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"エラー: JSONのパースに失敗しました: {e}")
        sys.exit(1)


def convert_decimal(obj):
    """再帰的にDecimal型に変換"""
    if isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimal(item) for item in obj]
    elif isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, int):
        return obj
    else:
        return obj


def add_stamp_masters_to_dynamodb(table_name: str, stamp_masters: List[Dict[str, Any]], region: str = 'us-east-1'):
    """DynamoDBにスタンプマスターデータを追加"""
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table(table_name)
    
    success_count = 0
    error_count = 0
    
    print(f"テーブル: {table_name}")
    print(f"追加するアイテム数: {len(stamp_masters)}\n")
    
    for stamp in stamp_masters:
        stamp_id = stamp.get('StampId')
        name = stamp.get('Name')
        
        try:
            # Decimal型に変換
            item = convert_decimal(stamp)
            
            # アイテムを追加
            table.put_item(Item=item)
            print(f"✅ {stamp_id}: {name} を追加しました")
            success_count += 1
            
        except Exception as e:
            print(f"❌ {stamp_id}: {name} の追加に失敗しました: {str(e)}")
            error_count += 1
    
    print(f"\n--- 完了 ---")
    print(f"成功: {success_count}件")
    print(f"失敗: {error_count}件")


def main():
    # 設定
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_dir, 'stamp_masters_data.json')
    table_name = os.environ.get('TABLE_STAMPMASTERS', 'StampMasters')
    region = os.environ.get('AWS_REGION', 'us-east-1')
    
    print("=" * 60)
    print("DynamoDB スタンプマスターデータ追加スクリプト")
    print("=" * 60)
    print(f"データファイル: {data_file}")
    print(f"テーブル名: {table_name}")
    print(f"リージョン: {region}\n")
    
    # データを読み込む
    stamp_masters = load_stamp_masters(data_file)
    
    # 確認
    print(f"以下の{len(stamp_masters)}件のスタンプを追加します:")
    for stamp in stamp_masters:
        print(f"  - {stamp['StampId']}: {stamp['Name']}")
    
    response = input("\n続行しますか？ (y/N): ")
    if response.lower() != 'y':
        print("キャンセルしました。")
        sys.exit(0)
    
    print("\n" + "=" * 60)
    
    # DynamoDBに追加
    try:
        add_stamp_masters_to_dynamodb(table_name, stamp_masters, region)
    except Exception as e:
        print(f"\nエラー: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()

