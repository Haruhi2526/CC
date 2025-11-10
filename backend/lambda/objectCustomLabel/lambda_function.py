import json
import boto3
import os
import time
from dynamodb_utils import find_stamp_by_image_label, check_stamp_exists, add_user_stamp, get_stamp_master

# Rekognitionクライアント
rekognition = boto3.client('rekognition')

# Lambdaクライアント（通知送信用）
lambda_client = boto3.client('lambda')

# 環境変数からモデルARNを取得
MODEL_ARN = os.environ['MODEL_ARN']


def extract_user_id_from_s3_key(key: str) -> str:
    """
    S3キーからユーザーIDを抽出
    
    想定されるキー形式:
    - users/{userId}/images/{filename}
    - {userId}/images/{filename}
    - {userId}/{filename}
    
    Args:
        key (str): S3オブジェクトキー
    
    Returns:
        str: ユーザーID（抽出できない場合はNone）
    """
    parts = key.split('/')
    
    # users/{userId}/images/{filename} の形式
    if len(parts) >= 3 and parts[0] == 'users':
        return parts[1]
    
    # {userId}/images/{filename} または {userId}/{filename} の形式
    if len(parts) >= 2:
        return parts[0]
    
    return None


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


def award_stamp_for_label(user_id: str, label_name: str) -> dict:
    """
    検出されたラベルに基づいてスタンプを付与
    
    Args:
        user_id (str): ユーザーID
        label_name (str): 検出されたラベル名
    
    Returns:
        dict: スタンプ付与結果
    """
    try:
        # ImageLabelでスタンプマスターを検索
        stamp_master = find_stamp_by_image_label(label_name)
        
        if not stamp_master:
            return {
                'awarded': False,
                'reason': f'No stamp found for label: {label_name}'
            }
        
        stamp_id = stamp_master.get('StampId')
        
        # スタンプマスタの有効期間チェック
        current_time = int(time.time())
        valid_from = stamp_master.get('ValidFrom')
        valid_to = stamp_master.get('ValidTo')
        
        if valid_from and current_time < valid_from:
            return {
                'awarded': False,
                'reason': f'Stamp is not yet valid. Valid from: {valid_from}'
            }
        
        if valid_to and current_time > valid_to:
            return {
                'awarded': False,
                'reason': f'Stamp has expired. Valid until: {valid_to}'
            }
        
        # スタンプタイプのチェック
        # Typeが設定されている場合、GPS/IMAGEのどちらでも許可（両方の方法で取得可能にする）
        stamp_type = stamp_master.get('Type', '').upper()
        if stamp_type and stamp_type not in ['GPS', 'IMAGE']:
            # TypeがGPS/IMAGE以外の場合はエラー
            return {
                'awarded': False,
                'reason': f'Invalid stamp type: {stamp_type}'
            }
        # Typeが設定されていない場合、またはGPS/IMAGEの場合は許可
        
        # 重複チェック
        if check_stamp_exists(user_id, stamp_id):
            return {
                'awarded': False,
                'reason': f'User already has this stamp: {stamp_id}'
            }
        
        # スタンプを追加
        result = add_user_stamp(user_id, stamp_id, 'IMAGE')
        
        # スタンプ授与成功時に通知を送信（非同期）
        send_notification_async(user_id, stamp_id, stamp_master)
        
        return {
            'awarded': True,
            'stamp_id': stamp_id,
            'stamp_name': stamp_master.get('Name'),
            'collected_at': result['CollectedAt']
        }
        
    except Exception as e:
        return {
            'awarded': False,
            'reason': f'Failed to award stamp: {str(e)}'
        }


def lambda_handler(event, context):
    # S3イベント情報を取得
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']

    print(f"Received image: s3://{bucket}/{key}")

    # S3キーからユーザーIDを抽出
    user_id = extract_user_id_from_s3_key(key)
    
    if not user_id:
        print(f"Warning: Could not extract user_id from S3 key: {key}")
        # ユーザーIDが取得できない場合でも画像認識は実行する

    # Rekognition Custom Labelsで推論
    response = rekognition.detect_custom_labels(
        ProjectVersionArn=MODEL_ARN,
        Image={'S3Object': {'Bucket': bucket, 'Name': key}},
        MinConfidence=70  # 信頼度70%以上のものを取得
    )

    labels = response.get('CustomLabels', [])

    if not labels:
        result = {"message": "No labels detected.", "image": key}
    else:
        # ラベル名だけを抽出
        detected = [
            {"Name": lbl["Name"], "Confidence": round(lbl["Confidence"], 2)}
            for lbl in labels
        ]
        result = {
            "image": key,
            "detected_labels": detected
        }
        
        # ユーザーIDが取得できた場合、検出されたラベルに基づいてスタンプを付与
        if user_id:
            awarded_stamps = []
            for label in detected:
                label_name = label["Name"]
                award_result = award_stamp_for_label(user_id, label_name)
                
                if award_result.get('awarded'):
                    awarded_stamps.append({
                        'stamp_id': award_result.get('stamp_id'),
                        'stamp_name': award_result.get('stamp_name'),
                        'label': label_name,
                        'collected_at': award_result.get('collected_at')
                    })
                    print(f"Stamp awarded: {award_result.get('stamp_id')} for label: {label_name}")
                else:
                    print(f"Stamp not awarded for label {label_name}: {award_result.get('reason')}")
            
            if awarded_stamps:
                result['awarded_stamps'] = awarded_stamps
                result['message'] = f"Successfully awarded {len(awarded_stamps)} stamp(s)"
            else:
                result['message'] = "Labels detected but no stamps awarded"
        else:
            result['message'] = "Labels detected but user_id not found in S3 key"

    # CloudWatchログに出力
    print("Detection result:", json.dumps(result, ensure_ascii=False, indent=2))

    return {
        "statusCode": 200,
        "body": json.dumps(result, ensure_ascii=False)
    }
