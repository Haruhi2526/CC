# ランキングAPI Gateway設定手順

**作成日**: 2025年1月  
**対象**: `/ranking/friends/weekly` と `/ranking/friends/monthly` エンドポイントの設定

---

## 🔴 問題: 404エラーが発生する

### エラーメッセージ
```
GET https://2bm71jvfs6.execute-api.us-east-1.amazonaws.com/dev/ranking/friends/weekly?user_id=... 404 (Not Found)
```

### 原因
API Gatewayで `/ranking/friends/weekly` リソースが設定されていないため、リクエストがLambda関数に到達していません。

---

## ✅ 解決方法: API Gatewayリソースの設定

### 方法1: リソース階層を作成（推奨）

#### 手順1: `/ranking` リソースの確認

1. API Gatewayコンソールを開く
2. 対象のREST APIを選択
3. 「リソース」から `/ranking` リソースを確認
   - 存在しない場合は作成

#### 手順2: `/ranking/friends` リソースの作成

1. `/ranking` リソースを選択
2. 「アクション」→「リソースの作成」
3. **リソース名**: `friends`
4. **リソースパス**: `friends`
5. 「リソースの作成」をクリック

#### 手順3: `/ranking/friends/weekly` リソースの作成

1. `/ranking/friends` リソースを選択
2. 「アクション」→「リソースの作成」
3. **リソース名**: `weekly`
4. **リソースパス**: `weekly`
5. 「リソースの作成」をクリック

#### 手順4: GETメソッドの追加

1. `/ranking/friends/weekly` リソースを選択
2. 「アクション」→「メソッドの作成」→「GET」を選択
3. **統合タイプ**: `Lambda関数`
4. **Lambdaプロキシ統合を使用**: ✅ チェックを入れる
5. **Lambda関数**: `ranking`（または作成した関数名）
6. **Lambdaリージョン**: 関数が作成されているリージョン
7. 「保存」をクリック
8. 権限の追加を求められたら「OK」をクリック

#### 手順5: `/ranking/friends/monthly` リソースの作成

1. `/ranking/friends` リソースを選択
2. 「アクション」→「リソースの作成」
3. **リソース名**: `monthly`
4. **リソースパス**: `monthly`
5. 「リソースの作成」をクリック
6. GETメソッドを追加（手順4と同様）

---

### 方法2: プロキシリソースを使用（簡易版）

#### 手順1: `/ranking/{proxy+}` リソースの作成

1. `/ranking` リソースを選択
2. 「アクション」→「リソースの作成」
3. **リソース名**: `proxy`
4. **リソースパス**: `{proxy+}`
   - `{proxy+}` はすべてのサブパスをキャッチする
5. 「リソースの作成」をクリック

#### 手順2: ANYメソッドの追加

1. `/ranking/{proxy+}` リソースを選択
2. 「アクション」→「メソッドの作成」→「ANY」を選択
3. **統合タイプ**: `Lambda関数`
4. **Lambdaプロキシ統合を使用**: ✅ チェックを入れる
5. **Lambda関数**: `ranking`
6. **Lambdaリージョン**: 関数が作成されているリージョン
7. 「保存」をクリック

**注意**: この方法では、`/ranking` 配下のすべてのパスがLambda関数に渡されます。Lambda関数内でパスを正しく処理する必要があります。

---

## 🔧 CORS設定

### 手順1: OPTIONSメソッドの追加

各リソース（`/ranking/friends/weekly`、`/ranking/friends/monthly`）にOPTIONSメソッドを追加：

1. リソースを選択
2. 「アクション」→「メソッドの作成」→「OPTIONS」を選択
3. **統合タイプ**: `Lambda関数`
4. **Lambdaプロキシ統合を使用**: ✅ チェックを入れる
5. **Lambda関数**: `ranking`
6. 「保存」をクリック

**または**、API GatewayのCORS機能を使用：

1. リソースを選択
2. 「アクション」→「CORSを有効化」
3. 以下の設定を入力：
   - **Access-Control-Allow-Origin**: `*`（本番環境では適切なオリジンを指定）
   - **Access-Control-Allow-Headers**: `Content-Type,Authorization`
   - **Access-Control-Allow-Methods**: `GET,OPTIONS`
4. 「CORSを有効化して既存のCORSヘッダーを置き換える」をクリック

---

## 📋 リソース構造（推奨）

```
/ranking
  ├── /friends
  │   ├── /weekly
  │   │   ├── GET (Lambda統合)
  │   │   └── OPTIONS (CORS)
  │   └── /monthly
  │       ├── GET (Lambda統合)
  │       └── OPTIONS (CORS)
  ├── /calculate
  │   └── POST (Lambda統合)
  └── /compare
      └── GET (Lambda統合)
```

---

## 🚀 APIのデプロイ

**重要**: リソースやメソッドを追加・変更した後は、必ずAPIを再デプロイする必要があります。

1. 「アクション」→「APIのデプロイ」
2. **デプロイされるステージ**: `dev` を選択
3. 「デプロイ」をクリック

---

## ✅ 動作確認

### 1. API Gatewayコンソールでテスト

1. `/ranking/friends/weekly` リソース → GETメソッドを選択
2. 「テスト」をクリック
3. **クエリ文字列**: `user_id=test_user_123&period=2025-W01`
4. 「テスト」ボタンをクリック
5. レスポンスを確認

**成功時のレスポンス例**:
```json
{
  "statusCode": 200,
  "body": "{\"ok\":true,\"period\":\"2025-W01\",\"period_type\":\"weekly\",\"rankings\":[]}"
}
```

### 2. curlコマンドでテスト

```bash
curl -X GET "https://2bm71jvfs6.execute-api.us-east-1.amazonaws.com/dev/ranking/friends/weekly?user_id=test_user_123"
```

### 3. ブラウザで確認

フロントエンドからアクセスして、エラーが解消されているか確認。

---

## 🔍 トラブルシューティング

### 問題1: 404エラーが続く

**確認事項**:
1. APIを再デプロイしたか
2. 正しいステージ（`dev`）にデプロイしたか
3. リソースパスが正しいか（`/ranking/friends/weekly`）
4. Lambda関数名が正しいか

### 問題2: CORSエラーが発生する

**確認事項**:
1. OPTIONSメソッドが追加されているか
2. CORS設定が正しいか
3. Lambda関数のレスポンスにCORSヘッダーが含まれているか

### 問題3: Lambda関数が呼び出されない

**確認事項**:
1. Lambda関数のIAMロールにAPI Gatewayからの呼び出し権限があるか
2. Lambda関数名が正しいか
3. Lambdaプロキシ統合が有効になっているか

---

## 📝 参考

- [ランキングAPI Gatewayエンドポイント一覧](./ランキングAPI Gatewayエンドポイント一覧.md)
- [ランキング機能実装手順](./ランキング機能実装手順.md)

---

**最終更新**: 2025年1月

