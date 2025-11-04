# API仕様書

**最終更新**: 2025年1月（GPS検証エンドポイント追加）  
**バージョン**: 1.1

---

## 目次

1. [概要](#概要)
2. [ベースURL](#ベースurl)
3. [認証方式](#認証方式)
4. [共通事項](#共通事項)
5. [エンドポイント一覧](#エンドポイント一覧)
   - [1. LINE認証](#1-line認証)
   - [2. スタンプ一覧取得](#2-スタンプ一覧取得)
   - [3. スタンプ授与](#3-スタンプ授与)
   - [4. GPS位置情報検証](#4-gps位置情報検証)
6. [エラーレスポンス](#エラーレスポンス)
7. [ステータスコード一覧](#ステータスコード一覧)

---

## 概要

本APIは、スタンプラリーLIFFアプリのバックエンドとして提供されるRESTful APIです。AWS API GatewayとLambda関数で構築されており、DynamoDBをデータストアとして使用します。

### 主要機能

- LINE IDトークンによる認証
- ユーザー情報の管理
- スタンプの取得・授与
- セッション管理

---

## ベースURL

```
https://{api-id}.execute-api.{region}.amazonaws.com/dev
```

**例**: `https://2bm71jvfs6.execute-api.us-east-1.amazonaws.com/dev`

---

## 認証方式

### 認証フロー

1. LIFFアプリからLINE IDトークンを取得
2. `/auth/verify`エンドポイントでIDトークンを送信
3. サーバーがIDトークンを検証し、セッショントークンを生成
4. 以降のAPIリクエストにはセッショントークンを`Authorization`ヘッダーに含める

### セッショントークン

- **形式**: `Bearer {token}`
- **ヘッダー名**: `Authorization`
- **有効期限**: 実装依存（現時点では無期限）

**例**:
```http
Authorization: Bearer {"display_name": "ユーザー名", "nonce": "...", "timestamp": 1234567890, "user_id": "..."}|{signature}
```

---

## 共通事項

### リクエストヘッダー

| ヘッダー名 | 必須 | 説明 |
|-----------|------|------|
| `Content-Type` | あり（POST/PUT） | `application/json` |
| `Authorization` | あり（認証が必要なエンドポイント） | `Bearer {session_token}` |

### レスポンス形式

すべてのレスポンスはJSON形式です。

#### 成功レスポンス

```json
{
  "ok": true,
  "data": { ... }
}
```

#### エラーレスポンス

```json
{
  "ok": false,
  "error": "Error",
  "message": "エラーメッセージ"
}
```

### CORS対応

すべてのエンドポイントでCORS（Cross-Origin Resource Sharing）に対応しています。

#### CORSヘッダー

- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Headers: Content-Type,Authorization`
- `Access-Control-Allow-Methods: GET,POST,OPTIONS`

#### プリフライトリクエスト（OPTIONS）

すべてのエンドポイントでOPTIONSリクエストを受け付け、適切なCORSヘッダーを返します。

---

## エンドポイント一覧

### 1. LINE認証

#### エンドポイント

```
POST /auth/verify
```

#### 説明

LINE IDトークンを検証し、ユーザー情報をDynamoDBに保存または更新します。セッショントークンを生成して返します。

#### リクエスト

**ヘッダー**:
```http
Content-Type: application/json
```

**ボディ**:
```json
{
  "id_token": "eyJraWQiOiJhMmE0NTlhZWM1YjY1ZmE0ZThhZGQ1Yzc2OTdjNzliZTQ0NWFlMzEyYmJjZDZlZWY4ZmUwOWI1YmI4MjZjZjNkIiwidHlwIjoiSldUIiwiYWxnIjoiRVMyNTYifQ..."
}
```

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `id_token` | string | 必須 | LINE IDトークン（JWT形式） |

#### レスポンス

**成功時（200 OK）**:
```json
{
  "ok": true,
  "user_id": "Ubb2550980506cc932bf7a8fa7f372ec1",
  "display_name": "竹ノ内春陽",
  "access_token": "{\"display_name\": \"竹ノ内春陽\", \"nonce\": \"...\", \"timestamp\": 1762146994, \"user_id\": \"...\"}|{signature}"
}
```

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `ok` | boolean | 成功を示すフラグ（常に`true`） |
| `user_id` | string | LINEユーザーID（JWTの`sub`から取得） |
| `display_name` | string | ユーザー表示名（JWTの`name`から取得） |
| `access_token` | string | セッショントークン（HMAC-SHA256署名付き） |

**エラー時（400 Bad Request）**:
```json
{
  "error": "Error",
  "message": "id_token is required"
}
```

**エラー時（401 Unauthorized）**:
```json
{
  "error": "Error",
  "message": "Token verification failed: {詳細}"
}
```

**エラー時（500 Internal Server Error）**:
```json
{
  "error": "Error",
  "message": "Failed to save user data: {詳細}"
}
```

#### 実装詳細

- JWTトークンの`sub`（ユーザーID）と`name`（表示名）を取得
- Usersテーブルにユーザー情報を保存または更新
- セッショントークンをHMAC-SHA256で署名して生成
- セッショントークンは`sessionStorage`に保存することを推奨

#### サンプルコード

**JavaScript (LIFFアプリ)**:
```javascript
const idToken = liff.getIDToken();
const response = await fetch('https://{api-id}.execute-api.{region}.amazonaws.com/dev/auth/verify', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    id_token: idToken
  })
});
const data = await response.json();
if (data.ok) {
  sessionStorage.setItem('access_token', data.access_token);
  sessionStorage.setItem('user_id', data.user_id);
}
```

**cURL**:
```bash
curl -X POST https://{api-id}.execute-api.{region}.amazonaws.com/dev/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"id_token": "eyJraWQiOiJhMmE0NTlhZWM1YjY1ZmE0ZThhZGQ1Yzc2OTdjNzliZTQ0NWFlMzEyYmJjZDZlZWY4ZmUwOWI1YmI4MjZjZjNkIiwidHlwIjoiSldUIiwiYWxnIjoiRVMyNTYifQ..."}'
```

---

### 2. スタンプ一覧取得

#### エンドポイント

```
GET /stamps?userId={userId}
```

#### 説明

指定されたユーザーが保有するスタンプの一覧を取得します。スタンプマスタ情報と結合して返します。

#### リクエスト

**ヘッダー**:
```http
Authorization: Bearer {session_token}
```

**クエリパラメータ**:
| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `userId` | string | 必須 | ユーザーID |

#### レスポンス

**成功時（200 OK）**:
```json
{
  "ok": true,
  "user_id": "Ubb2550980506cc932bf7a8fa7f372ec1",
  "stamps": [
    {
      "stamp_id": "stamp_001",
      "name": "駅前広場",
      "description": "JR駅前広場のスタンプ",
      "location": {
        "latitude": 35.6812,
        "longitude": 139.7671
      },
      "image_url": "https://example.com/stamps/stamp_001.png",
      "collected_at": "2025-11-03T12:34:56Z",
      "collection_method": "GPS"
    }
  ],
  "total": 1
}
```

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `ok` | boolean | 成功を示すフラグ（常に`true`） |
| `user_id` | string | ユーザーID |
| `stamps` | array | スタンプ一覧（スタンプマスタ情報と収集情報を含む） |
| `stamps[].stamp_id` | string | スタンプID |
| `stamps[].name` | string | スタンプ名 |
| `stamps[].description` | string | スタンプ説明 |
| `stamps[].location` | object | 位置情報（GPS収集の場合） |
| `stamps[].location.latitude` | number | 緯度 |
| `stamps[].location.longitude` | number | 経度 |
| `stamps[].image_url` | string | スタンプ画像URL |
| `stamps[].collected_at` | string | 収集日時（ISO 8601形式） |
| `stamps[].collection_method` | string | 収集方法（`GPS`または`IMAGE`） |
| `total` | number | スタンプ総数 |

**スタンプが0件の場合（200 OK）**:
```json
{
  "ok": true,
  "user_id": "Ubb2550980506cc932bf7a8fa7f372ec1",
  "stamps": [],
  "total": 0
}
```

**エラー時（400 Bad Request）**:
```json
{
  "error": "Bad Request",
  "message": "userId is required"
}
```

#### 実装詳細

- UserStampsテーブルからユーザーIDでクエリ
- 各スタンプについてStampMastersテーブルからマスタ情報を取得して結合
- スタンプが存在しない場合は空配列を返す

#### サンプルコード

**JavaScript (LIFFアプリ)**:
```javascript
const userId = sessionStorage.getItem('user_id');
const token = sessionStorage.getItem('access_token');
const response = await fetch(`https://{api-id}.execute-api.{region}.amazonaws.com/dev/stamps?userId=${userId}`, {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const data = await response.json();
if (data.ok) {
  console.log(`スタンプ数: ${data.total}`);
  data.stamps.forEach(stamp => {
    console.log(`スタンプ: ${stamp.name} (${stamp.collected_at})`);
  });
}
```

**cURL**:
```bash
curl -X GET "https://{api-id}.execute-api.{region}.amazonaws.com/dev/stamps?userId=Ubb2550980506cc932bf7a8fa7f372ec1" \
  -H "Authorization: Bearer {session_token}"
```

---

### 3. スタンプ授与

#### エンドポイント

```
POST /stamps/award
```

#### 説明

ユーザーにスタンプを授与します。重複チェック、有効期間検証、収集方法の検証を行います。

#### リクエスト

**ヘッダー**:
```http
Content-Type: application/json
Authorization: Bearer {session_token}
```

**ボディ**:
```json
{
  "user_id": "Ubb2550980506cc932bf7a8fa7f372ec1",
  "stamp_id": "stamp_001",
  "method": "GPS"
}
```

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `user_id` | string | 必須 | ユーザーID |
| `stamp_id` | string | 必須 | スタンプID |
| `method` | string | 必須 | 収集方法（`GPS`または`IMAGE`） |

#### レスポンス

**成功時（200 OK）**:
```json
{
  "ok": true,
  "message": "スタンプを授与しました",
  "stamp": {
    "stamp_id": "stamp_001",
    "name": "駅前広場",
    "description": "JR駅前広場のスタンプ",
    "collected_at": "2025-11-03T12:34:56Z"
  }
}
```

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `ok` | boolean | 成功を示すフラグ（常に`true`） |
| `message` | string | 成功メッセージ |
| `stamp` | object | 授与されたスタンプ情報 |
| `stamp.stamp_id` | string | スタンプID |
| `stamp.name` | string | スタンプ名 |
| `stamp.description` | string | スタンプ説明 |
| `stamp.collected_at` | string | 収集日時（ISO 8601形式） |

**エラー時（400 Bad Request）**:

スタンプが存在しない場合（404 Not Found）:
```json
{
  "error": "Error",
  "message": "Stamp not found: {stamp_id}",
  "error_code": "STAMP_NOT_FOUND"
}
```

有効期間外の場合（400 Bad Request）:
```json
{
  "error": "Error",
  "message": "Stamp has expired. Valid until: {timestamp}",
  "error_code": "STAMP_EXPIRED"
}
```

有効期間前の場合（400 Bad Request）:
```json
{
  "error": "Error",
  "message": "Stamp is not yet valid. Valid from: {timestamp}",
  "error_code": "STAMP_NOT_VALID_YET"
}
```

既に収集済みの場合（409 Conflict）:
```json
{
  "error": "Error",
  "message": "User already has this stamp: {stamp_id}",
  "error_code": "STAMP_ALREADY_EXISTS"
}
```

収集方法が一致しない場合（400 Bad Request）:
```json
{
  "error": "Error",
  "message": "Stamp type mismatch. Expected: {expected}, Got: {got}",
  "error_code": "STAMP_TYPE_MISMATCH"
}
```

必須パラメータが不足している場合:
```json
{
  "error": "Bad Request",
  "message": "user_id, stamp_id, method are required"
}
```

**エラー時（500 Internal Server Error）**:
```json
{
  "error": "Internal Server Error",
  "message": "Internal Server Error: {詳細なエラーメッセージ}"
}
```

#### 実装詳細

1. スタンプマスタ情報を取得
2. スタンプが存在するか確認
3. 有効期間内か確認（`ValidFrom` <= 現在時刻 <= `ValidTo`）
4. 収集方法が一致するか確認（`CollectionMethod`）
5. 重複チェック（同一ユーザー・同一スタンプの組み合わせ）
6. UserStampsテーブルに書き込み

#### バリデーションルール

- **スタンプの存在確認**: StampMastersテーブルに`stamp_id`が存在するか
- **有効期間**: 現在時刻が`ValidFrom`と`ValidTo`の間にあるか
- **収集方法**: リクエストの`method`がスタンプマスタの`CollectionMethod`と一致するか
- **重複チェック**: UserStampsテーブルに同一の`UserId`と`StampId`の組み合わせが存在しないか

#### サンプルコード

**JavaScript (LIFFアプリ)**:
```javascript
const userId = sessionStorage.getItem('user_id');
const token = sessionStorage.getItem('access_token');
const response = await fetch('https://{api-id}.execute-api.{region}.amazonaws.com/dev/stamps/award', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    user_id: userId,
    stamp_id: 'stamp_001',
    method: 'GPS'
  })
});
const data = await response.json();
if (data.ok) {
  console.log(`スタンプ獲得: ${data.stamp.name}`);
} else {
  console.error(`エラー: ${data.message}`);
}
```

**cURL**:
```bash
curl -X POST https://{api-id}.execute-api.{region}.amazonaws.com/dev/stamps/award \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {session_token}" \
  -d '{
    "user_id": "Ubb2550980506cc932bf7a8fa7f372ec1",
    "stamp_id": "stamp_001",
    "method": "GPS"
  }'
```

---

### 4. GPS位置情報検証

#### エンドポイント

```
POST /gps/verify
```

#### 説明

GPS位置情報を検証し、指定されたスタンプの範囲内にユーザーがいるかどうかを判定します。Haversine公式を使用して距離を計算し、スタンプマスタに設定された半径（radiusM）と端末の精度（accuracy）を考慮して判定します。

#### リクエスト

**ヘッダー**:
```http
Content-Type: application/json
```

**ボディ**:
```json
{
  "userId": "Ubb2550980506cc932bf7a8fa7f372ec1",
  "spotId": "YIL-001",
  "lat": 35.55548,
  "lon": 139.65503,
  "accuracy": 10.5
}
```

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `userId` | string | 必須 | ユーザーID |
| `spotId` | string | 必須 | スタンプID（spotId） |
| `lat` | number | 必須 | 緯度（-90～90） |
| `lon` | number | 必須 | 経度（-180～180） |
| `accuracy` | number | オプション | 端末の精度（メートル）。指定しない場合は0として扱う |

#### レスポンス

**成功時（200 OK）**:
```json
{
  "ok": true,
  "spotId": "YIL-001",
  "name": "Yagami Innovation Laboratory",
  "lat": 35.55548,
  "lon": 139.65503,
  "distanceM": 45.2,
  "within": true,
  "radiusM": 15,
  "accuracy": 10.5
}
```

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `ok` | boolean | 成功を示すフラグ（常に`true`） |
| `spotId` | string | スタンプID |
| `name` | string | スタンプ名 |
| `lat` | number | リクエストされた緯度 |
| `lon` | number | リクエストされた経度 |
| `distanceM` | number | スタンプ位置からの距離（メートル、小数点第2位まで） |
| `within` | boolean | 範囲内かどうか（`true`：範囲内、`false`：範囲外） |
| `radiusM` | number | スタンプの有効半径（メートル） |
| `accuracy` | number | 使用された精度（メートル） |

**エラー時（400 Bad Request）**:

必須パラメータが不足している場合:
```json
{
  "error": "Error",
  "message": "userId is required"
}
```

スタンプが存在しない場合（404 Not Found）:
```json
{
  "error": "Error",
  "message": "Stamp not found: YIL-001",
  "error_code": "STAMP_NOT_FOUND"
}
```

スタンプタイプがGPSでない場合:
```json
{
  "error": "Error",
  "message": "This stamp is not a GPS type stamp. Type: IMAGE",
  "error_code": "STAMP_TYPE_MISMATCH"
}
```

位置情報が見つからない場合:
```json
{
  "error": "Error",
  "message": "Location information not found in stamp master",
  "error_code": "LOCATION_NOT_FOUND"
}
```

無効な位置データの場合:
```json
{
  "error": "Error",
  "message": "Invalid location data in stamp master",
  "error_code": "INVALID_LOCATION"
}
```

**エラー時（500 Internal Server Error）**:
```json
{
  "error": "Error",
  "message": "Internal Server Error: {詳細なエラーメッセージ}"
}
```

#### 実装詳細

1. スタンプマスタ情報を取得（StampMastersテーブル）
2. スタンプタイプがGPSか確認
3. Location情報からスタンプの座標（lat, lon）と半径（radiusM）を取得
4. Haversine公式を使用して距離を計算
5. 精度（accuracy）と半径（radiusM）を考慮して判定
   - 有効半径 = max(radiusM, accuracy)
   - distanceM <= 有効半径 の場合、`within = true`

#### 距離計算アルゴリズム

Haversine公式を使用して、2点間の大円距離を計算します。

```
distance = R * 2 * atan2(√a, √(1-a))

where:
  a = sin²(Δφ/2) + cos(φ1) * cos(φ2) * sin²(Δλ/2)
  R = 地球の半径 (6,371,000 メートル)
  φ1, φ2 = 緯度1, 緯度2 (ラジアン)
  Δφ = 緯度の差 (ラジアン)
  Δλ = 経度の差 (ラジアン)
```

#### サンプルコード

**JavaScript (LIFFアプリ)**:
```javascript
const userId = sessionStorage.getItem('user_id');

// 位置情報を取得
navigator.geolocation.getCurrentPosition(async (pos) => {
  const { latitude, longitude, accuracy } = pos.coords;
  
  const result = await window.api.verifyGPS(
    userId,
    'YIL-001',
    latitude,
    longitude,
    accuracy
  );
  
  if (result.ok) {
    if (result.within) {
      console.log(`範囲内！距離: ${result.distanceM}m`);
      // スタンプ授与を試みる
      await window.api.awardStamp(userId, 'YIL-001', 'GPS');
    } else {
      console.log(`範囲外。距離: ${result.distanceM}m（半径: ${result.radiusM}m）`);
    }
  }
});
```

**cURL**:
```bash
curl -X POST https://{api-id}.execute-api.{region}.amazonaws.com/dev/gps/verify \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "Ubb2550980506cc932bf7a8fa7f372ec1",
    "spotId": "YIL-001",
    "lat": 35.55548,
    "lon": 139.65503,
    "accuracy": 10.5
  }'
```

---

## エラーレスポンス

### エラーレスポンス形式

すべてのエラーは以下の形式で返されます：

```json
{
  "error": "Error",
  "message": "エラーメッセージ"
}
```

または

```json
{
  "ok": false,
  "error": "Error",
  "message": "エラーメッセージ"
}
```

### エラータイプ

| エラータイプ | HTTPステータス | 説明 |
|------------|--------------|------|
| `Bad Request` | 400 | リクエストパラメータが不正、バリデーションエラー、有効期間外、収集方法不一致 |
| `Unauthorized` | 401 | 認証が必要、または認証に失敗 |
| `Not Found` | 404 | リソースが見つからない（スタンプが存在しない等） |
| `Conflict` | 409 | リソースの競合（既に収集済みのスタンプ等） |
| `Internal Server Error` | 500 | サーバー内部エラー |

---

## ステータスコード一覧

| ステータスコード | 説明 |
|----------------|------|
| `200 OK` | リクエスト成功 |
| `400 Bad Request` | リクエストが不正、バリデーションエラー、有効期間外、収集方法不一致 |
| `401 Unauthorized` | 認証が必要、または認証に失敗 |
| `404 Not Found` | リソースが見つからない（スタンプが存在しない等） |
| `409 Conflict` | リソースの競合（既に収集済みのスタンプ等） |
| `500 Internal Server Error` | サーバー内部エラー |

---

## 補足情報

### タイムゾーン

すべての日時はUTC形式（ISO 8601）で返されます。

### レート制限

現時点ではレート制限は実装されていません。将来的に実装予定です。

### バージョニング

現時点ではAPIバージョニングは実装されていません。URLパスにバージョン番号を含める予定です（例: `/v1/auth/verify`）。

---

## 変更履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2025年11月 | 1.0 | 初版作成（auth, stamps, awardエンドポイント） |
| 2025年11月 | 1.1 | GPS検証エンドポイント（/gps/verify）を追加 |

---

**最終更新**: 2025年1月（GPS検証エンドポイント追加）

