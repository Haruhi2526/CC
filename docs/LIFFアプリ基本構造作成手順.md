# LIFFアプリ基本構造作成手順

## 概要

このドキュメントでは、LIFFアプリの基本構造を作成する手順を説明します。

**目標**: 
- LIFF SDKの初期化
- LINEログイン機能の実装
- API呼び出しの基本構造
- 認証フローの実装

---

## 前提条件

### 必要な情報
- **LIFF ID**: LINE Developersコンソールで取得
- **API Gatewayエンドポイント**: 
  - `https://2bm71jvfs6.execute-api.us-east-1.amazonaws.com/dev`
- **エンドポイント一覧**:
  - `POST /auth/verify` - LINE認証
  - `GET /stamps?userId={userId}` - スタンプ一覧取得
  - `POST /stamps/award` - スタンプ授与

### 必要な技術
- LIFF SDK 2.x
- HTML5/CSS3/JavaScript (ES6+)
- Fetch API

---

## 作業手順

### 手順1: index.htmlの作成

エントリーポイントとなるHTMLファイルを作成します。

**ファイル**: `frontend/liff-app/index.html`

**主な機能**:
- LIFF SDKの読み込み
- 基本的なHTML構造
- ローディング表示
- エラーハンドリング

---

### 手順2: js/app.jsの作成

LIFF初期化と基本フローを実装します。

**ファイル**: `frontend/liff-app/js/app.js`

**主な機能**:
- LIFF SDKの初期化
- LINEログイン状態の確認
- IDトークンの取得
- 認証フローの管理
- 画面遷移の制御

**処理フロー**:
1. LIFF SDK初期化
2. ログイン状態確認
3. 未ログインの場合: ログインボタン表示
4. ログイン済みの場合: ホーム画面へ遷移
5. IDトークン取得 → auth API呼び出し
6. セッショントークン保存
7. メインアプリへ遷移

---

### 手順3: js/api.jsの作成

API呼び出しのラッパー関数を実装します。

**ファイル**: `frontend/liff-app/js/api.js`

**主な機能**:
- API呼び出しの共通処理
- エラーハンドリング
- セッショントークンの管理
- リトライロジック（オプション）

**実装する関数**:
- `apiCall()` - 汎用API呼び出し
- `auth.verify()` - LINE認証
- `stamps.list()` - スタンプ一覧取得
- `stamps.award()` - スタンプ授与

---

### 手順4: css/style.cssの作成（オプション）

基本的なスタイルを定義します。

**ファイル**: `frontend/liff-app/css/style.css`

**主な内容**:
- リセットCSS
- 基本的なレイアウト
- ローディング表示
- エラーメッセージ表示

---

### 手順5: 設定ファイルの準備

**ファイル**: `frontend/liff-app/js/config.js`

**内容**:
- APIベースURL
- LIFF ID（環境変数から読み込み）
- その他の設定値

---

### 手順6: 動作確認

1. LINE DevelopersコンソールでLIFFアプリを設定
2. LIFF URLにアクセス
3. LINEログインの動作確認
4. 認証API呼び出しの確認
5. エラーハンドリングの確認

---

## 実装詳細

### 1. index.html の構造

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>スタンプラリー</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div id="liffAppContent">
        <!-- ローディング表示 -->
        <div id="loading" class="loading">
            <p>読み込み中...</p>
        </div>
        
        <!-- エラー表示 -->
        <div id="error" class="error" style="display: none;">
            <p id="errorMessage"></p>
        </div>
        
        <!-- メインコンテンツ -->
        <div id="mainContent" style="display: none;">
            <!-- ここにアプリコンテンツが表示される -->
        </div>
    </div>
    
    <!-- LIFF SDK -->
    <script charset="utf-8" src="https://static.line-scdn.net/liff/edge/versions/2.1/sdk.js"></script>
    
    <!-- 設定 -->
    <script src="js/config.js"></script>
    
    <!-- APIラッパー -->
    <script src="js/api.js"></script>
    
    <!-- メインアプリケーション -->
    <script src="js/app.js"></script>
</body>
</html>
```

---

### 2. js/config.js の実装

```javascript
// API設定
const CONFIG = {
    // API Gatewayエンドポイント
    API_BASE_URL: 'https://2bm71jvfs6.execute-api.us-east-1.amazonaws.com/dev',
    
    // LIFF ID（環境に応じて変更）
    // LINE Developersコンソールで取得
    LIFF_ID: window.LIFF_ID || '2008398050-PkX4k4px',
    
    // セッションストレージのキー
    STORAGE_KEYS: {
        ACCESS_TOKEN: 'stamp_rally_access_token',
        USER_ID: 'stamp_rally_user_id'
    }
};

// エクスポート（グローバルスコープ）
window.CONFIG = CONFIG;
```

---

### 3. js/api.js の実装ポイント

**必須機能**:
- API呼び出しの共通処理
- エラーハンドリング
- レスポンスのパース
- セッショントークンの管理

**エラーハンドリング**:
- ネットワークエラー
- HTTPステータスエラー
- APIエラーレスポンス

---

### 4. js/app.js の実装ポイント

**LIFF初期化**:
```javascript
liff.init({ liffId: CONFIG.LIFF_ID })
    .then(() => {
        // 初期化成功
        if (!liff.isLoggedIn()) {
            // ログインしていない場合
            showLoginButton();
        } else {
            // ログイン済みの場合
            handleLoggedIn();
        }
    })
    .catch((err) => {
        // 初期化エラー
        showError('LIFF初期化に失敗しました', err);
    });
```

**認証フロー**:
1. IDトークンを取得: `liff.getIDToken()`
2. auth APIを呼び出し: `api.auth.verify(idToken)`
3. レスポンスからaccess_tokenを取得
4. セッションストレージに保存
5. ホーム画面へ遷移

---

## ファイル構成

```
frontend/liff-app/
├── index.html          # エントリーポイント
├── css/
│   └── style.css      # スタイルシート
└── js/
    ├── config.js      # 設定ファイル
    ├── api.js         # API呼び出しラッパー
    └── app.js         # メインアプリケーション
```

---

## テスト手順

### 1. ローカルテスト

1. ローカルサーバーを起動（例: `python3 -m http.server 8000`）
2. LINE DevelopersコンソールでLIFF URLを設定
3. LINEアプリからアクセスして動作確認

### 2. 認証フローのテスト

1. 未ログイン状態でアクセス
   - ログインボタンが表示されることを確認
2. ログインボタンをクリック
   - LINEログイン画面に遷移することを確認
3. ログイン後
   - auth APIが呼び出されることを確認
   - セッショントークンが保存されることを確認
   - ホーム画面へ遷移することを確認

### 3. エラーハンドリングのテスト

1. ネットワークエラー
   - ネットワークを切断してエラーメッセージを確認
2. APIエラー
   - 無効なIDトークンでエラーレスポンスを確認

---

## 注意事項

### セキュリティ
- セッショントークンは`sessionStorage`に保存（タブを閉じると消える）
- 機密情報はハードコーディングしない
- HTTPS通信を必須とする

### パフォーマンス
- LIFF SDKの読み込みを最適化
- 不要なAPI呼び出しを避ける
- ローディング表示でUXを向上

### ブラウザ互換性
- LIFFはLINEアプリ内ブラウザでのみ動作
- 通常のブラウザでは動作しない
- デバッグ時はLINEアプリ経由で確認

---

## 次のステップ

基本構造が完成したら:

1. **ホーム画面の実装**
   - スタンプ一覧表示
   - スタンプ取得APIとの統合

2. **GPSスタンプ画面の実装**
   - 位置情報取得
   - GPS検証APIとの統合

3. **カメラスタンプ画面の実装**
   - カメラ機能
   - 画像アップロード
   - 画像認識APIとの統合

---

## 参考リンク

- [LIFF 公式ドキュメント](https://developers.line.biz/ja/docs/liff/)
- [LIFF API リファレンス](https://developers.line.biz/ja/reference/liff/)
- [Fetch API ドキュメント](https://developer.mozilla.org/ja/docs/Web/API/Fetch_API)

---

**最終更新**: 2024年
**作成者**: 開発チーム

