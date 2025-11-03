# LIFFログイン400 Bad Requestエラー解決手順

## エラー内容

```
GET https://access.line.me/oauth2/v2.1/error400?error=Bad%20Request&error_descr...
400 (Bad Request)
```

このエラーは、LIFFアプリのログイン処理でLINEの認証サーバーにリダイレクトされた際に発生します。

## 原因

**リダイレクトURIがLINE Developersコンソールに登録されているエンドポイントURLと一致していない**

ngrokを使用している場合、以下の理由でURLが一致しなくなることがあります：
1. ngrokの無料プランでは、URLが毎回変わる
2. ngrokを再起動すると、URLが変更される
3. LINE Developersコンソールの設定を更新していない

## 解決手順

### 手順1: 現在のngrok URLを確認

1. ngrokを起動しているターミナルを確認
2. 表示されているHTTPS URLを確認（例: `https://xxxx-xxx-xxx-xxx.ngrok-free.app`）
3. **完全なエンドポイントURLを確認**（例: `https://xxxx-xxx-xxx-xxx.ngrok-free.app/index.html`）

### 手順2: LINE DevelopersコンソールでエンドポイントURLを確認・更新

1. [LINE Developersコンソール](https://developers.line.biz/console/)にログイン
2. プロバイダーを選択
3. チャネル（LIFFアプリ）を選択
4. 「LIFF」タブをクリック
5. LIFFアプリを選択
6. **「エンドポイントURL」を確認**
   - 現在のngrok URLと一致しているか確認
   - 形式: `https://xxxx-xxx-xxx-xxx.ngrok-free.app/index.html`
   - **重要**: `/index.html`まで含めること

### 手順3: エンドポイントURLを更新（不一致の場合）

1. 「エンドポイントURL」を編集
2. 現在のngrok URLを入力（例: `https://xxxx-xxx-xxx-xxx.ngrok-free.app/index.html`）
3. **注意**: 
   - 必ずHTTPSを使用
   - `/index.html`まで含める
   - ngrokのURLが変更された場合は、必ず更新する
4. 「更新」ボタンをクリック
5. 設定が反映されるまで数秒待つ

### 手順4: ブラウザのキャッシュをクリア

1. ブラウザの開発者ツールを開く（F12）
2. リロードボタンを右クリック
3. 「キャッシュの消去とハード再読み込み」を選択
4. または、シークレット/プライベートモードでアクセス

### 手順5: 再度ログインを試す

1. LINEアプリからLIFFアプリを開く
2. 「LINEでログイン」ボタンをクリック
3. エラーが解消されているか確認

## 確認項目チェックリスト

- [ ] ngrokが起動しているか
- [ ] ngrokのHTTPS URLを確認したか
- [ ] LINE DevelopersコンソールのエンドポイントURLと現在のngrok URLが一致しているか
- [ ] エンドポイントURLに`/index.html`が含まれているか（重要: `/`で終わっていないか確認）
- [ ] エンドポイントURLがHTTPSで始まっているか
- [ ] エンドポイントURLに末尾スラッシュ（`/`）が含まれていないか確認
- [ ] 設定を保存したか
- [ ] ブラウザのキャッシュをクリアしたか

## 重要な注意事項

### エンドポイントURLの形式

**正しい形式**:
```
https://xxxx-xxx-xxx-xxx.ngrok-free.app/index.html
```

**間違った形式**:
```
https://xxxx-xxx-xxx-xxx.ngrok-free.app/          ❌（末尾スラッシュ）
https://xxxx-xxx-xxx-xxx.ngrok-free.app           ❌（/index.htmlがない）
```

LIFFアプリでは、エンドポイントURLは必ず `/index.html` で終わる必要があります。

## トラブルシューティング

### 問題1: ngrokのURLが頻繁に変わる

**解決策**: 
- ngrokの有料プランを使用すると、固定ドメインを使用できます
- または、ngrokを再起動するたびにLINE Developersコンソールを更新

### 問題2: エンドポイントURLを更新してもエラーが続く

**確認事項**:
1. 設定を保存したか（「更新」ボタンをクリックしたか）
2. 数秒待ってから再度試しているか（設定反映に時間がかかる場合がある）
3. ブラウザのキャッシュをクリアしたか
4. ngrokが正常に動作しているか（ngrokのWebインターフェース: http://127.0.0.1:4040 で確認）

### 問題3: 外部ブラウザからアクセスしている

**注意**: 
- LINEアプリ内からアクセスすることを推奨
- 外部ブラウザからアクセスする場合、リダイレクトURIの設定が複雑になる場合がある

## デバッグ方法

ブラウザのコンソールで以下を確認：

```javascript
// 現在のURLを確認
console.log('現在のURL:', window.location.href);

// LIFFアプリの設定を確認
console.log('LIFF ID:', CONFIG.LIFF_ID);
console.log('LINEアプリ内:', liff.isInClient());
```

## 参考

- [ngrok動作確認手順](./ngrok動作確認手順.md)
- [LIFFアプリ基本構造作成手順](./LIFFアプリ基本構造作成手順.md)
- [LINE Developers公式ドキュメント](https://developers.line.biz/ja/docs/liff/)

