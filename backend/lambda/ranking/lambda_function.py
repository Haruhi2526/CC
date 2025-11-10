import json
import os
import boto3
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
from response_utils import create_response, create_error_response

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
    env_table_name = os.environ.get(f'TABLE_{table_name.upper()}', table_name)
    return dynamodb.Table(env_table_name)


def decimal_to_number(obj):
    """Decimal型をint/floatに変換"""
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    elif isinstance(obj, dict):
        return {k: decimal_to_number(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decimal_to_number(item) for item in obj]
    return obj


def lambda_handler(event, context):
    """
    ランキング関連API
    
    エンドポイント:
    - POST /ranking/calculate - ランキング計算（バッチ処理用）
    - GET /ranking/weekly?period=2025-W45 - 週間ランキング取得
    - GET /ranking/monthly?period=2025-11 - 月間ランキング取得
    - GET /ranking/compare?user_id=XXX&friend_id=YYY - 友達比較
    """
    try:
        # OPTIONSリクエストの処理（CORS preflight）
        if event.get('httpMethod') == 'OPTIONS':
            return create_response(200, {})
        
        method = event.get('httpMethod')
        path = event.get('path', '')
        query_params = event.get('queryStringParameters') or {}
        
        if method == 'POST' and '/ranking/calculate' in path:
            # ランキング計算
            period_type = query_params.get('type', 'weekly')  # weekly or monthly
            return calculate_rankings(period_type)
        elif method == 'GET' and '/ranking/friends/weekly' in path:
            # 友達週間ランキング取得
            user_id = query_params.get('user_id')
            period = query_params.get('period') or get_current_week_period()
            if not user_id:
                return create_error_response(400, 'user_id is required')
            return get_friends_weekly_rankings(user_id, period)
        elif method == 'GET' and '/ranking/friends/monthly' in path:
            # 友達月間ランキング取得
            user_id = query_params.get('user_id')
            period = query_params.get('period') or get_current_month_period()
            if not user_id:
                return create_error_response(400, 'user_id is required')
            return get_friends_monthly_rankings(user_id, period)
        elif method == 'GET' and '/ranking/compare' in path:
            # 友達比較
            user_id = query_params.get('user_id')
            friend_id = query_params.get('friend_id')
            if not user_id or not friend_id:
                return create_error_response(400, 'user_id and friend_id are required')
            return compare_users(user_id, friend_id)
        else:
            return create_error_response(404, 'Not Found')
            
    except Exception as e:
        error_msg = f'Internal Server Error: {str(e)}'
        print(error_msg)
        return create_error_response(500, error_msg)


def calculate_rankings(period_type='weekly'):
    """
    ランキングを計算してDynamoDBに保存
    
    Args:
        period_type (str): 'weekly' または 'monthly'
    
    Returns:
        dict: API Gateway用のレスポンス
    """
    try:
        period = get_current_week_period() if period_type == 'weekly' else get_current_month_period()
        period_key = f'weekly-{period}' if period_type == 'weekly' else f'monthly-{period}'
        
        print(f'ランキング計算開始: period_type={period_type}, period={period}, period_key={period_key}')
        
        # 期間の開始日時を計算
        if period_type == 'weekly':
            # ISO週の開始日（月曜日）を計算
            now = datetime.now()
            year, week, weekday = now.isocalendar()
            # 月曜日を週の開始とする（weekday: 1=月曜日, 7=日曜日）
            days_from_monday = weekday - 1
            start_date = now - timedelta(days=days_from_monday)
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            start_timestamp = int(start_date.timestamp())
        else:
            # 月間ランキング: 今月の1日 00:00:00 を開始日とする
            now = datetime.now()
            start_date = datetime(now.year, now.month, 1, 0, 0, 0, 0)
            start_timestamp = int(start_date.timestamp())
        
        print(f'期間開始タイムスタンプ: {start_timestamp} ({start_date})')
        print(f'現在のタイムスタンプ: {int(datetime.now().timestamp())}')
        
        # UserStampsテーブルから全ユーザーのスタンプ数を集計
        user_stamps_table = get_table('UserStamps')
        users_table = get_table('Users')
        rankings_table = get_table('Rankings')
        
        # ユーザーごとのスタンプ数を集計
        user_stamp_counts = {}
        
        # Scanを使用して全スタンプを取得（実際の運用では効率化が必要）
        print('UserStampsテーブルからスタンプデータを取得中...')
        response = user_stamps_table.scan()
        items = response.get('Items', [])
        print(f'取得したスタンプデータ件数: {len(items)}')
        
        period_stamp_count = 0
        for item in items:
            user_id = item.get('UserId')
            collected_at = int(item.get('CollectedAt', 0))
            
            # 期間内のスタンプのみをカウント
            if collected_at >= start_timestamp:
                period_stamp_count += 1
                if user_id not in user_stamp_counts:
                    user_stamp_counts[user_id] = 0
                user_stamp_counts[user_id] += 1
                print(f'期間内スタンプ: user_id={user_id}, collected_at={collected_at}')
        
        print(f'期間内のスタンプ数: {period_stamp_count}')
        print(f'ユーザー数: {len(user_stamp_counts)}')
        print(f'ユーザーごとのスタンプ数: {user_stamp_counts}')
        
        # スタンプ数でソート
        sorted_users = sorted(user_stamp_counts.items(), key=lambda x: x[1], reverse=True)
        print(f'ソート後のユーザー数: {len(sorted_users)}')
        
        # ランキングデータを保存
        rank = 1
        rankings_to_save = []
        
        for user_id, stamp_count in sorted_users:
            # ユーザー情報を取得（表示名用）
            try:
                user = users_table.get_item(Key={'UserId': user_id})
                display_name = user.get('Item', {}).get('DisplayName', 'Unknown')
            except:
                display_name = 'Unknown'
            
            rankings_to_save.append({
                'Period': period_key,
                'Rank': rank,
                'UserId': user_id,
                'StampCount': stamp_count,
                'DisplayName': display_name,
                'UpdatedAt': int(datetime.now().timestamp())
            })
            rank += 1
        
        # 既存のランキングを削除（バッチ削除）
        if rankings_to_save:
            # 既存データを削除
            try:
                existing = rankings_table.query(
                    KeyConditionExpression='Period = :period',
                    ExpressionAttributeValues={':period': period_key}
                )
                for item in existing.get('Items', []):
                    rankings_table.delete_item(
                        Key={
                            'Period': period_key,
                            'Rank': item['Rank']
                        }
                    )
            except Exception as e:
                print(f'Warning: Failed to delete existing rankings: {str(e)}')
            
            # 新しいランキングを保存
            for ranking in rankings_to_save:
                rankings_table.put_item(Item=ranking)
        
        return create_response(200, {
            'ok': True,
            'period': period,
            'period_type': period_type,
            'rankings_count': len(rankings_to_save)
        })
        
    except Exception as e:
        error_msg = f'Failed to calculate rankings: {str(e)}'
        print(error_msg)
        return create_error_response(500, error_msg)


def get_weekly_rankings(period: str):
    """
    週間ランキングを取得
    
    Args:
        period (str): 期間文字列（例: "2025-W45"）
    
    Returns:
        dict: API Gateway用のレスポンス
    """
    try:
        rankings_table = get_table('Rankings')
        period_key = f'weekly-{period}'
        
        response = rankings_table.query(
            KeyConditionExpression='Period = :period',
            ExpressionAttributeValues={
                ':period': period_key
            },
            Limit=100,
            ScanIndexForward=True  # 昇順（ランク1から）
        )
        
        rankings = []
        for item in response.get('Items', []):
            rankings.append({
                'rank': int(item.get('Rank', 0)),
                'user_id': item.get('UserId', ''),
                'stamp_count': int(item.get('StampCount', 0)),
                'display_name': item.get('DisplayName', 'Unknown')
            })
        
        return create_response(200, {
            'ok': True,
            'period': period,
            'period_type': 'weekly',
            'rankings': rankings
        })
        
    except Exception as e:
        error_msg = f'Failed to get weekly rankings: {str(e)}'
        print(error_msg)
        return create_error_response(500, error_msg)


def get_monthly_rankings(period: str):
    """
    月間ランキングを取得
    
    Args:
        period (str): 期間文字列（例: "2025-11"）
    
    Returns:
        dict: API Gateway用のレスポンス
    """
    try:
        rankings_table = get_table('Rankings')
        period_key = f'monthly-{period}'
        
        response = rankings_table.query(
            KeyConditionExpression='Period = :period',
            ExpressionAttributeValues={
                ':period': period_key
            },
            Limit=100,
            ScanIndexForward=True  # 昇順（ランク1から）
        )
        
        rankings = []
        for item in response.get('Items', []):
            rankings.append({
                'rank': int(item.get('Rank', 0)),
                'user_id': item.get('UserId', ''),
                'stamp_count': int(item.get('StampCount', 0)),
                'display_name': item.get('DisplayName', 'Unknown')
            })
        
        return create_response(200, {
            'ok': True,
            'period': period,
            'period_type': 'monthly',
            'rankings': rankings
        })
        
    except Exception as e:
        error_msg = f'Failed to get monthly rankings: {str(e)}'
        print(error_msg)
        return create_error_response(500, error_msg)


def compare_users(user_id: str, friend_id: str):
    """
    2人のユーザーを比較
    
    Args:
        user_id (str): ユーザーID
        friend_id (str): 友達のユーザーID
    
    Returns:
        dict: API Gateway用のレスポンス
    """
    try:
        user_stamps_table = get_table('UserStamps')
        users_table = get_table('Users')
        
        # 両ユーザーのスタンプ数を取得
        def get_stamp_count(uid):
            response = user_stamps_table.query(
                KeyConditionExpression='UserId = :user_id',
                ExpressionAttributeValues={':user_id': uid}
            )
            return len(response.get('Items', []))
        
        def get_user_info(uid):
            try:
                response = users_table.get_item(Key={'UserId': uid})
                item = response.get('Item', {})
                return {
                    'user_id': uid,
                    'display_name': item.get('DisplayName', 'Unknown'),
                    'stamp_count': get_stamp_count(uid)
                }
            except:
                return {
                    'user_id': uid,
                    'display_name': 'Unknown',
                    'stamp_count': 0
                }
        
        user_info = get_user_info(user_id)
        friend_info = get_user_info(friend_id)
        
        # ランク差を計算（簡易版）
        rank_diff = user_info['stamp_count'] - friend_info['stamp_count']
        
        return create_response(200, {
            'ok': True,
            'user': user_info,
            'friend': friend_info,
            'rank_diff': rank_diff,
            'user_is_higher': rank_diff > 0
        })
        
    except Exception as e:
        error_msg = f'Failed to compare users: {str(e)}'
        print(error_msg)
        return create_error_response(500, error_msg)


def get_current_week_period():
    """
    現在の週の期間文字列を返す（例: "2025-W45"）
    
    Returns:
        str: 期間文字列
    """
    now = datetime.now()
    year, week, _ = now.isocalendar()
    return f"{year}-W{week:02d}"


def get_current_month_period():
    """
    現在の月の期間文字列を返す（例: "2025-11"）
    
    Returns:
        str: 期間文字列
    """
    now = datetime.now()
    return f"{now.year}-{now.month:02d}"


def get_friends_weekly_rankings(user_id: str, period: str):
    """
    友達の週間ランキングを取得
    
    Args:
        user_id (str): ユーザーID
        period (str): 期間文字列（例: "2025-W45"）
    
    Returns:
        dict: API Gateway用のレスポンス
    """
    try:
        friends_table = get_table('Friends')
        rankings_table = get_table('Rankings')
        users_table = get_table('Users')
        
        # 友達リストを取得
        friends_response = friends_table.query(
            KeyConditionExpression='UserId = :user_id',
            ExpressionAttributeValues={':user_id': user_id}
        )
        
        friends_items = friends_response.get('Items', [])
        print(f'友達リスト取得: user_id={user_id}, 友達数={len(friends_items)}')
        
        # Statusが'active'の友達のみをフィルタリング
        friend_ids = []
        for item in friends_items:
            status = item.get('Status', 'active')
            friend_id = item.get('FriendId')
            print(f'友達: {friend_id}, Status: {status}')
            if status == 'active':
                friend_ids.append(friend_id)
        
        print(f'アクティブな友達数: {len(friend_ids)}')
        
        # 自分自身もランキングに含める
        user_ids_to_include = friend_ids.copy()
        if user_id not in user_ids_to_include:
            user_ids_to_include.append(user_id)
            print(f'自分自身を追加: {user_id}')
        
        print(f'ランキングに含めるユーザー数: {len(user_ids_to_include)} (友達: {len(friend_ids)}, 自分: 1)')
        
        if not user_ids_to_include:
            print('ランキングに含めるユーザーがありません')
            return create_response(200, {
                'ok': True,
                'period': period,
                'period_type': 'weekly',
                'rankings': []
            })
        
        # 全体ランキングから友達と自分自身をフィルタリング
        period_key = f'weekly-{period}'
        print(f'友達ランキング取得: user_id={user_id}, period={period}, period_key={period_key}')
        print(f'ランキングに含めるIDリスト: {user_ids_to_include}')
        
        rankings_response = rankings_table.query(
            KeyConditionExpression='Period = :period_val',
            ExpressionAttributeValues={':period_val': period_key},
            ScanIndexForward=True
        )
        
        all_rankings = rankings_response.get('Items', [])
        print(f'全体ランキング件数: {len(all_rankings)}')
        
        # 友達と自分自身をフィルタリング
        friend_rankings = []
        for item in all_rankings:
            item_user_id = item.get('UserId')
            if item_user_id in user_ids_to_include:
                is_self = (item_user_id == user_id)
                friend_rankings.append({
                    'rank': int(item.get('Rank')),
                    'user_id': item_user_id,
                    'stamp_count': int(item.get('StampCount', 0)),
                    'display_name': item.get('DisplayName', 'Unknown'),
                    'is_self': is_self  # 自分自身かどうかのフラグ
                })
                print(f'ランキング追加: {item_user_id} {"(自分)" if is_self else "(友達)"}, rank={item.get("Rank")}, stamps={item.get("StampCount")}')
        
        print(f'友達ランキング件数: {len(friend_rankings)}')
        
        # ランクを再計算（1位から）
        for i, ranking in enumerate(friend_rankings):
            ranking['rank'] = i + 1
        
        return create_response(200, {
            'ok': True,
            'period': period,
            'period_type': 'weekly',
            'rankings': friend_rankings
        })
        
    except Exception as e:
        error_msg = f'Failed to get friends weekly rankings: {str(e)}'
        print(error_msg)
        return create_error_response(500, error_msg)


def get_friends_monthly_rankings(user_id: str, period: str):
    """
    友達の月間ランキングを取得
    
    Args:
        user_id (str): ユーザーID
        period (str): 期間文字列（例: "2025-11"）
    
    Returns:
        dict: API Gateway用のレスポンス
    """
    try:
        friends_table = get_table('Friends')
        rankings_table = get_table('Rankings')
        users_table = get_table('Users')
        
        # 友達リストを取得
        friends_response = friends_table.query(
            KeyConditionExpression='UserId = :user_id',
            ExpressionAttributeValues={':user_id': user_id}
        )
        
        friends_items = friends_response.get('Items', [])
        print(f'友達リスト取得: user_id={user_id}, 友達数={len(friends_items)}')
        
        # Statusが'active'の友達のみをフィルタリング
        friend_ids = []
        for item in friends_items:
            status = item.get('Status', 'active')
            friend_id = item.get('FriendId')
            print(f'友達: {friend_id}, Status: {status}')
            if status == 'active':
                friend_ids.append(friend_id)
        
        print(f'アクティブな友達数: {len(friend_ids)}')
        
        # 自分自身もランキングに含める
        user_ids_to_include = friend_ids.copy()
        if user_id not in user_ids_to_include:
            user_ids_to_include.append(user_id)
            print(f'自分自身を追加: {user_id}')
        
        print(f'ランキングに含めるユーザー数: {len(user_ids_to_include)} (友達: {len(friend_ids)}, 自分: 1)')
        
        if not user_ids_to_include:
            print('ランキングに含めるユーザーがありません')
            return create_response(200, {
                'ok': True,
                'period': period,
                'period_type': 'monthly',
                'rankings': []
            })
        
        # 全体ランキングから友達と自分自身をフィルタリング
        period_key = f'monthly-{period}'
        print(f'友達ランキング取得: user_id={user_id}, period={period}, period_key={period_key}')
        print(f'ランキングに含めるIDリスト: {user_ids_to_include}')
        
        rankings_response = rankings_table.query(
            KeyConditionExpression='Period = :period_val',
            ExpressionAttributeValues={':period_val': period_key},
            ScanIndexForward=True
        )
        
        all_rankings = rankings_response.get('Items', [])
        print(f'全体ランキング件数: {len(all_rankings)}')
        
        # 友達と自分自身をフィルタリング
        friend_rankings = []
        for item in all_rankings:
            item_user_id = item.get('UserId')
            if item_user_id in user_ids_to_include:
                is_self = (item_user_id == user_id)
                friend_rankings.append({
                    'rank': int(item.get('Rank')),
                    'user_id': item_user_id,
                    'stamp_count': int(item.get('StampCount', 0)),
                    'display_name': item.get('DisplayName', 'Unknown'),
                    'is_self': is_self  # 自分自身かどうかのフラグ
                })
                print(f'ランキング追加: {item_user_id} {"(自分)" if is_self else "(友達)"}, rank={item.get("Rank")}, stamps={item.get("StampCount")}')
        
        # ランクを再計算（1位から）
        for i, ranking in enumerate(friend_rankings):
            ranking['rank'] = i + 1
        
        return create_response(200, {
            'ok': True,
            'period': period,
            'period_type': 'monthly',
            'rankings': friend_rankings
        })
        
    except Exception as e:
        error_msg = f'Failed to get friends monthly rankings: {str(e)}'
        print(error_msg)
        return create_error_response(500, error_msg)

