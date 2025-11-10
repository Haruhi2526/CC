# ランキングAPI Gateway完全設定手順

**作成日**: 2025年1月  
**対象**: ランキング関連のすべてのエンドポイント設定

---

## 🔴 エラーメッセージ

```
ID 2bm71jvfs6 の API には、POST メソッドで統合 arn:aws:lambda:us-east-1:776121695817:function:ranking を持つパス /ranking のリソースが含まれていません。
```

### 原因
`/ranking` リソースが存在しないか、POSTメソッドが設定されていません。

---

## ✅ 完全な設定手順

### ステップ1: `/ranking` リソースの作成

1. **API Gatewayコンソールを開く**
   - AWSコンソール → API Gateway
   - API ID `2bm71jvfs6` のAPIを選択

2. **`/ranking` リソースを作成**
   - 左メニューの「リソース」を選択
   - 「アクション」→「リソースの作成」をクリック
   - **リソースパス**: `/ranking`
   - **リソース名**: `ranking`（任意）
   - 「リソースの作成」をクリック

### ステップ2: `/ranking/calculate` リソースの作成

1. **`/ranking` リソースを選択**
2. **「アクション」→「リソースの作成」**
3. **リソースパス**: `calculate`
4. **リソース名**: `calculate`
5. **「リソースの作成」をクリック**

### ステップ3: `/ranking/calculate` にPOSTメソッドを追加

1. **`/ranking/calculate` リソースを選択**
2. **「アクション」→「メソッドの作成」→「POST」を選択**
3. **統合タイプ**: `Lambda関数`
4. **Lambdaプロキシ統合を使用**: ✅ **チェックを入れる（重要！）**
5. **Lambda関数**: `ranking` を選択
   - または、ARNを直接入力: `arn:aws:lambda:us-east-1:776121695817:function:ranking`
6. **Lambdaリージョン**: `us-east-1`
7. **「保存」をクリック**
8. **権限の追加を求められたら「OK」をクリック**

### ステップ4: `/ranking/friends` リソースの作成

1. **`/ranking` リソースを選択**
2. **「アクション」→「リソースの作成」**
3. **リソースパス**: `friends`
4. **リソース名**: `friends`
5. **「リソースの作成」をクリック**

### ステップ5: `/ranking/friends/weekly` リソースの作成

1. **`/ranking/friends` リソースを選択**
2. **「アクション」→「リソースの作成」**
3. **リソースパス**: `weekly`
4. **リソース名**: `weekly`
5. **「リソースの作成」をクリック**

### ステップ6: `/ranking/friends/weekly` にGETメソッドを追加

1. **`/ranking/friends/weekly` リソースを選択**
2. **「アクション」→「メソッドの作成」→「GET」を選択**
3. **統合タイプ**: `Lambda関数`
4. **Lambdaプロキシ統合を使用**: ✅ **チェックを入れる**
5. **Lambda関数**: `ranking` を選択
6. **Lambdaリージョン**: `us-east-1`
7. **「保存」をクリック**
8. **権限の追加を求められたら「OK」をクリック**

### ステップ7: `/ranking/friends/monthly` リソースの作成

1. **`/ranking/friends` リソースを選択**
2. **「アクション」→「リソースの作成」**
3. **リソースパス**: `monthly`
4. **リソース名**: `monthly`
5. **「リソースの作成」をクリック**

### ステップ8: `/ranking/friends/monthly` にGETメソッドを追加

1. **`/ranking/friends/monthly` リソースを選択**
2. **「アクション」→「メソッドの作成」→「GET」を選択**
3. **統合タイプ**: `Lambda関数`
4. **Lambdaプロキシ統合を使用**: ✅ **チェックを入れる**
5. **Lambda関数**: `ranking` を選択
6. **Lambdaリージョン**: `us-east-1`
7. **「保存」をクリック**
8. **権限の追加を求められたら「OK」をクリック**

### ステップ9: `/ranking/compare` リソースの作成（オプション）

1. **`/ranking` リソースを選択**
2. **「アクション」→「リソースの作成」**
3. **リソースパス**: `compare`
4. **リソース名**: `compare`
5. **「リソースの作成」をクリック**
6. **GETメソッドを追加**（ステップ6と同様）

### ステップ10: CORS設定

各リソース（`/ranking/friends/weekly`、`/ranking/friends/monthly`）にCORSを設定：

1. **リソースを選択**
2. **「アクション」→「CORSを有効化」**
3. **設定を入力**:
   - **Access-Control-Allow-Origin**: `*`
   - **Access-Control-Allow-Headers**: `Content-Type,Authorization`
   - **Access-Control-Allow-Methods**: `GET,OPTIONS`（または`GET,POST,OPTIONS`）
4. **「CORSを有効化して既存のCORSヘッダーを置き換える」をクリック**

### ステップ11: APIの再デプロイ（重要！）

**重要**: すべての設定変更後は、必ずAPIを再デプロイする必要があります。

1. **「アクション」→「APIのデプロイ」**
2. **デプロイされるステージ**: `dev` を選択
3. **「デプロイ」をクリック**

---

## 📋 完成後のリソース構造

```
/ranking
  ├── /calculate
  │   └── POST (Lambda統合: ranking)
  ├── /friends
  │   ├── /weekly
  │   │   ├── GET (Lambda統合: ranking)
  │   │   └── OPTIONS (CORS)
  │   └── /monthly
  │       ├── GET (Lambda統合: ranking)
  │       └── OPTIONS (CORS)
  └── /compare
      └── GET (Lambda統合: ranking) [オプション]

/friends
  ├── /add
  │   └── POST (Lambda統合: friends)
  └── /list
      └── GET (Lambda統合: friends)
```

**注意**: `/ranking/weekly` と `/ranking/monthly` は実装されていません。友達ランキングのみを使用してください。

---

## ✅ 動作確認

### 1. API Gatewayコンソールでテスト

#### `/ranking/friends/weekly` のテスト

1. `/ranking/friends/weekly` リソース → GETメソッドを選択
2. 「テスト」をクリック
3. **クエリ文字列**: `user_id=test_user_123`
4. 「テスト」ボタンをクリック
5. **レスポンス**:
   ```json
   {
     "statusCode": 200,
     "body": "{\"ok\":true,\"period\":\"2025-W01\",\"period_type\":\"weekly\",\"rankings\":[]}"
   }
   ```

#### `/ranking/calculate` のテスト

1. `/ranking/calculate` リソース → POSTメソッドを選択
2. 「テスト」をクリック
3. **クエリ文字列**: `type=weekly`
4. 「テスト」ボタンをクリック

### 2. curlコマンドでテスト

```bash
# 友達週間ランキング取得
curl -X GET "https://2bm71jvfs6.execute-api.us-east-1.amazonaws.com/dev/ranking/friends/weekly?user_id=test_user_123"

# ランキング計算
curl -X POST "https://2bm71jvfs6.execute-api.us-east-1.amazonaws.com/dev/ranking/calculate?type=weekly"
```

### 3. ブラウザで確認

フロントエンドからアクセスして、404エラーが解消されているか確認してください。

---

## 🔍 トラブルシューティング

### 問題1: エラーメッセージが続く

**確認事項**:
1. `/ranking` リソースが作成されているか
2. `/ranking/calculate` リソースが作成されているか
3. POSTメソッドが正しく設定されているか
4. Lambda関数名が正しいか（`ranking`）
5. Lambdaプロキシ統合が有効になっているか
6. APIが再デプロイされているか

### 問題2: Lambda関数が見つからない

**確認事項**:
1. Lambda関数名が正しいか
2. Lambda関数が `us-east-1` リージョンに存在するか
3. Lambda関数のARNが正しいか: `arn:aws:lambda:us-east-1:776121695817:function:ranking`

### 問題3: 権限エラー

**確認事項**:
1. API GatewayがLambda関数を呼び出す権限があるか
2. 権限の追加を求められたときに「OK」をクリックしたか

---

## 📝 参考

- [ランキングAPI Gatewayエンドポイント一覧](./ランキングAPI Gatewayエンドポイント一覧.md)
- [ランキング機能実装手順](./ランキング機能実装手順.md)

---

**最終更新**: 2025年1月

