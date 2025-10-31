# 担当者D - AI・位置情報処理

## 担当範囲
- GPS位置情報検証ロジック
- Amazon Rekognition実装
- 画像認識処理
- カスタムラベル訓練
- 地理的計算アルゴリズム

## 作業内容

### Phase 1: 準備・学習（Week 1-2）
- [ ] Rekognition SDKの学習
- [ ] テスト画像の準備
- [ ] Haversine距離計算の実装

### Phase 2: GPS検証システム（Week 3）
- [ ] **位置情報検証Lambda関数** (`lambda/gps-verify`)
  - Haversine公式による距離計算
  - 半径100m以内の判定
  - 複数地点の同時判定対応
  - タイムスタンプ検証（不正防止）

- [ ] **距離計算アルゴリズム**
  - 高精度な距離計算
  - ケーススタディ対応（建物内補正等）
  - エラーハンドリング

### Phase 3: 画像認識システム（Week 3-4）
- [ ] **画像アップロードLambda関数** (`lambda/image-upload`)
  - S3への画像アップロード
  - 画像形式・サイズ検証
  - 一意なファイル名生成

- [ ] **Rekognition連携Lambda関数** (`lambda/image-recognize`)
  - Rekognition Custom Labels呼び出し
  - デフォルトラベル検出の実装
  - 信頼度スコアの判定
  - 閾値設定

- [ ] **カスタムラベル訓練**
  - 訓練用データセット準備
  - ラベル設定
  - モデル訓練と評価
  - 本番環境デプロイ

### Phase 4: 不正防止（Week 4）
- [ ] メタデータ検証（EXIF情報チェック）
- [ ] 画像類似度チェック（同一画像の重複提出防止）
- [ ] GPS位置情報と撮影位置の整合性チェック
- [ ] レート制限実装

### Phase 5: テスト・調整（Week 7）
- [ ] 画像認識精度テスト
- [ ] GPS精度テスト
- [ ] 不正検知テスト
- [ ] パフォーマンス最適化

## 使用技術
- Python 3.9+
- boto3 (AWS SDK)
- Amazon Rekognition Custom Labels
- PIL/Pillow (画像処理)
- NumPy (数値計算)

## 担当ファイル
```
ai-processing/
├── gps-verification/
│   ├── lambda_function.py
│   ├── haversine.py
│   ├── geoutils.py
│   └── tests/
├── image-recognition/
│   ├── lambda_function.py
│   ├── rekognition_client.py
│   ├── image_validator.py
│   └── tests/
├── algorithms/
│   └── distance_calculator.py
└── training-data/
    ├── images/
    └── annotations/
```

## 実装する距離計算アルゴリズム

```python
import math

def calculate_distance_haversine(lat1, lon1, lat2, lon2):
    """
    Haversine公式を使用して2点間の距離を計算（単位：メートル）
    
    Parameters:
    lat1, lon1: 現在地の緯度・経度
    lat2, lon2: 目標地点の緯度・経度
    
    Returns:
    float: 距離（メートル）
    """
    R = 6371000  # 地球の半径（メートル）
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi/2)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def is_within_radius(current_lat, current_lon, target_lat, target_lon, radius_meters):
    """
    現在地が目標地点の指定半径内にあるか判定
    
    Returns:
    tuple: (bool: 判定結果, float: 距離)
    """
    distance = calculate_distance_haversine(
        current_lat, current_lon, target_lat, target_lon
    )
    return distance <= radius_meters, distance
```

## Rekognition実装例

```python
import boto3

def detect_custom_labels(image_bytes, project_arn, model_version):
    """
    Custom Labelsを使用して画像内部の物体を検出
    
    Returns:
    dict: 検出結果
    """
    client = boto3.client('rekognition')
    
    response = client.detect_custom_labels(
        Image={'Bytes': image_bytes},
        ProjectVersionArn=f"{project_arn}/{model_version}",
        MinConfidence=70.0
    )
    
    return response

def validate_stamp_object(labels, expected_label):
    """
    スタンプ対象物体が正しく検出されたか判定
    
    Returns:
    tuple: (bool: 判定結果, float: 信頼度)
    """
    for label in labels['CustomLabels']:
        if label['Name'] == expected_label and label['Confidence'] >= 70.0:
            return True, label['Confidence']
    
    return False, 0.0
```

## 連携先
- **担当者A**: 画像フォーマット仕様の確認、GPS精度の説明
- **担当者B**: 検証結果の受け渡し仕様
- **担当者C**: S3バケット構造、Rekognition権限設定

## 成果物
- GPS検証Lambda関数
- 画像認識Lambda関数
- カスタムラベルモデル
- 距離計算ユーティリティ
- テストデータセット
- 精度レポート

## 注意事項
- プライバシー: 画像は一時的保存、自動削除設定
- 精度: 閾値は実際の使用データで調整
- パフォーマンス: Rekognition料金に注意


