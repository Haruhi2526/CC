# CORSエラー解決手順 - 即座に実行

## 🔴 現在のエラー状況

### エラーメッセージ
```
Access to fetch at 'https://c5nmu4q3di.execute-api.us-east-1.amazonaws.com/dev/auth/verify' 
from origin 'https://semiemotionally-nonanarchistic-beverley.ngrok-free.dev' 
has been blocked by CORS policy: 
Response to preflight request doesn't pass access control check: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

### エラーの流れ

1. **ブラウザがOPTIONSリクエストを送信**（プリフライト）
   - オリジン: `https://semiemotionally-nonanarchistic-beverley.ngrok-free.dev`
   - エンドポイント: `/dev/auth/verify`

2. **API GatewayがCORSヘッダーを返さない**
   - `Access-Control-Allow-Origin`ヘッダーが存在しない
   - OPTIONSメソッドが設定されていない可能性

3. **ブラウザがリクエストをブロック**
   - 実際のPOSTリクエストは送信されない
   - `net::ERR_FAILED`エラーが発生

4. **アプリケーションがエラーを表示**
   - 改善されたエラーメッセージが表示されている（✅ 正常動作）

---

## ✅ 即座に実行すべき解決手順

### 手順1: API Gatewayコンソールを開く

1. AWSマネジメントコンソールにログイン
2. 「API Gateway」を検索して開く
3. 対象のREST APIを選択（例: `stamp-rally-api`）

### 手順2: `/auth`リソースでCORSを有効化

1. 左側の「リソース」から `/auth` リソースを選択
   - ⚠️ **重要**: `/auth/verify`ではなく、親リソースの`/auth`を選択

2. 「アクション」ドロップダウンメニューをクリック

3. 「CORSを有効化」を選択

4. 以下の設定を入力:
   ```
   Access-Control-Allow-Origin: *
   Access-Control-Allow-Headers: Content-Type,Authorization
   Access-Control-Allow-Methods: POST,OPTIONS
   ```

5. 「CORSを有効化して既存のCORSヘッダーを置き換える」をクリック

6. 確認ダイアログで「はい、既存の値を置き換えます」をクリック

### 手順3: APIを再デプロイ（必須）

**⚠️ 重要**: CORS設定を変更した後は、必ずAPIを再デプロイする必要があります。

1. 「アクション」ドロップダウンメニューをクリック

2. 「APIのデプロイ」を選択

3. 以下の設定を確認:
   - **デプロイされるステージ**: `dev` を選択
   - **デプロイの説明**: `auth CORS設定追加` など（任意）

4. 「デプロイ」をクリック

5. デプロイが完了するまで待つ（数秒）

### 手順4: 動作確認

1. **ブラウザのキャッシュをクリア**
   - Chrome/Edge: `Ctrl+Shift+Delete` (Windows) または `Cmd+Shift+Delete` (Mac)
   - または、シークレットモードでテスト

2. **ページを再読み込み**
   - `F5` または `Ctrl+R` (Windows) / `Cmd+R` (Mac)

3. **ブラウザのコンソールを確認**
   - `F12` で開発者ツールを開く
   - 「Console」タブでCORSエラーが解消されているか確認

4. **認証が正常に動作するか確認**

---

## 🔍 トラブルシューティング

### 問題1: CORSエラーが解消されない

**確認事項**:
- [ ] `/auth`リソースでCORSを有効化したか（`/auth/verify`ではない）
- [ ] APIを`dev`ステージに再デプロイしたか
- [ ] ブラウザのキャッシュをクリアしたか
- [ ] OPTIONSメソッドが作成されているか（CORS有効化で自動作成される）

**確認方法**:
1. `/auth`リソースを選択
2. 「OPTIONS」メソッドが存在することを確認
3. OPTIONSメソッドの「統合リクエスト」で「Lambdaプロキシ統合を使用」にチェックが入っていることを確認

### 問題2: OPTIONSメソッドが作成されていない

**対処法**:
1. CORS有効化ウィザードを再度実行
2. または、手動でOPTIONSメソッドを作成:
   - `/auth`リソースを選択
   - 「アクション」→「メソッドの作成」→「OPTIONS」
   - 統合タイプ: Lambda関数
   - Lambda関数: `stamp-rally-auth`
   - 「Lambdaプロキシ統合を使用」にチェック
   - 「保存」をクリック

### 問題3: APIを再デプロイしていない

**症状**: CORS設定を変更したが、エラーが続く

**対処法**:
- 必ず「アクション」→「APIのデプロイ」を実行
- デプロイしないと設定変更が反映されません

### 問題4: ブラウザのキャッシュ

**症状**: 設定を変更したが、まだエラーが表示される

**対処法**:
1. ブラウザのキャッシュを完全にクリア
2. シークレットモードでテスト
3. 開発者ツールで「キャッシュを無効にする」を有効化

---

## 📋 チェックリスト

### API Gatewayの設定

- [ ] `/auth`リソースが存在する
- [ ] `/auth`リソースにPOSTメソッドが設定されている
- [ ] `/auth`リソースにOPTIONSメソッドが設定されている（CORS有効化で自動作成）
- [ ] OPTIONSメソッドで「Lambdaプロキシ統合を使用」にチェックが入っている
- [ ] CORSが有効化されている
- [ ] APIが`dev`ステージにデプロイされている

### 動作確認

- [ ] ブラウザのキャッシュをクリアした
- [ ] ページを再読み込みした
- [ ] ブラウザのコンソールでCORSエラーが解消された
- [ ] 認証が正常に動作する

---

## 🧪 テスト方法

### curlコマンドでOPTIONSリクエストをテスト

```bash
curl -X OPTIONS \
  -H "Origin: https://semiemotionally-nonanarchistic-beverley.ngrok-free.dev" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization" \
  -v \
  https://c5nmu4q3di.execute-api.us-east-1.amazonaws.com/dev/auth/verify
```

**成功時のレスポンス例**:
```
< HTTP/1.1 200 OK
< Access-Control-Allow-Origin: *
< Access-Control-Allow-Methods: POST,OPTIONS
< Access-Control-Allow-Headers: Content-Type,Authorization
```

### ブラウザの開発者ツールで確認

1. `F12`で開発者ツールを開く
2. 「Network」タブを選択
3. ページを再読み込み
4. `/auth/verify`リクエストを確認
5. OPTIONSリクエストが成功しているか確認
6. レスポンスヘッダーにCORSヘッダーが含まれているか確認

---

## 📚 参考ドキュメント

- [CORS設定修正手順-auth関数.md](./CORS設定修正手順-auth関数.md) - 詳細な修正手順
- [CORSエラー詳細分析-auth関数.md](./CORSエラー詳細分析-auth関数.md) - エラーの詳細分析
- [AWS-Console実装手順-auth関数.md](./AWS-Console実装手順-auth関数.md) - auth関数の実装手順

---

## ⚡ クイックリファレンス

### 最も重要な3つのステップ

1. **API Gatewayで`/auth`リソースを選択**
2. **「アクション」→「CORSを有効化」**
3. **「アクション」→「APIのデプロイ」→ ステージ: `dev`**

これでCORSエラーが解消されるはずです！

