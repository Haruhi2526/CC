# CORSエラー - OPTIONSリクエストが500エラーを返す場合の解決方法

## 🔴 問題の状況

### エラーメッセージ
```
Access to fetch at 'https://c5nmu4q3di.execute-api.us-east-1.amazonaws.com/dev/auth/verify' 
from origin 'https://semiemotionally-nonanarchistic-beverley.ngrok-free.dev' 
has been blocked by CORS policy: 
Response to preflight request doesn't pass access control check: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

### OPTIONSリクエストのテスト結果

```bash
curl -X OPTIONS \
  -H "Origin: https://semiemotionally-nonanarchistic-beverley.ngrok-free.dev" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization" \
  -i https://c5nmu4q3di.execute-api.us-east-1.amazonaws.com/dev/auth/verify
```

**レスポンス**:
```
HTTP/2 500 
{"message": "Internal server error"}
```

**問題点**:
- OPTIONSリクエストが500エラーを返している
- CORSヘッダーが含まれていない
- Lambda関数でエラーが発生している可能性

---

## 🔍 原因の分析

### 考えられる原因

1. **Lambda関数がOPTIONSリクエストを正しく処理していない**
   - `lambda_function.py`のOPTIONS処理に問題がある可能性

2. **Lambdaプロキシ統合の設定が正しくない**
   - OPTIONSメソッドで「Lambdaプロキシ統合を使用」にチェックが入っていない

3. **Lambda関数のエラーハンドリングに問題がある**
   - OPTIONSリクエスト時に例外が発生している

4. **API GatewayのCORS設定が正しくない**
   - CORS有効化ウィザードを使用していない

---

## ✅ 解決方法

### 解決方法1: API GatewayでCORSを有効化（推奨）

Lambda関数に依存せず、API GatewayでCORSを処理する方法：

1. **API Gatewayコンソールを開く**
   - AWSマネジメントコンソール → API Gateway

2. **対象のREST APIを選択**

3. **`/auth`リソースを選択**
   - ⚠️ `/auth/verify`ではなく、親リソースの`/auth`を選択

4. **「アクション」→「CORSを有効化」をクリック**

5. **以下の設定を入力**:
   ```
   Access-Control-Allow-Origin: *
   Access-Control-Allow-Headers: Content-Type,Authorization
   Access-Control-Allow-Methods: POST,OPTIONS
   ```

6. **「CORSを有効化して既存のCORSヘッダーを置き換える」をクリック**

7. **確認ダイアログで「はい、既存の値を置き換えます」をクリック**

これにより、API Gatewayが自動的にOPTIONSメソッドを作成し、CORSヘッダーを返します。

### 解決方法2: OPTIONSメソッドをMOCK統合に変更

Lambda関数に依存せず、API Gatewayで直接CORSヘッダーを返す方法：

1. **`/auth`リソース → 「OPTIONS」メソッドを選択**

2. **「統合リクエスト」をクリック**

3. **統合タイプを変更**:
   - **統合タイプ**: `MOCK` を選択
   - 「保存」をクリック

4. **「メソッドレスポンス」をクリック**

5. **「200」レスポンスの「ヘッダー」を展開**

6. **以下のヘッダーを追加**:
   - `Access-Control-Allow-Origin`
   - `Access-Control-Allow-Headers`
   - `Access-Control-Allow-Methods`

7. **「統合レスポンス」をクリック**

8. **「ヘッダーマッピング」で以下を設定**:
   - `Access-Control-Allow-Origin`: `'*'`
   - `Access-Control-Allow-Headers`: `'Content-Type,Authorization'`
   - `Access-Control-Allow-Methods`: `'POST,OPTIONS'`

9. **「マッピングテンプレート」を追加**:
   - **コンテンツタイプ**: `application/json`
   - **テンプレート**: `{}`（空のJSON）

10. **APIを再デプロイ**

### 解決方法3: Lambda関数のOPTIONS処理を修正

Lambda関数でOPTIONSリクエストを正しく処理する方法：

1. **`lambda_function.py`を確認**

現在のコード（134-136行目）:
```python
# OPTIONSリクエストの処理（CORS preflight）
if event.get('httpMethod') == 'OPTIONS':
    logger.info('CORS preflightリクエストを処理')
    return create_response(200, {'ok': True})
```

このコードは正しいはずですが、エラーが発生している場合は以下を確認：

2. **Lambda関数のログを確認**
   - CloudWatch Logsでエラーの詳細を確認
   - エラーメッセージを確認

3. **Lambda関数を再デプロイ**
   - ZIPファイルを再作成
   - Lambda関数を更新

---

## 🔧 推奨される解決手順

### ステップ1: API GatewayでCORSを有効化（最も簡単）

1. `/auth`リソースを選択
2. 「アクション」→「CORSを有効化」
3. 設定を入力
4. 「CORSを有効化して既存のCORSヘッダーを置き換える」をクリック

### ステップ2: 既存のOPTIONSメソッドを削除（必要に応じて）

CORS有効化ウィザードが自動的にOPTIONSメソッドを作成するため、既存のOPTIONSメソッドがある場合は削除：

1. `/auth`リソース → 「OPTIONS」メソッドを選択
2. 「アクション」→「メソッドの削除」
3. 確認ダイアログで「削除」をクリック

### ステップ3: APIを再デプロイ

1. 「アクション」→「APIのデプロイ」
2. **デプロイされるステージ**: `dev` を選択
3. 「デプロイ」をクリック

### ステップ4: 動作確認

```bash
curl -X OPTIONS \
  -H "Origin: https://semiemotionally-nonanarchistic-beverley.ngrok-free.dev" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization" \
  -i https://c5nmu4q3di.execute-api.us-east-1.amazonaws.com/dev/auth/verify
```

**期待される成功レスポンス**:
```
HTTP/2 200 
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: POST,OPTIONS
Access-Control-Allow-Headers: Content-Type,Authorization
```

---

## 📋 チェックリスト

### API Gatewayの設定

- [ ] `/auth`リソースでCORSを有効化した
- [ ] CORS設定:
  - [ ] `Access-Control-Allow-Origin: *`
  - [ ] `Access-Control-Allow-Headers: Content-Type,Authorization`
  - [ ] `Access-Control-Allow-Methods: POST,OPTIONS`
- [ ] OPTIONSメソッドが自動作成された（CORS有効化で）
- [ ] APIを`dev`ステージに再デプロイした

### 動作確認

- [ ] curlコマンドでOPTIONSリクエストが200を返す
- [ ] レスポンスにCORSヘッダーが含まれている
- [ ] ブラウザのキャッシュをクリアした
- [ ] ブラウザでCORSエラーが解消された

---

## 🚨 注意事項

### 既存のOPTIONSメソッドがある場合

CORS有効化ウィザードを使用すると、既存のOPTIONSメソッドが上書きされる可能性があります。問題が発生する場合は：

1. 既存のOPTIONSメソッドを削除
2. CORS有効化ウィザードを実行
3. APIを再デプロイ

### Lambda関数のOPTIONS処理

CORS有効化ウィザードを使用する場合、Lambda関数のOPTIONS処理は不要になります。API Gatewayが自動的にCORSヘッダーを返します。

ただし、Lambda関数のOPTIONS処理を残しておいても問題ありません。API GatewayのCORS設定が優先されます。

---

## 📚 参考ドキュメント

- [CORSエラー診断と解決チェックリスト.md](./CORSエラー診断と解決チェックリスト.md) - 診断手順
- [CORSエラー解決手順-即座に実行.md](./CORSエラー解決手順-即座に実行.md) - 簡易版解決手順
- [CORS設定修正手順-auth関数.md](./CORS設定修正手順-auth関数.md) - 詳細な修正手順

