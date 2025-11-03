# Phase 1 実装チェックリスト

**作成日**: 2025年11月  
**対象**: リッチメニュー機能実装

---

## ✅ 実装完了項目

### 1. Lambda関数の実装
- [x] `backend/lambda/richmenu/lambda_function.py` - メイン関数
- [x] `backend/lambda/richmenu/response_utils.py` - レスポンスユーティリティ
- [x] `backend/lambda/richmenu/requirements.txt` - 依存関係
- [x] `backend/lambda/richmenu/build.sh` - ビルドスクリプト

### 2. フロントエンド設定
- [x] `frontend/liff-app/js/config.js` - エンドポイント追加
- [x] `frontend/liff-app/js/api.js` - API関数追加

### 3. ドキュメント
- [x] `docs/リッチメニュー実装手順.md` - 詳細な実装手順

---

## 📋 次のステップ（手動作業が必要）

### Step 1: LINE Developers Console設定

1. **Messaging APIチャンネルの確認**
   - [ ] LINE Developers Consoleにログイン
   - [ ] 対象チャネルを選択
   - [ ] Messaging APIタブを開く

2. **Channel Access Tokenの発行**
   - [ ] 「チャンネルアクセストークン（長期）」を発行
   - [ ] トークンをメモ（後でAWS環境変数に設定）
   - 注意: トークンは一度しか表示されないため、必ずメモ

3. **リッチメニューの作成**
   - [ ] 「リッチメニュー」タブを開く
   - [ ] 「作成」ボタンをクリック
   - [ ] メニュー名: 「メインメニュー」
   - [ ] チャットバーテキスト: 「メニュー」
   - [ ] サイズ: 2500 x 843（2段レイアウト）
   - [ ] 4つのボタンエリアを設定:
     - ホーム: `https://liff.line.me/{LIFF_ID}`
     - スタンプ一覧: `https://liff.line.me/{LIFF_ID}/stamps.html`
     - マップ: `https://liff.line.me/{LIFF_ID}/map.html`（将来実装）
     - ランキング: `https://liff.line.me/{LIFF_ID}/ranking.html`（Phase 3で実装）

4. **リッチメニューの公開**
   - [ ] 「公開」ボタンをクリック
   - [ ] リッチメニューIDをメモ（例: `richmenu-xxxxxxxxxxxxx`）

---

### Step 2: Lambda関数のデプロイ

1. **パッケージの作成**
   ```bash
   cd backend/lambda/richmenu
   ./build.sh
   ```
   - [ ] `lambda-richmenu.zip` が作成されたことを確認

2. **AWS Lambda Consoleで関数を作成**
   - [ ] AWS Lambda Consoleにアクセス
   - [ ] 「関数の作成」をクリック
   - [ ] 関数名: `richmenu`
   - [ ] ランタイム: `Python 3.11`
   - [ ] アーキテクチャ: `x86_64`
   - [ ] 「作成」をクリック

3. **ZIPファイルのアップロード**
   - [ ] 「コードソース」セクションを開く
   - [ ] 「.zipファイルをアップロード」を選択
   - [ ] `lambda-richmenu.zip` をアップロード
   - [ ] 「保存」をクリック

4. **環境変数の設定**
   - [ ] 「設定」タブ → 「環境変数」を開く
   - [ ] 「編集」をクリック
   - [ ] 環境変数を追加:
     - キー: `LINE_CHANNEL_ACCESS_TOKEN`
     - 値: LINE Developers Consoleで取得したトークン
   - [ ] 「保存」をクリック

5. **IAM権限の確認**
   - [ ] 「設定」タブ → 「権限」を確認
   - [ ] CloudWatch Logsへの書き込み権限があることを確認

---

### Step 3: API Gateway設定

1. **API Gateway Consoleにアクセス**
   - [ ] 既存のAPI Gateway（devステージ）を開く
   - [ ] または新規APIを作成

2. **リソースの作成**
   - [ ] `/richmenu` リソースを作成
   - [ ] `/richmenu/list` サブリソースを作成（GET）
   - [ ] `/richmenu/set` サブリソースを作成（POST）
   - [ ] `/richmenu/{richmenuId}` サブリソースを作成（GET）
   - [ ] `/richmenu/unset/{userId}` サブリソースを作成（DELETE）

3. **Lambda統合の設定**
   - [ ] 各メソッドで「統合リクエスト」を開く
   - [ ] 統合タイプ: `Lambda関数`
   - [ ] Lambda関数: `richmenu`
   - [ ] Lambda プロキシ統合: 有効化
   - [ ] 「保存」をクリック

4. **CORS設定**
   - [ ] 各メソッドで「アクション」→「CORSを有効にする」をクリック
   - [ ] アクセス制御許可オリジン: `*`
   - [ ] アクセス制御許可ヘッダー: `Content-Type,Authorization`
   - [ ] アクセス制御許可メソッド: `GET,POST,OPTIONS,DELETE`
   - [ ] 「CORSを有効にして既存のCORSヘッダーを置換」をクリック

5. **APIのデプロイ**
   - [ ] 「アクション」→「APIのデプロイ」
   - [ ] デプロイステージ: `dev`
   - [ ] 「デプロイ」をクリック
   - [ ] エンドポイントURLをメモ

---

### Step 4: 動作確認

1. **リッチメニュー一覧取得の確認**
   ```bash
   curl -X GET \
     'https://2bm71jvfs6.execute-api.us-east-1.amazonaws.com/dev/richmenu/list' \
     -H 'Content-Type: application/json'
   ```
   - [ ] ステータスコード200が返る
   - [ ] リッチメニュー一覧が取得できる

2. **リッチメニュー設定の確認**
   ```bash
   curl -X POST \
     'https://2bm71jvfs6.execute-api.us-east-1.amazonaws.com/dev/richmenu/set' \
     -H 'Content-Type: application/json' \
     -d '{
       "user_id": "Ubb2550980506cc932bf7a8fa7f372ec1",
       "richmenu_id": "18040549"
     }'
   ```
   - [ ] ステータスコード200が返る
   - [ ] `ok: true` が返る

3. **LINEアプリでの確認**
   - [ ] LINEアプリを開く
   - [ ] 公式アカウントまたはトークを開く
   - [ ] 画面下部にリッチメニューが表示される
   - [ ] 「ホーム」ボタンをタップ → LIFFアプリが開く
   - [ ] 「スタンプ一覧」ボタンをタップ → スタンプ一覧画面に遷移（将来実装）

---

## 🔍 トラブルシューティング

### エラー: `LINE_CHANNEL_ACCESS_TOKEN environment variable is not set`
- **原因**: 環境変数が設定されていない
- **解決**: Lambda関数の環境変数を確認・設定

### エラー: `401 Unauthorized`
- **原因**: チャンネルアクセストークンが無効
- **解決**: LINE Developers Consoleで新しいトークンを発行し、Lambda関数の環境変数を更新

### エラー: `404 Not Found`（リッチメニューが見つからない）
- **原因**: リッチメニューIDが間違っている、または未公開
- **解決**: LINE Developers ConsoleでリッチメニューIDを確認し、公開状態を確認

### リッチメニューが表示されない
- **原因**: デフォルト設定されていない、または友達登録していない
- **解決**: LINE Developers Consoleでリッチメニューを「デフォルト」に設定

---

## 📝 メモ

- Channel Access Tokenは定期的に更新が必要（通常90日間有効）
- リッチメニューは最大12個まで作成可能
- 1つのチャネルにつき、デフォルトリッチメニューは1つまで
- ユーザー別にリッチメニューを設定する場合は、`/richmenu/set` APIを使用

---

**最終更新**: 2025年11月

