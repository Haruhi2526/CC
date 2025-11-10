import json
import boto3
import os
import uuid
from response_utils import create_response, create_error_response

# S3クライアント
s3_client = boto3.client('s3')

# 環境変数から取得
S3_BUCKET = os.environ.get('S3_BUCKET')
S3_PREFIX = os.environ.get('S3_PREFIX', 'users/')  # デフォルト: users/
PRESIGNED_URL_EXPIRATION = int(os.environ.get('PRESIGNED_URL_EXPIRATION', '3600'))  # デフォルト: 1時間


def lambda_handler(event, context):
    """
    S3アップロード用のPresigned URLを生成
    POST /s3/upload-url
    
    リクエストボディ:
    {
        "user_id": "USER_ID",
        "file_name": "image.jpg" (オプション)
    }
    
    レスポンス（成功時）:
    {
        "ok": true,
        "upload_url": "https://...",
        "fields": {...},
        "key": "users/USER_ID/images/xxx.jpg"
    }
    """
    try:
        # OPTIONSリクエストの処理（CORS preflight）
        if event.get('httpMethod') == 'OPTIONS':
            return create_response(200, {})
        
        # リクエストボディの取得
        body = json.loads(event.get('body', '{}'))
        
        # バリデーション
        user_id = body.get('user_id')
        if not user_id:
            return create_error_response(400, 'user_id is required', 'VALIDATION_ERROR')
        
        # S3バケットの確認
        if not S3_BUCKET:
            return create_error_response(500, 'S3_BUCKET environment variable is not set', 'CONFIG_ERROR')
        
        # ファイル名の生成
        file_name = body.get('file_name')
        if not file_name:
            # ファイル名が指定されていない場合、UUIDを生成
            file_name = f"{uuid.uuid4()}.jpg"
        
        # ファイル拡張子の確認
        if not file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            return create_error_response(400, 'Invalid file type. Only image files are allowed.', 'INVALID_FILE_TYPE')
        
        # S3キーの生成（users/{user_id}/images/{file_name}）
        s3_key = f"{S3_PREFIX.rstrip('/')}/{user_id}/images/{file_name}"
        
        # ファイルタイプに応じてContent-Typeを決定
        file_ext = file_name.lower().split('.')[-1]
        content_type_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif'
        }
        content_type = content_type_map.get(file_ext, 'image/jpeg')
        
        # Presigned POST URLを生成
        try:
            presigned_post = s3_client.generate_presigned_post(
                Bucket=S3_BUCKET,
                Key=s3_key,
                Fields={
                    'Content-Type': content_type
                },
                Conditions=[
                    {'Content-Type': content_type},
                    ['content-length-range', 1, 10485760]  # 1バイト〜10MB
                ],
                ExpiresIn=PRESIGNED_URL_EXPIRATION
            )
        except Exception as e:
            return create_error_response(500, f'Failed to generate presigned URL: {str(e)}', 'S3_ERROR')
        
        # レスポンスの作成
        response_data = {
            'ok': True,
            'upload_url': presigned_post['url'],
            'fields': presigned_post['fields'],
            'key': s3_key,
            'bucket': S3_BUCKET
        }
        
        return create_response(200, response_data)
        
    except json.JSONDecodeError:
        return create_error_response(400, 'Invalid JSON format', 'INVALID_JSON')
    except Exception as e:
        return create_error_response(500, f'Internal Server Error: {str(e)}', 'INTERNAL_ERROR')

