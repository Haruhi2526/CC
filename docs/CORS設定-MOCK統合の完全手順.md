# CORS設定 - OPTIONSメソッドをMOCK統合に変更した場合の完全手順

## ✅ 現在の状況

OPTIONSメソッドをMOCK統合に変更しました。次に、CORSヘッダーを正しく返すための設定が必要です。

---

## 🔧 完全な設定手順

### ステップ1: メソッドレスポンスにCORSヘッダーを追加

1. **API Gatewayコンソールを開く**
   - AWSマネジメントコンソール → API Gateway

2. **対象のREST APIを選択**

3. **`/auth`リソース → 「OPTIONS」メソッドを選択**

4. **「メソッドレスポンス」をクリック**

5. **「200」レスポンスを展開**

6. **「ヘッダー」セクションで「ヘッダーの追加」をクリック**

7. **以下の3つのヘッダーを追加**:
   - `Access-Control-Allow-Origin`
   - `Access-Control-Allow-Headers`
   - `Access-Control-Allow-Methods`

8. **各ヘッダーの設定**:
   - `Access-Control-Allow-Origin`: チェックボックスをオンにする
   - `Access-Control-Allow-Headers`: チェックボックスをオンにする
   - `Access-Control-Allow-Methods`: チェックボックスをオンにする

9. **「保存」をクリック**

### ステップ2: 統合レスポンスでヘッダーマッピングを設定

1. **「統合レスポンス」をクリック**

2. **「200」レスポンスを展開**

3. **「ヘッダーマッピング」セクションで以下を設定**:

   | マッピング先 | マッピング値 |
   |------------|------------|
   | `method.response.header.Access-Control-Allow-Origin` | `'*'` |
   | `method.response.header.Access-Control-Allow-Headers` | `'Content-Type,Authorization'` |
   | `method.response.header.Access-Control-Allow-Methods` | `'POST,OPTIONS'` |

   **重要**: 値は**シングルクォートで囲む**必要があります。

4. **「マッピングテンプレート」セクションで以下を設定**:
   - **コンテンツタイプ**: `application/json` を選択
   - **テンプレート**: `{}`（空のJSONオブジェクト）を入力

5. **「保存」をクリック**

### ステップ3: APIを再デプロイ（必須）

1. **「アクション」→「APIのデプロイ」**

2. **デプロイされるステージ**: `dev` を選択

3. **デプロイの説明**: `OPTIONS MOCK統合 CORS設定` など（任意）

4. **「デプロイ」をクリック**

5. **デプロイが完了するまで待つ（数秒）**

---

## 🧪 動作確認

### curlコマンドでテスト

```bash
curl -X OPTIONS \
  -H "Origin: https://semiemotionally-nonanarchistic-beverley.ngrok-free.dev" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization" \
  -i https://c5nmu4q3di.execute-api.us-east-1.amazonaws.com/dev/auth/verify
```

### 期待される成功レスポンス

```
HTTP/2 200 
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: POST,OPTIONS
Access-Control-Allow-Headers: Content-Type,Authorization
Content-Type: application/json
```

### 失敗時の確認ポイント

もしCORSヘッダーが返されない場合、以下を確認：

1. **メソッドレスポンスのヘッダー設定**
   - `Access-Control-Allow-Origin`、`Access-Control-Allow-Headers`、`Access-Control-Allow-Methods`が追加されているか

2. **統合レスポンスのヘッダーマッピング**
   - マッピング値がシングルクォートで囲まれているか（例: `'*'`）
   - マッピング先が正しいか（`method.response.header.`で始まる）

3. **APIの再デプロイ**
   - 設定変更後、必ずAPIを再デプロイしたか

---

## 📋 設定チェックリスト

### メソッドレスポンス

- [ ] 「200」レスポンスが存在する
- [ ] `Access-Control-Allow-Origin`ヘッダーが追加されている
- [ ] `Access-Control-Allow-Headers`ヘッダーが追加されている
- [ ] `Access-Control-Allow-Methods`ヘッダーが追加されている

### 統合レスポンス

- [ ] 「200」レスポンスが存在する
- [ ] ヘッダーマッピングが設定されている:
  - [ ] `method.response.header.Access-Control-Allow-Origin` → `'*'`
  - [ ] `method.response.header.Access-Control-Allow-Headers` → `'Content-Type,Authorization'`
  - [ ] `method.response.header.Access-Control-Allow-Methods` → `'POST,OPTIONS'`
- [ ] マッピングテンプレートが設定されている:
  - [ ] コンテンツタイプ: `application/json`
  - [ ] テンプレート: `{}`

### デプロイ

- [ ] APIを`dev`ステージに再デプロイした

### 動作確認

- [ ] curlコマンドでOPTIONSリクエストが200を返す
- [ ] レスポンスにCORSヘッダーが含まれている
- [ ] ブラウザのキャッシュをクリアした
- [ ] ブラウザでCORSエラーが解消された

---

## 🚨 よくある間違い

### 間違い1: ヘッダーマッピングの値にシングルクォートを付けていない

❌ **間違い**: `*`（シングルクォートなし）
✅ **正しい**: `'*'`（シングルクォートあり）

### 間違い2: メソッドレスポンスにヘッダーを追加していない

❌ **間違い**: 統合レスポンスのヘッダーマッピングだけ設定
✅ **正しい**: メソッドレスポンスと統合レスポンスの両方で設定

### 間違い3: APIを再デプロイしていない

❌ **間違い**: 設定を変更したが、APIを再デプロイしていない
✅ **正しい**: 設定変更後、必ずAPIを再デプロイ

### 間違い4: マッピングテンプレートを設定していない

❌ **間違い**: ヘッダーマッピングだけ設定
✅ **正しい**: ヘッダーマッピングとマッピングテンプレートの両方を設定

---

## 📸 設定画面のイメージ

### メソッドレスポンスの設定

```
メソッドレスポンス
└── 200
    └── ヘッダー
        ├── Access-Control-Allow-Origin ✓
        ├── Access-Control-Allow-Headers ✓
        └── Access-Control-Allow-Methods ✓
```

### 統合レスポンスの設定

```
統合レスポンス
└── 200
    ├── ヘッダーマッピング
    │   ├── method.response.header.Access-Control-Allow-Origin → '*'
    │   ├── method.response.header.Access-Control-Allow-Headers → 'Content-Type,Authorization'
    │   └── method.response.header.Access-Control-Allow-Methods → 'POST,OPTIONS'
    └── マッピングテンプレート
        └── application/json → {}
```

---

## 💡 次のステップ

1. **メソッドレスポンスにCORSヘッダーを追加**
2. **統合レスポンスでヘッダーマッピングを設定**
3. **マッピングテンプレートを設定**
4. **APIを再デプロイ**
5. **動作確認**

---

## 📚 参考ドキュメント

- [CORSエラー-Lambda関数名変更が原因の場合の解決方法.md](./CORSエラー-Lambda関数名変更が原因の場合の解決方法.md)
- [CORSエラー-500エラーの解決方法.md](./CORSエラー-500エラーの解決方法.md)
- [CORSエラー診断と解決チェックリスト.md](./CORSエラー診断と解決チェックリスト.md)

