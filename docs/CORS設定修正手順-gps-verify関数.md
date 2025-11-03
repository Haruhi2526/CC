# CORS設定修正手順 - gps-verify関数

## 問題: CORSエラーが発生している

### エラーメッセージ

```
Access to fetch at 'https://2bm71jvfs6.execute-api.us-east-1.amazonaws.com/dev/gps/verify' 
from origin 'https://semiemotionally-nonanarchistic-beverley.ngrok-free.dev' 
has been blocked by CORS policy: 
Response to preflight request doesn't pass access control check: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

### エラーの詳細

1. **Preflightリクエスト（OPTIONS）が失敗**
   - ブラウザが自動的に送信するOPTIONSリクエストにCORSヘッダーが返されていない
   - API Gatewayで`/gps/verify`エンドポイントにOPTIONSメソッドが設定されていない可能性が高い

2. **POSTリクエストも失敗**
   - Preflightが失敗したため、実際のPOSTリクエストも実行されない

### 原因

API Gatewayの`/gps/verify`エンドポイントで以下が不足しています：

1. **OPTIONSメソッドが作成されていない**
2. **CORS設定が有効化されていない**
3. **APIが再デプロイされていない**（設定変更が反映されていない）

---

## 解決手順

### 手順1: Lambda関数のコード確認（完了済み）

`backend/lambda/gps-verify/lambda_function.py`には既に以下が実装されています：

- ✅ OPTIONSリクエストの処理（行113-114）
- ✅ CORSヘッダーの設定（`response_utils.py`内）

### 手順2: Lambda関数をデプロイ（初回デプロイの場合）

もしまだ`gps-verify` Lambda関数をデプロイしていない場合：

1. **ZIPファイルを作成**
   ```bash
   cd backend/lambda/gps-verify
   ./build.sh
   ```

2. **Lambda関数を作成**
   - AWS Lambdaコンソールにアクセス
   - 「関数の作成」をクリック
   - **関数名**: `stamp-rally-gps-verify`
   - **ランタイム**: Python 3.11
   - 「関数の作成」をクリック

3. **ZIPファイルをアップロード**
   - 「コード」タブで「アップロード元」→「.zipファイル」を選択
   - `lambda-gps-verify.zip`をアップロード

4. **環境変数を設定**
   - 「設定」→「環境変数」→「編集」
   - 以下を追加:
     ```
     TABLE_STAMPMASTERS=StampMasters
     ```

5. **IAMロールの設定**
   - 「設定」→「アクセス権限」
   - DynamoDB読み取り権限を追加（StampMastersテーブル）

### 手順3: API Gatewayでリソースとメソッドを作成

#### 3-1. `/gps`リソースを作成（存在しない場合）

1. API Gatewayコンソールを開く
2. 対象のREST API（例: `stamp-rally-api`）を選択
3. 「リソース」→「アクション」→「リソースの作成」
4. **リソースパス**: `/gps`
5. 「リソースの作成」をクリック

#### 3-2. `/gps/verify`リソースを作成

1. 作成した`/gps`リソースを選択
2. 「アクション」→「リソースの作成」
3. **リソースパス**: `verify`
4. 「リソースの作成」をクリック

#### 3-3. POSTメソッドを追加

1. `/gps/verify`リソースを選択
2. 「アクション」→「メソッドの作成」→「POST」を選択
3. **統合タイプ**: Lambda関数
4. **Lambdaプロキシ統合を使用**: ✅ チェック
5. **Lambda関数**: `stamp-rally-gps-verify`を選択
6. 「保存」をクリック
7. 権限の追加を求められたら「OK」をクリック

### 手順4: API GatewayでCORSを有効化（重要）

#### 方法A: CORS有効化ウィザードを使用（推奨）

1. `/gps/verify`リソースを選択
2. 「アクション」→「CORSを有効化」をクリック
3. 以下の設定を確認:
   - **Access-Control-Allow-Origin**: `*` （開発環境）または特定のドメイン（本番環境）
   - **Access-Control-Allow-Headers**: `Content-Type,Authorization`
   - **Access-Control-Allow-Methods**: `POST,OPTIONS`
4. 「CORSを有効化して既存のCORSヘッダーを置き換える」をクリック

これにより、自動的にOPTIONSメソッドが作成されます。

#### 方法B: 手動でOPTIONSメソッドを作成

CORS有効化ウィザードを使わない場合：

1. `/gps/verify`リソースを選択
2. 「アクション」→「メソッドの作成」→「OPTIONS」を選択
3. **統合タイプ**: Lambda関数
4. **Lambdaプロキシ統合を使用**: ✅ チェック
5. **Lambda関数**: `stamp-rally-gps-verify`を選択
6. 「保存」をクリック

### 手順5: APIを再デプロイ（必須）

**重要**: 設定変更後は必ず再デプロイが必要です。

1. API Gatewayの左メニューで「アクション」をクリック
2. 「APIのデプロイ」を選択
3. **デプロイされるステージ**: `dev` を選択
4. **デプロイの説明**: `gps-verify CORS設定追加` など
5. 「デプロイ」をクリック

### 手順6: 動作確認

1. **ブラウザのキャッシュをクリア**（重要）
2. ページを再読み込み
3. GPS検証を試行
4. ブラウザのコンソールでエラーが解消されているか確認

---

## 確認手順

### 1. OPTIONSメソッドの確認

1. `/gps/verify`リソースを選択
2. 「OPTIONS」メソッドが存在することを確認
3. 「統合リクエスト」でLambda関数が正しく設定されていることを確認

### 2. POSTメソッドの確認

1. `/gps/verify`リソースを選択
2. 「POST」メソッドが存在することを確認
3. 「統合リクエスト」でLambda関数が正しく設定されていることを確認
4. **Lambdaプロキシ統合を使用**にチェックが入っていることを確認

### 3. CORSヘッダーの確認

1. `/gps/verify`リソース → POSTメソッドを選択
2. 「メソッドレスポンス」をクリック
3. 「200」レスポンスの「ヘッダー」を確認
4. 以下のヘッダーが含まれていることを確認:
   - `Access-Control-Allow-Origin`
   - `Access-Control-Allow-Headers`
   - `Access-Control-Allow-Methods`

### 4. curlコマンドでテスト

```bash
# OPTIONSリクエスト（preflight）のテスト
curl -X OPTIONS \
  -H "Origin: https://semiemotionally-nonanarchistic-beverley.ngrok-free.dev" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v \
  https://2bm71jvfs6.execute-api.us-east-1.amazonaws.com/dev/gps/verify
```

期待されるレスポンス:
- HTTPステータス: `200 OK`
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: POST,OPTIONS`
- `Access-Control-Allow-Headers: Content-Type,Authorization`

---

## トラブルシューティング

### 問題1: CORSエラーが解消されない

**確認事項**:
1. ✅ APIを再デプロイしたか（最も重要）
2. ✅ Lambda関数をデプロイしたか
3. ✅ OPTIONSメソッドが正しく作成されているか
4. ✅ 「Lambdaプロキシ統合を使用」にチェックが入っているか
5. ✅ ブラウザのキャッシュをクリアしたか

### 問題2: OPTIONSメソッドが作成できない

**対処法**:
1. **CORS有効化ウィザードを使用**すると自動的に作成されます（推奨）
2. または、手動でOPTIONSメソッドを作成

### 問題3: 「Lambdaプロキシ統合を使用」のチェックが重要

Lambdaプロキシ統合を使用しないと、Lambda関数が返すCORSヘッダーが正しくレスポンスに含まれません。

確認方法:
1. メソッドを選択
2. 「統合リクエスト」をクリック
3. 「Lambdaプロキシ統合を使用」にチェックが入っていることを確認

### 問題4: 再デプロイを忘れやすい

API Gatewayの設定変更は、**必ず再デプロイしないと反映されません**。

確認方法:
- 「アクション」→「APIのデプロイ」を実行
- デプロイ履歴で最新のデプロイ日時を確認

---

## クイックチェックリスト

- [ ] Lambda関数`stamp-rally-gps-verify`が作成されている
- [ ] Lambda関数に環境変数`TABLE_STAMPMASTERS`が設定されている
- [ ] Lambda関数にDynamoDB読み取り権限が設定されている
- [ ] API Gatewayで`/gps/verify`リソースが作成されている
- [ ] `/gps/verify`にPOSTメソッドが追加されている
- [ ] `/gps/verify`にOPTIONSメソッドが追加されている（CORS有効化で自動作成）
- [ ] POSTメソッドで「Lambdaプロキシ統合を使用」にチェックが入っている
- [ ] OPTIONSメソッドで「Lambdaプロキシ統合を使用」にチェックが入っている
- [ ] APIが再デプロイされている
- [ ] ブラウザのキャッシュをクリアした

---

## 注意事項

### Lambdaプロキシ統合の重要性

Lambdaプロキシ統合を使用しないと：
- Lambda関数が返す`statusCode`や`headers`が正しく処理されない
- CORSヘッダーがレスポンスに含まれない
- エラーハンドリングが正しく動作しない

**必ず「Lambdaプロキシ統合を使用」にチェックを入れてください。**

### デプロイの重要性

API Gatewayの設定を変更したら、**必ずAPIを再デプロイ**してください。
再デプロイしないと変更が反映されません。

### ブラウザキャッシュ

CORSエラーが解消されたように見えても、ブラウザのキャッシュが原因でエラーが続く場合があります。
必ずブラウザのキャッシュをクリアしてください。

---

**次のステップ**: 
1. Lambda関数をデプロイ（未デプロイの場合）
2. API Gatewayでリソースとメソッドを作成
3. CORSを有効化
4. APIを再デプロイ
5. 動作確認

