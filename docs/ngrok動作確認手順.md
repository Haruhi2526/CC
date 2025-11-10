# ngrokを使用したLIFFアプリ動作確認手順

## 概要

ngrokを使用してローカル開発サーバーを公開し、LIFFアプリの動作確認を行います。

---

## 前提条件

### 必要なツール
- Python 3.x（ローカルサーバー起動用）
- ngrok（インストール済みであること）

### ngrokのインストール（未インストールの場合）

#### macOSの場合
```bash
# Homebrewでインストール
brew install ngrok/ngrok/ngrok

# または、公式サイトからダウンロード
# https://ngrok.com/download
```

#### ngrokアカウントのセットアップ
1. [ngrok公式サイト](https://ngrok.com/)でアカウント作成
2. 認証トークンを取得
3. トークンを設定:
   ```bash
   ngrok config add-authtoken YOUR_AUTH_TOKEN
   ```

---

## 手順1: ローカルサーバーの起動

### 1-1. ディレクトリに移動

```bash
cd /Users/takenouchiharuhi/Downloads/CC/frontend/liff-app
```

### 1-2. Python HTTPサーバーを起動

```bash
# Python 3の場合
python3 -m http.server 8000

# または、ポートを指定
python3 -m http.server 8080
```

サーバーが起動すると、以下のメッセージが表示されます:
```
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

**注意**: このターミナルは開いたままにしてください。

---

## 手順2: ngrokでローカルサーバーを公開

### 2-1. 新しいターミナルを開く

ローカルサーバーとは別のターミナルウィンドウを開きます。

### 2-2. ngrokでトンネルを作成

```bash
# ポート8000で公開する場合
ngrok http 8000

# または、カスタムサブドメインを使用する場合（有料プランの場合）
ngrok http 8000 --subdomain=your-custom-subdomain
```

ngrokが起動すると、以下のような情報が表示されます:

```
ngrok

Session Status                online
Account                       Your Name (Plan: Free)
Version                       3.x.x
Region                        Japan (jp)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://xxxx-xxx-xxx-xxx.ngrok-free.app -> http://localhost:8000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

### 2-3. 公開URLを確認

重要: **HTTPSのURL**（`https://xxxx-xxx-xxx-xxx.ngrok-free.app`）をコピーします。

**注意**: 
- 無料プランの場合、URLは毎回変わります
- HTTPSが必須です（LIFFはHTTPSのみ対応）
- ngrokのWebインターフェース（http://127.0.0.1:4040）でリクエストを確認できます

---

## 手順3: LINE DevelopersコンソールでLIFF URLを設定

### 3-1. LINE Developersコンソールを開く

1. [LINE Developers](https://developers.line.biz/console/)にログイン
2. プロバイダーを選択
3. チャネル（LIFFアプリ）を選択

### 3-2. LIFFアプリの設定

1. 「LIFF」タブをクリック
2. LIFFアプリを選択（または新規作成）
3. 「エンドポイントURL」を以下の形式で設定:
   ```
   https://xxxx-xxx-xxx-xxx.ngrok-free.app/index.html
   ```
   （ngrokで取得したHTTPS URL + `/index.html`）

### 3-3. 設定を保存

「更新」または「追加」ボタンをクリックして保存します。

---

## 手順4: LINEアプリから動作確認

### 4-1. LINEアプリでアクセス

1. LINEアプリを開く
2. 「ホーム」タブ → 「その他」→「LINEアプリ」→「追加」
3. LIFFアプリを検索して追加
4. または、チャットボットからLIFFアプリのURLを送信してアクセス

### 4-2. 動作確認項目

#### ローディング画面
- [ ] アプリを開くとローディング表示が表示される

#### ログイン画面
- [ ] 未ログイン状態で「LINEでログイン」ボタンが表示される
- [ ] ログインボタンをクリックするとLINEログイン画面に遷移する

#### 認証処理
- [ ] ログイン後に認証APIが呼び出される
- [ ] エラーなく認証が完了する
- [ ] セッショントークンが保存される（開発者ツールで確認）

#### ホーム画面
- [ ] ログイン後にホーム画面が表示される
- [ ] ユーザー情報が表示される
- [ ] スタンプ一覧エリアが表示される

#### スタンプ一覧
- [ ] スタンプ一覧APIが呼び出される
- [ ] スタンプが表示される（または「スタンプがありません」と表示される）

---

## トラブルシューティング

### 問題1: ngrokが起動しない

**原因**: ngrokがインストールされていない、または認証トークンが設定されていない

**解決方法**:
```bash
# ngrokのバージョンを確認
ngrok version

# 認証トークンを設定
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### 問題2: 「ngrok-free.app」の警告ページが表示される

**原因**: ngrokの無料プランでは、初回アクセス時に警告ページが表示される

**解決方法**:
1. 警告ページで「Visit Site」ボタンをクリック
2. または、ngrokの設定で警告ページを無効化（有料プランの場合）

### 問題3: CORSエラーが発生する

**原因**: API GatewayのCORS設定やngrokの設定の問題

**確認項目**:
- API GatewayのCORS設定が正しいか
- ngrokのHTTPS URLを使用しているか
- ブラウザのコンソールでエラーメッセージを確認

### 問題4: ERR_NGROK_3200 - エンドポイントがオフライン

**原因**: ngrokエージェントが起動していない、またはセッションが切れている

**エラーメッセージ例**:
```
ERR_NGROK_3200
The endpoint nonactinically-uninscribed-griffin.ngrok-free.dev is offline.
```

**解決方法**:

1. **ngrokが起動しているか確認**
   ```bash
   # ターミナルでngrokプロセスを確認
   ps aux | grep ngrok
   ```

2. **ngrokを再起動**
   - 既存のngrokプロセスを停止（Ctrl+C）
   - 新しいターミナルでngrokを起動:
     ```bash
     ngrok http 8000
     ```

3. **新しいURLを確認**
   - ngrok起動時に表示される新しいHTTPS URLをコピー
   - 例: `https://xxxx-xxx-xxx-xxx.ngrok-free.app`

4. **LINE DevelopersコンソールでURLを更新**
   - 新しいngrok URL + `/index.html` を設定
   - 例: `https://xxxx-xxx-xxx-xxx.ngrok-free.app/index.html`

5. **ローカルサーバーが起動しているか確認**
   ```bash
   # 別のターミナルで確認
   cd frontend/liff-app
   python3 -m http.server 8000
   ```

6. **ngrokダッシュボードで確認**（オプション）
   - [ngrokダッシュボード](https://dashboard.ngrok.com/endpoints)にログイン
   - アクティブなエンドポイントを確認

### 問題5: LIFFアプリが表示されない

**原因**: URLの設定ミスやngrokの接続が切れている

**確認項目**:
1. LINE DevelopersコンソールのLIFF URLが正しいか
2. ngrokが起動しているか（ターミナルを確認）
3. ローカルサーバーが起動しているか
4. ngrokのWebインターフェース（http://127.0.0.1:4040）でリクエストが来ているか確認

### 問題6: 認証APIが失敗する

**原因**: APIエンドポイントのURLやIDトークンの問題

**確認方法**:
1. ブラウザの開発者ツール（F12）でネットワークタブを確認
2. API呼び出しのリクエスト/レスポンスを確認
3. エラーメッセージを確認

---

## ngrokの便利な機能

### Webインターフェース

ngrok起動時に表示されるWebインターフェース（http://127.0.0.1:4040）では:
- すべてのHTTPリクエストを確認できる
- リクエスト/レスポンスの詳細を確認できる
- リクエストをリプレイできる

### リクエストインスペクション

開発中は以下のオプションで詳細なログを確認:
```bash
ngrok http 8000 --log=stdout
```

---

## セキュリティ注意事項

### 開発環境のみで使用

- ngrokは開発環境でのみ使用してください
- 本番環境では適切なホスティングサービスを使用してください

### 認証トークンの保護

- ngrokの認証トークンは機密情報です
- Gitにコミットしないでください
- 環境変数や設定ファイルで管理してください

---

## 次のステップ

動作確認が完了したら:

1. **機能追加**: GPSスタンプ画面、カメラスタンプ画面の実装
2. **エラーハンドリングの改善**: より詳細なエラーメッセージ
3. **UI/UX改善**: デザインの調整、アニメーション追加
4. **パフォーマンス最適化**: ローディング時間の短縮

---

**最終更新**: 2024年
**作成者**: 開発チーム

