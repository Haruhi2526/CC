# CORSエラー詳細分析 - auth関数

## エラー概要

### 発生しているエラー

1. **CORSプリフライトエラー**
   ```
   Access to fetch at 'https://c5nmu4q3di.execute-api.us-east-1.amazonaws.com/dev/auth/verify' 
   from origin 'https://semiemotionally-nonanarchistic-beverley.ngrok-free.dev' 
   has been blocked by CORS policy: 
   Response to preflight request doesn't pass access control check: 
   No 'Access-Control-Allow-Origin' header is present on the requested resource.
   ```

2. **ネットワークエラー**
   ```
   Failed to load resource: net::ERR_FAILED
   ```

3. **アプリケーションエラー**
   ```
   認証API呼び出しエラー: Error: ネットワークエラーが発生しました。インターネット接続を確認してください。
   ```

---

## エラーの発生フロー

### 1. ブラウザの動作

```
[ブラウザ] 
  ↓
1. POST /auth/verify リクエストを送信しようとする
  ↓
2. CORSポリシーチェック: 異なるオリジンからのリクエストを検出
  ↓
3. プリフライトリクエスト（OPTIONS）を自動送信
   - Origin: https://semiemotionally-nonanarchistic-beverley.ngrok-free.dev
   - Access-Control-Request-Method: POST
   - Access-Control-Request-Headers: Content-Type,Authorization
  ↓
4. OPTIONSリクエストが失敗（CORSヘッダーなし）
  ↓
5. ブラウザがCORSエラーを発生
  ↓
6. 実際のPOSTリクエストは送信されない
```

### 2. フロントエンドのエラーハンドリング

```javascript
// api.js:49-50
const response = await fetch(url, fetchOptions);
// ↑ ここでCORSエラーが発生

// api.js:123-128
catch (error) {
    // ネットワークエラーなどの場合
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
        throw new Error('ネットワークエラーが発生しました。インターネット接続を確認してください。');
    }
    throw error;
}
```

**問題点**: CORSエラーは`TypeError`としてキャッチされ、「ネットワークエラー」として表示されるため、実際の原因（CORS設定不足）が分かりにくい。

### 3. エラーの伝播

```
api.js:50 (fetch失敗)
  ↓
api.js:126 (TypeErrorをキャッチ → ネットワークエラーメッセージ)
  ↓
api.js:186 (auth関数でエラーをログ出力)
  ↓
app.js:230 (handleLoggedInでエラーをキャッチ)
  ↓
app.js:292 (エラーログ出力)
  ↓
app.js:37 (showErrorでユーザーに表示)
```

---

## 根本原因の分析

### 原因1: API GatewayでOPTIONSメソッドが設定されていない

**確認方法**:
1. API Gatewayコンソールで`/auth`リソースを確認
2. OPTIONSメソッドが存在するか確認

**問題**: OPTIONSメソッドがない場合、プリフライトリクエストが404エラーまたはCORSヘッダーなしのレスポンスを返す

### 原因2: CORS設定が有効化されていない

**確認方法**:
1. API Gatewayコンソールで`/auth`リソースを選択
2. 「アクション」→「CORSを有効化」が実行されているか確認

**問題**: CORSが有効化されていない場合、OPTIONSメソッドがあっても適切なCORSヘッダーが返されない

### 原因3: APIが再デプロイされていない

**確認方法**:
1. API Gatewayコンソールで「アクション」→「APIのデプロイ」を確認
2. 最後のデプロイ時刻を確認

**問題**: CORS設定を変更しても、APIを再デプロイしないと変更が反映されない

### 原因4: Lambdaプロキシ統合が有効になっていない

**確認方法**:
1. `/auth`リソース → OPTIONSメソッド → 「統合リクエスト」を確認
2. 「Lambdaプロキシ統合を使用」にチェックが入っているか確認

**問題**: Lambdaプロキシ統合が無効の場合、Lambda関数が返すCORSヘッダーがレスポンスに含まれない

---

## エラーメッセージの詳細

### 1. CORSプリフライトエラー

```
Access to fetch at '...' has been blocked by CORS policy: 
Response to preflight request doesn't pass access control check: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

**意味**:
- ブラウザがOPTIONSリクエストを送信した
- レスポンスに`Access-Control-Allow-Origin`ヘッダーが含まれていない
- ブラウザがCORSポリシー違反としてリクエストをブロック

### 2. ネットワークエラー

```
Failed to load resource: net::ERR_FAILED
```

**意味**:
- fetch APIがリクエストを送信しようとしたが失敗
- CORSエラーにより、ブラウザがリクエストをブロックした結果

### 3. アプリケーションエラーメッセージ

```
ネットワークエラーが発生しました。インターネット接続を確認してください。
```

**問題点**:
- 実際の原因はCORS設定不足だが、エラーメッセージが「ネットワークエラー」となっている
- ユーザーに誤解を与える可能性がある

---

## 解決方法

### 即座に実行すべき手順

1. **API GatewayでCORSを有効化**
   - `/auth`リソースを選択
   - 「アクション」→「CORSを有効化」
   - 設定:
     - `Access-Control-Allow-Origin`: `*`
     - `Access-Control-Allow-Headers`: `Content-Type,Authorization`
     - `Access-Control-Allow-Methods`: `POST,OPTIONS`

2. **APIを再デプロイ**
   - 「アクション」→「APIのデプロイ」
   - ステージ: `dev`

3. **動作確認**
   - ブラウザのキャッシュをクリア
   - ページを再読み込み

詳細な手順は [CORS設定修正手順-auth関数.md](./CORS設定修正手順-auth関数.md) を参照してください。

---

## エラーハンドリングの改善提案

### 現在の問題

```javascript
// api.js:123-128
catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
        throw new Error('ネットワークエラーが発生しました。インターネット接続を確認してください。');
    }
    throw error;
}
```

CORSエラーも`TypeError`としてキャッチされるため、実際の原因が分かりにくい。

### 改善案

```javascript
catch (error) {
    // CORSエラーの検出
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
        // CORSエラーの可能性をチェック
        if (error.message.includes('CORS') || 
            error.message.includes('Access-Control')) {
            throw new Error('CORSエラーが発生しました。API GatewayのCORS設定を確認してください。');
        }
        throw new Error('ネットワークエラーが発生しました。インターネット接続を確認してください。');
    }
    throw error;
}
```

---

## チェックリスト

### API Gatewayの設定確認

- [ ] `/auth`リソースが存在する
- [ ] `/auth`リソースにPOSTメソッドが設定されている
- [ ] `/auth`リソースにOPTIONSメソッドが設定されている
- [ ] OPTIONSメソッドで「Lambdaプロキシ統合を使用」にチェックが入っている
- [ ] CORSが有効化されている
- [ ] APIが`dev`ステージにデプロイされている

### Lambda関数の確認

- [ ] `lambda_function.py`にOPTIONSリクエストの処理が実装されている（134-136行目）
- [ ] `response_utils.py`にCORSヘッダーが含まれている（19-21行目）

### 動作確認

- [ ] curlコマンドでOPTIONSリクエストが成功する
- [ ] ブラウザのキャッシュをクリアした
- [ ] ブラウザでCORSエラーが解消された
- [ ] 認証が正常に動作する

---

## 参考情報

- [CORS設定修正手順-auth関数.md](./CORS設定修正手順-auth関数.md) - 詳細な修正手順
- [AWS-Console実装手順-auth関数.md](./AWS-Console実装手順-auth関数.md) - auth関数の実装手順
- [CORS設定修正手順.md](./CORS設定修正手順.md) - stamps関数のCORS設定手順

