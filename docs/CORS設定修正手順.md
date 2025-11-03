# CORS設定修正手順 - stamps関数

## 問題: CORSエラーが発生している

### エラーメッセージ
```
Access to fetch at '...' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

### 原因
API Gatewayの`/stamps`エンドポイントでCORS設定が不十分です。

---

## 解決手順

### 手順1: stamps関数のコードを更新（完了済み）

`lambda_function.py`にOPTIONSリクエストの処理を追加しました。

### 手順2: Lambda関数を再デプロイ

1. ZIPファイルを再作成
   ```bash
   cd backend/lambda/stamps
   # 既存のbuild.shがあれば実行、なければ手動でZIP作成
   zip -r lambda-stamps.zip lambda_function.py dynamodb_utils.py response_utils.py
   ```

2. Lambda関数を更新
   - AWS Lambdaコンソールで`stamp-rally-stamps`関数を開く
   - 「コード」タブで「アップロード元」→「.zipファイル」を選択
   - 作成したZIPファイルをアップロード

### 手順3: API GatewayでOPTIONSメソッドを追加

1. API Gatewayコンソールを開く
2. 対象のREST APIを選択
3. `/stamps`リソースを選択
4. 「アクション」→「メソッドの作成」→「OPTIONS」を選択
5. **統合タイプ**: Lambda関数
6. **Lambda関数**: `stamp-rally-stamps`を選択
7. 「保存」をクリック

### 手順4: API GatewayでCORSを有効化（推奨）

#### 方法A: CORS有効化ウィザードを使用（簡単）

1. `/stamps`リソースを選択
2. 「アクション」→「CORSを有効化」をクリック
3. 以下の設定を確認:
   - **Access-Control-Allow-Origin**: `*` （開発環境）または特定のドメイン
   - **Access-Control-Allow-Headers**: `Content-Type,Authorization`
   - **Access-Control-Allow-Methods**: `GET,OPTIONS`
4. 「CORSを有効化して既存のCORSヘッダーを置き換える」をクリック

これにより、自動的にOPTIONSメソッドが作成されます。

#### 方法B: 手動でOPTIONSメソッドを作成（上記手順3）

### 手順5: APIを再デプロイ

**重要**: 設定変更後は必ず再デプロイが必要です。

1. 「アクション」→「APIのデプロイ」
2. **デプロイされるステージ**: `dev` を選択
3. 「デプロイ」をクリック

---

## 確認手順

### 1. OPTIONSメソッドの確認

1. `/stamps`リソースを選択
2. 「OPTIONS」メソッドが存在することを確認
3. 「統合リクエスト」でLambda関数が正しく設定されていることを確認

### 2. CORSヘッダーの確認

1. `/stamps`リソース → GETメソッドを選択
2. 「メソッドレスポンス」をクリック
3. 「200」レスポンスの「ヘッダー」を確認
4. 以下のヘッダーが含まれていることを確認:
   - `Access-Control-Allow-Origin`
   - `Access-Control-Allow-Headers`
   - `Access-Control-Allow-Methods`

### 3. 動作確認

1. ページを再読み込み
2. ブラウザのコンソールでCORSエラーが解消されているか確認
3. スタンプ一覧が表示されるか確認

---

## トラブルシューティング

### 問題1: CORSエラーが解消されない

**確認事項**:
1. APIを再デプロイしたか
2. Lambda関数を再アップロードしたか
3. OPTIONSメソッドが正しく作成されているか
4. ブラウザのキャッシュをクリア

### 問題2: OPTIONSメソッドが作成できない

**対処法**:
1. CORS有効化ウィザードを使用すると自動的に作成されます
2. または、手動でOPTIONSメソッドを作成

### 問題3: 複数のエンドポイントでCORSエラーが発生する

**対処法**:
- `/auth`、`/stamps`、`/stamps/award`の各リソースでCORS設定を確認
- 各リソースで「CORSを有効化」を実行

---

## 注意事項

### Lambdaプロキシ統合の確認

OPTIONSメソッドでも「Lambdaプロキシ統合を使用」にチェックを入れてください。

### デプロイの重要性

設定を変更したら、必ずAPI GatewayでAPIを再デプロイしてください。再デプロイしないと変更が反映されません。

---

**次のステップ**: 
1. stamps関数のZIPファイルを再作成
2. Lambda関数を更新
3. API GatewayでCORS設定
4. APIを再デプロイ
5. 動作確認

