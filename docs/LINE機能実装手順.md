# LINE機能実装手順

**作成日**: 2025年1月  
**対象機能**: リッチメニュー、プッシュ通知

---

## 📋 実装完了項目

### ✅ Phase 1: リッチメニュー機能

#### 実装ファイル
- `backend/lambda/richmenu/lambda_function.py` - リッチメニュー管理API
- `backend/lambda/richmenu/response_utils.py` - レスポンスユーティリティ
- `backend/lambda/richmenu/requirements.txt` - 依存ライブラリ
- `backend/lambda/richmenu/build.sh` - ビルドスクリプト

#### 機能
- リッチメニュー一覧取得 (`GET /richmenu/list`)
- ユーザーへのリッチメニュー設定 (`POST /richmenu/set`)
- ユーザーからのリッチメニュー削除 (`DELETE /richmenu/unset`)
- デフォルトリッチメニューID取得 (`GET /richmenu/default`)

---

### ✅ Phase 2: プッシュ通知機能

#### 実装ファイル
- `backend/lambda/notify/lambda_function.py` - プッシュ通知送信API
- `backend/lambda/notify/response_utils.py` - レスポンスユーティリティ
- `backend/lambda/notify/requirements.txt` - 依存ライブラリ
- `backend/lambda/notify/build.sh` - ビルドスクリプト

#### 機能
- スタンプ取得通知 (`type: stamp_awarded`)
- イベント開始通知 (`type: event_started`)
- リマインド通知 (`type: reminder`)
- Flex Message対応（スタンプ取得通知）

#### 統合
- `backend/lambda/award/lambda_function.py` - スタンプ授与成功時に自動通知

---

## 🚀 デプロイ手順

### 1. リッチメニュー関数のデプロイ

#### Step 1: ZIPファイルの作成
```bash
cd backend/lambda/richmenu
./build.sh
```

#### Step 2: AWS Lambda関数の作成
1. AWS Lambdaコンソールにアクセス
2. 「関数の作成」をクリック
3. 関数名: `richmenu`
4. ランタイム: Python 3.11
5. アーキテクチャ: x86_64
6. ZIPファイルをアップロード

#### Step 3: 環境変数の設定
- `LINE_CHANNEL_ACCESS_TOKEN`: LINE Messaging APIのアクセストークン

#### Step 4: API Gateway統合
1. API Gatewayコンソールで既存のAPIを選択
2. リソース `/richmenu` を作成
3. 以下のメソッドを追加:
   - `GET /richmenu/list`
   - `POST /richmenu/set`
   - `DELETE /richmenu/unset`
   - `GET /richmenu/default`
4. 各メソッドにLambda統合を設定（プロキシ統合）
5. CORS設定を有効化

---

### 2. プッシュ通知関数のデプロイ

#### Step 1: ZIPファイルの作成
```bash
cd backend/lambda/notify
./build.sh
```

#### Step 2: AWS Lambda関数の作成
1. AWS Lambdaコンソールにアクセス
2. 「関数の作成」をクリック
3. 関数名: `notify`
4. ランタイム: Python 3.11
5. アーキテクチャ: x86_64
6. ZIPファイルをアップロード

#### Step 3: 環境変数の設定
- `LINE_CHANNEL_ACCESS_TOKEN`: LINE Messaging APIのアクセストークン
- `LIFF_BASE_URL`: LIFFアプリのベースURL（オプション）

#### Step 4: API Gateway統合
1. API Gatewayコンソールで既存のAPIを選択
2. リソース `/notify` を作成
3. `POST /notify` メソッドを追加
4. Lambda統合を設定（プロキシ統合）
5. CORS設定を有効化

#### Step 5: award関数の更新
1. `award` Lambda関数のZIPファイルを再作成
2. 環境変数に追加:
   - `NOTIFY_FUNCTION_NAME`: `notify`（デフォルト値）
3. IAMロールにLambda呼び出し権限を追加:
   ```json
   {
     "Effect": "Allow",
     "Action": "lambda:InvokeFunction",
     "Resource": "arn:aws:lambda:*:*:function:notify"
   }
   ```

---

## 🔧 LINE Developers Console設定

### 1. Channel Access Tokenの取得
1. LINE Developers Consoleにログイン
2. チャネルを選択
3. 「Messaging API」タブを開く
4. 「Channel access token」セクションで「Issue」をクリック
5. トークンをコピー（AWS Secrets Managerまたは環境変数に保存）

### 2. リッチメニューの作成
1. LINE Developers Consoleで「Messaging API」タブを開く
2. 「Rich menu」セクションで「Create」をクリック
3. リッチメニューを設定:
   - メニュー名: 「ホーム | スタンプ一覧」
   - エリア1: 「ホーム」→ LIFF URL遷移
   - エリア2: 「スタンプ一覧」→ LIFF URL遷移
4. 画像をアップロード（2500x1686px推奨）
5. 「Publish」をクリックして公開
6. リッチメニューIDをメモ

---

## 📝 API仕様

### リッチメニューAPI

#### GET /richmenu/list
リッチメニュー一覧を取得

**レスポンス例:**
```json
{
  "ok": true,
  "richmenus": [
    {
      "richMenuId": "richmenu-xxx",
      "size": {...},
      "selected": true,
      "name": "ホーム | スタンプ一覧",
      "chatBarText": "メニュー",
      "areas": [...]
    }
  ]
}
```

#### POST /richmenu/set
ユーザーにリッチメニューを設定

**リクエストボディ:**
```json
{
  "user_id": "U1234567890abcdef",
  "richmenu_id": "richmenu-xxx"
}
```

**レスポンス例:**
```json
{
  "ok": true,
  "message": "Richmenu set successfully",
  "user_id": "U1234567890abcdef",
  "richmenu_id": "richmenu-xxx"
}
```

---

### プッシュ通知API

#### POST /notify
プッシュ通知を送信

**リクエストボディ:**
```json
{
  "user_id": "U1234567890abcdef",
  "type": "stamp_awarded",
  "data": {
    "stamp_id": "YIL-001",
    "stamp_name": "駅前広場",
    "stamp_image_url": "https://example.com/stamp.png"
  }
}
```

**通知タイプ:**
- `stamp_awarded`: スタンプ取得通知（Flex Message）
- `event_started`: イベント開始通知（テキストメッセージ）
- `reminder`: リマインド通知（テキストメッセージ）

**レスポンス例:**
```json
{
  "ok": true,
  "message": "Notification sent successfully",
  "user_id": "U1234567890abcdef",
  "type": "stamp_awarded"
}
```

---

## 🧪 テスト方法

### リッチメニューのテスト
```bash
# リッチメニュー一覧取得
curl -X GET https://2bm71jvfs6.execute-api.us-east-1.amazonaws.com/dev/richmenu/list

# ユーザーにリッチメニュー設定
curl -X POST https://2bm71jvfs6.execute-api.us-east-1.amazonaws.com/dev/richmenu/set \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "YOUR_USER_ID",
    "richmenu_id": "YOUR_RICHMENU_ID"
  }'
```

### プッシュ通知のテスト
```bash
curl -X POST https://2bm71jvfs6.execute-api.us-east-1.amazonaws.com/dev/notify \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "YOUR_USER_ID",
    "type": "stamp_awarded",
    "data": {
      "stamp_id": "YIL-001",
      "stamp_name": "駅前広場",
      "stamp_image_url": "https://example.com/stamp.png"
    }
  }'
```

---

## ⚠️ 注意事項

### セキュリティ
- Channel Access Tokenは環境変数またはAWS Secrets Managerで管理
- 本番環境では環境変数からSecrets Managerへの移行を推奨

### コスト管理
- プッシュ通知は1秒あたり最大200メッセージの制限あり
- CloudWatchアラームで送信量を監視

### エラーハンドリング
- 通知失敗時もスタンプ授与は成功（非同期処理のため）
- エラーはCloudWatch Logsで確認

---

## 🔧 トラブルシューティング

### 400 Bad Request エラー

#### 原因1: 無効なユーザーID
**エラーメッセージ例:**
```json
{
  "ok": false,
  "error": "LINE API Error (400): Invalid user ID"
}
```

**対処法:**
- `YOUR_USER_ID`を実際のLINEユーザーIDに置き換える
- ユーザーIDは`U`で始まる33文字の文字列（例: `U1234567890abcdef1234567890abcdef`）
- LIFFアプリから取得: `liff.getProfile().then(profile => console.log(profile.userId))`

#### 原因2: Channel Access Tokenが設定されていない
**エラーメッセージ例:**
```json
{
  "ok": false,
  "error": "LINE_CHANNEL_ACCESS_TOKEN is not configured"
}
```

**対処法:**
1. LINE Developers ConsoleでChannel Access Tokenを発行
2. AWS Lambda関数の環境変数に設定:
   - キー: `LINE_CHANNEL_ACCESS_TOKEN`
   - 値: 発行したトークン

#### 原因3: Flex Messageの形式エラー
**エラーメッセージ例:**
```json
{
  "ok": false,
  "error": "LINE API Error (400): Invalid request body"
}
```

**対処法:**
- Flex Messageの構造を確認
- `altText`が設定されているか確認
- 画像URLが有効か確認

### 401 Unauthorized エラー

**原因:** Channel Access Tokenが無効または期限切れ

**対処法:**
1. LINE Developers Consoleで新しいトークンを発行
2. Lambda関数の環境変数を更新
3. 関数を再デプロイ

### 実際のユーザーIDの取得方法

#### 方法1: LIFFアプリから取得
```javascript
// frontend/liff-app/js/app.js など
liff.init({ liffId: CONFIG.LIFF_ID })
  .then(() => {
    if (liff.isLoggedIn()) {
      liff.getProfile()
        .then(profile => {
          console.log('User ID:', profile.userId);
          // このuserIdをテストに使用
        });
    }
  });
```

#### 方法2: auth関数のレスポンスから取得
認証APIのレスポンスにユーザーIDが含まれている場合、それを使用できます。

### テスト時の注意点

1. **実際のユーザーIDを使用**
   - `YOUR_USER_ID`はプレースホルダーです
   - 実際のLINEユーザーIDに置き換えてください

2. **Channel Access Tokenの確認**
   - Lambda関数の環境変数が正しく設定されているか確認
   - トークンが有効期限内か確認

3. **CloudWatch Logsで詳細を確認**
   - Lambda関数のログを確認して、詳細なエラーメッセージを確認
   - LINE APIからのエラーレスポンスが記録されています

---

## 📚 参考資料

- [LINE Messaging API ドキュメント](https://developers.line.biz/ja/docs/messaging-api/)
- [リッチメニュー API リファレンス](https://developers.line.biz/ja/reference/messaging-api/#rich-menu)
- [プッシュメッセージ API リファレンス](https://developers.line.biz/ja/reference/messaging-api/#send-push-message)
- [Flex Message 仕様](https://developers.line.biz/ja/docs/messaging-api/using-flex-messages/)

---

**最終更新**: 2025年1月

