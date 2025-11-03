import json
import math
from dynamodb_utils import get_stamp_master
from response_utils import create_response, create_error_response


def calculate_distance_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Haversine公式を使用して2点間の距離を計算（単位：メートル）
    
    Args:
        lat1 (float): 現在地の緯度
        lon1 (float): 現在地の経度
        lat2 (float): 目標地点の緯度
        lon2 (float): 目標地点の経度
    
    Returns:
        float: 距離（メートル）
    """
    # 地球の半径（メートル）
    R = 6371000
    
    # 度をラジアンに変換
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    # Haversine公式
    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def validate_gps_request(body: dict) -> tuple[bool, str, dict]:
    """
    GPS検証リクエストのバリデーション
    
    Args:
        body (dict): リクエストボディ
    
    Returns:
        tuple: (is_valid, error_message, validated_data)
    """
    user_id = body.get('userId') or body.get('user_id')
    spot_id = body.get('spotId') or body.get('stamp_id') or body.get('stampId')
    lat = body.get('lat') or body.get('latitude')
    lon = body.get('lon') or body.get('longitude')
    accuracy = body.get('accuracy')
    
    if not user_id:
        return False, 'userId is required', {}
    
    if not spot_id:
        return False, 'spotId is required', {}
    
    if lat is None:
        return False, 'lat (latitude) is required', {}
    
    if lon is None:
        return False, 'lon (longitude) is required', {}
    
    # 緯度・経度の範囲チェック
    if not (-90 <= lat <= 90):
        return False, 'lat must be between -90 and 90', {}
    
    if not (-180 <= lon <= 180):
        return False, 'lon must be between -180 and 180', {}
    
    # accuracyはオプション（デフォルトで精度を考慮）
    if accuracy is None:
        accuracy = 0  # デフォルト値
    
    return True, '', {
        'user_id': user_id,
        'spot_id': spot_id,
        'lat': float(lat),
        'lon': float(lon),
        'accuracy': float(accuracy) if accuracy else 0
    }


def lambda_handler(event, context):
    """
    GPS位置情報を検証する
    POST /gps/verify または POST /gps/check
    
    リクエストボディ:
    {
        "userId": "USER_ID",
        "spotId": "STAMP_ID",
        "lat": 35.6812,
        "lon": 139.7671,
        "accuracy": 10.5  // オプション: 端末の精度（メートル）
    }
    
    レスポンス（成功時）:
    {
        "ok": true,
        "spotId": "STAMP_ID",
        "name": "駅前広場",
        "lat": 35.6812,
        "lon": 139.7671,
        "distanceM": 45.2,
        "within": true,
        "radiusM": 100
    }
    """
    try:
        # OPTIONSリクエストの処理（CORS preflight）
        if event.get('httpMethod') == 'OPTIONS':
            return create_response(200, {})
        
        # リクエストボディの取得
        body = json.loads(event.get('body', '{}'))
        
        # バリデーション
        is_valid, error_message, validated_data = validate_gps_request(body)
        if not is_valid:
            return create_error_response(400, error_message)
        
        user_id = validated_data['user_id']
        spot_id = validated_data['spot_id']
        user_lat = validated_data['lat']
        user_lon = validated_data['lon']
        accuracy = validated_data['accuracy']
        
        # スタンプマスタ情報を取得
        try:
            stamp_master = get_stamp_master(spot_id)
            if not stamp_master:
                return create_error_response(404, f'Stamp not found: {spot_id}', 'STAMP_NOT_FOUND')
        except Exception as e:
            return create_error_response(500, f'Failed to get stamp master: {str(e)}')
        
        # スタンプタイプのチェック（GPSタイプのみ許可）
        stamp_type = stamp_master.get('Type', '').upper()
        if stamp_type and stamp_type != 'GPS':
            return create_error_response(400, 
                f'This stamp is not a GPS type stamp. Type: {stamp_type}', 
                'STAMP_TYPE_MISMATCH')
        
        # Location情報を取得
        location = stamp_master.get('Location')
        if not location:
            return create_error_response(400, 
                'Location information not found in stamp master', 
                'LOCATION_NOT_FOUND')
        
        # スタンプの座標と半径を取得
        stamp_lat = location.get('lat') or location.get('latitude')
        stamp_lon = location.get('lon') or location.get('longitude')
        radius_m = location.get('radius') or location.get('radiusM') or 100  # デフォルト100m
        
        if stamp_lat is None or stamp_lon is None:
            return create_error_response(400, 
                'Invalid location data in stamp master', 
                'INVALID_LOCATION')
        
        # 距離を計算
        distance_m = calculate_distance_haversine(
            user_lat, user_lon,
            float(stamp_lat), float(stamp_lon)
        )
        
        # 精度と半径を考慮して判定
        # 精度分のマージンを追加（精度が大きいほど範囲を広げる）
        effective_radius = max(float(radius_m), accuracy) if accuracy > 0 else float(radius_m)
        within = distance_m <= effective_radius
        
        # レスポンスの作成
        response_data = {
            'ok': True,
            'spotId': spot_id,
            'name': stamp_master.get('Name', ''),
            'lat': user_lat,
            'lon': user_lon,
            'distanceM': round(distance_m, 2),
            'within': within,
            'radiusM': float(radius_m),
            'accuracy': accuracy
        }
        
        return create_response(200, response_data)
        
    except json.JSONDecodeError:
        return create_error_response(400, 'Invalid JSON format')
    except Exception as e:
        return create_error_response(500, f'Internal Server Error: {str(e)}')

