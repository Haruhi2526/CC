# CORSエラー - Lambda関数名変更が原因の場合の解決方法

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

---

## 🔍 原因の分析

### Lambda関数名を変更した場合の問題

Lambda関数名を変更した場合、API GatewayのOPTIONSメソッドが**古いLambda関数名**を参照している可能性があります。

**問題の流れ**:
1. Lambda関数名を変更（例: `auth` → `stamp-rally-auth`）
2. API GatewayのOPTIONSメソッドが古い関数名（`auth`）を参照
3. 古い関数が存在しない、またはエラーが発生
4. OPTIONSリクエストが500エラーを返す
5. CORSヘッダーが返されない
6. ブラウザがCORSエラーを表示

---

## ✅ 解決方法

### 方法1: API GatewayのOPTIONSメソッドの統合設定を確認・修正（推奨）

#### ステップ1: OPTIONSメソッドの統合設定を確認

1. **API Gatewayコンソールを開く**
   - AWSマネジメントコンソール → API Gateway

2. **対象のREST APIを選択**

3. **`/auth`リソースを選択**

4. **「OPTIONS」メソッドを選択**

5. **「統合リクエスト」をクリック**

6. **統合設定を確認**:
   - **統合タイプ**: `Lambda関数` が選択されているか
   - **Lambda関数**: 現在参照されている関数名を確認
   - **Lambdaリージョン**: 正しいリージョンが選択されているか

#### ステップ2: Lambda関数名を修正

1. **「統合リクエスト」画面で「Lambda関数」フィールドを確認**

2. **現在のLambda関数名を確認**
   - 例: `auth`（古い名前）
   - または、存在しない関数名

3. **正しいLambda関数名に変更**:
   - ドロップダウンから正しい関数名を選択
   - または、正しい関数名を入力（例: `stamp-rally-auth`）

4. **「保存」をクリック**

5. **権限の追加を求められたら「OK」をクリック**

#### ステップ3: Lambdaプロキシ統合の確認

1. **「Lambdaプロキシ統合を使用」にチェックが入っているか確認**
   - チェックが入っていない場合、チェックを入れる

2. **「保存」をクリック**

#### ステップ4: APIを再デプロイ

1. **「アクション」→「APIのデプロイ」**

2. **デプロイされるステージ**: `dev` を選択

3. **「デプロイ」をクリック**

### 方法2: API GatewayでCORSを有効化（Lambda関数に依存しない方法）

Lambda関数名の問題を回避するため、API GatewayのCORS機能を使用する方法：

1. **`/auth`リソースを選択**

2. **「アクション」→「CORSを有効化」**

3. **以下の設定を入力**:
   ```
   Access-Control-Allow-Origin: *
   Access-Control-Allow-Headers: Content-Type,Authorization
   Access-Control-Allow-Methods: POST,OPTIONS
   ```

4. **「CORSを有効化して既存のCORSヘッダーを置き換える」をクリック**

5. **確認ダイアログで「はい、既存の値を置き換えます」をクリック**

これにより、API Gatewayが自動的にOPTIONSメソッドを作成し、Lambda関数に依存せずにCORSヘッダーを返します。

6. **APIを再デプロイ**

### 方法3: OPTIONSメソッドを削除して再作成

既存のOPTIONSメソッドに問題がある場合：

1. **`/auth`リソース → 「OPTIONS」メソッドを選択**

2. **「アクション」→「メソッドの削除」**

3. **確認ダイアログで「削除」をクリック**

4. **「アクション」→「メソッドの作成」→「OPTIONS」**

5. **統合設定**:
   - **統合タイプ**: `Lambda関数`
   - **Lambda関数**: 正しい関数名を選択（例: `stamp-rally-auth`）
   - **Lambdaプロキシ統合を使用**: ✅ チェックを入れる

6. **「保存」をクリック**

7. **APIを再デプロイ**

---

## 🔍 確認手順

### 1. 現在のLambda関数名を確認

1. **Lambdaコンソールを開く**
   - AWSマネジメントコンソール → Lambda

2. **関数一覧から認証用のLambda関数を確認**
   - 関数名をメモ（例: `stamp-rally-auth`）

### 2. API GatewayのOPTIONSメソッドの統合設定を確認

1. **API Gatewayコンソール → 対象のREST API → `/auth`リソース → 「OPTIONS」メソッド**

2. **「統合リクエスト」をクリック**

3. **「Lambda関数」フィールドを確認**
   - 現在の関数名と、実際のLambda関数名が一致しているか確認

### 3. 動作確認

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

### Lambda関数の確認

- [ ] 実際のLambda関数名を確認した
- [ ] Lambda関数が存在することを確認した
- [ ] Lambda関数が正しいリージョンにあることを確認した

### API Gatewayの設定

- [ ] `/auth`リソースにOPTIONSメソッドが存在する
- [ ] OPTIONSメソッドの統合設定を確認した
- [ ] OPTIONSメソッドが正しいLambda関数名を参照している
- [ ] 「Lambdaプロキシ統合を使用」にチェックが入っている
- [ ] APIを`dev`ステージに再デプロイした

### 動作確認

- [ ] curlコマンドでOPTIONSリクエストが200を返す
- [ ] レスポンスにCORSヘッダーが含まれている
- [ ] ブラウザのキャッシュをクリアした
- [ ] ブラウザでCORSエラーが解消された

---

## 🚨 よくある間違い

### 間違い1: Lambda関数名の不一致

❌ **間違い**: API GatewayのOPTIONSメソッドが古いLambda関数名を参照している
✅ **正しい**: 正しいLambda関数名を参照するように修正

### 間違い2: Lambdaプロキシ統合を使用していない

❌ **間違い**: OPTIONSメソッドで「Lambdaプロキシ統合を使用」にチェックを入れていない
✅ **正しい**: 「Lambdaプロキシ統合を使用」にチェックを入れる

### 間違い3: APIを再デプロイしていない

❌ **間違い**: 設定を変更したが、APIを再デプロイしていない
✅ **正しい**: 設定変更後、必ずAPIを再デプロイ

---

## 💡 推奨される解決手順

1. **Lambda関数名を確認**
   - Lambdaコンソールで実際の関数名を確認

2. **API GatewayのOPTIONSメソッドの統合設定を確認**
   - 正しいLambda関数名を参照しているか確認

3. **必要に応じて修正**
   - Lambda関数名を修正
   - または、CORS有効化ウィザードを使用（推奨）

4. **APIを再デプロイ**

5. **動作確認**

---

## 📚 参考ドキュメント

- [CORSエラー-500エラーの解決方法.md](./CORSエラー-500エラーの解決方法.md) - 500エラーの解決方法
- [CORSエラー診断と解決チェックリスト.md](./CORSエラー診断と解決チェックリスト.md) - 診断手順
- [CORSエラー解決手順-即座に実行.md](./CORSエラー解決手順-即座に実行.md) - 簡易版解決手順

