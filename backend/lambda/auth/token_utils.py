import hmac
import hashlib
import secrets
import time
import json
import os
from typing import Dict, Optional


def get_secret_key() -> str:
    """
    環境変数からシークレットキーを取得（存在しない場合はデフォルト値）
    本番環境では必ず環境変数で設定すること
    """
    return os.environ.get('TOKEN_SECRET_KEY', 'default-secret-key-change-in-production')


def generate_session_token(user_id: str, display_name: str) -> str:
    """
    セッショントークンを生成（簡易版）
    
    HMAC-SHA256を使用してトークンを生成します。
    本番環境ではJWTなどの標準的なトークン形式の使用を推奨します。
    
    Args:
        user_id (str): ユーザーID（LINE UID）
        display_name (str): 表示名
    
    Returns:
        str: セッショントークン
    """
    secret_key = get_secret_key()
    current_time = int(time.time())
    
    # トークンデータの作成
    token_data = {
        'user_id': user_id,
        'display_name': display_name,
        'timestamp': current_time,
        'nonce': secrets.token_hex(16)  # ランダムな文字列を追加
    }
    
    # JSON文字列に変換
    token_json = json.dumps(token_data, sort_keys=True)
    
    # HMAC-SHA256で署名を生成
    signature = hmac.new(
        secret_key.encode('utf-8'),
        token_json.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # トークンと署名を結合（簡易形式）
    # 本番ではBase64エンコードなどを使用することを推奨
    token_string = f"{token_json}|{signature}"
    
    return token_string


def verify_session_token(token: str) -> Optional[Dict]:
    """
    セッショントークンを検証
    
    Args:
        token (str): 検証するトークン
    
    Returns:
        Optional[Dict]: 検証成功時はトークンデータ、失敗時はNone
    """
    try:
        # トークンと署名を分割
        if '|' not in token:
            return None
        
        token_json, signature = token.rsplit('|', 1)
        
        # 署名を再計算
        secret_key = get_secret_key()
        expected_signature = hmac.new(
            secret_key.encode('utf-8'),
            token_json.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # 署名を比較（タイミング攻撃対策としてhmac.compare_digestを使用）
        if not hmac.compare_digest(signature, expected_signature):
            return None
        
        # トークンデータをパース
        token_data = json.loads(token_json)
        
        # タイムスタンプの検証（オプション：24時間有効とする）
        timestamp = token_data.get('timestamp', 0)
        current_time = int(time.time())
        if current_time - timestamp > 86400:  # 24時間 = 86400秒
            return None
        
        return token_data
    
    except (ValueError, json.JSONDecodeError, KeyError):
        return None
