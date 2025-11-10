# スタンプラリー LIFF アプリ

本リポジトリは、LINEのLIFFを用いたスタンプラリーアプリのモノリポ構成です。フロントエンド（LIFF）、バックエンド（AWS Lambda / API Gateway）、AI処理（Amazon Rekognition）、インフラ（CloudFormation/SAM）で構成されます。

## 📊 現在の進捗状況

### ✅ 完了した機能
- **インフラ構築**: 100%完了
  - DynamoDB、S3、API Gatewayのセットアップ完了
- **バックエンド実装**: 100%完了
  - auth関数（LINE認証）✅
  - award関数（スタンプ授与）✅
  - stamps関数（スタンプ一覧取得）✅
  - gps-verify関数（GPS検証）✅
  - objectCustomLabel関数（画像認識）✅
  - s3-upload関数（S3アップロードURL生成）✅
  - ranking関数（ランキング計算・取得）✅
  - friends関数（友達管理）✅
  - notify関数（通知送信）✅
  - richmenu関数（リッチメニュー管理）✅
- **フロントエンド実装**: 100%完了
  - LIFFアプリ基本構造 ✅
  - LINEログイン機能 ✅
  - スタンプ一覧表示機能 ✅
  - GPS検証機能統合 ✅
  - 画像アップロード機能 ✅
  - スタンプ画像UI表示機能 ✅
  - ランキング表示機能 ✅
  - 友達招待機能 ✅
  - API統合（認証、スタンプ取得、スタンプ授与、GPS検証、画像アップロード、ランキング）✅

### ⏳ 次のステップ
1. 本番環境への移行
2. パフォーマンス最適化
3. UI/UXの改善
4. 統合テストの実施

詳細は [`docs/残りのタスク整理.md`](./docs/残りのタスク整理.md) を参照してください。

## ディレクトリ構成

```
frontend/liff-app/         # LIFFフロントエンド（HTML/CSS/JS）
backend/                   # Lambda関数と共通モジュール
  ├─ lambda/               # 各機能のLambda
  │   ├─ auth/            # LINE認証関数 ✅
  │   ├─ award/           # スタンプ授与関数 ✅
  │   ├─ stamps/          # スタンプ一覧取得関数 ✅
  │   ├─ gps-verify/      # GPS検証関数 ✅
  │   ├─ objectCustomLabel/ # 画像認識関数 ✅
  │   ├─ s3-upload/       # S3アップロードURL生成関数 ✅
  │   ├─ ranking/         # ランキング計算・取得関数 ✅
  │   ├─ friends/         # 友達管理関数 ✅
  │   ├─ notify/          # 通知送信関数 ✅
  │   └─ richmenu/        # リッチメニュー管理関数 ✅
  └─ common/               # 共通ユーティリティ
docs/                      # 仕様・設計ドキュメント
work-assignment/           # 体制・担当・運用ルール
```

## 事前準備

### 必須環境
- ✅ AWSアカウント: 作成済み
- ✅ LINE Developers: チャネルおよびLIFFアプリの基本設定完了
- ✅ GitHubリポジトリ: 作成済み

### 開発環境
- Python 3.11+ (Lambda関数用)
- Node.js / npm (任意、フロントエンド開発用)
- AWS CLI (AWSリソース操作用)
- ngrok (ローカル開発時のLIFF動作確認用)

## フロントエンド（LIFF）

### 実装済み
- **位置**: `frontend/liff-app/`
- **技術スタック**: HTML/CSS/JavaScript（LIFF SDK 2.x）
- **実装済みファイル**:
  - `index.html` - エントリーポイント、LIFF SDK読み込み
  - `ranking.html` - ランキング表示画面
  - `js/app.js` - LIFF初期化、認証フロー、スタンプ一覧表示
  - `js/api.js` - API呼び出しラッパー（認証、スタンプ取得、スタンプ授与、GPS検証、画像アップロード、ランキング）
  - `js/script.js` - GPS検証・画像アップロード機能（位置情報取得、チェックイン処理、画像アップロード、スタンプ画像UI表示）
  - `js/ranking.js` - ランキング表示機能（週間/月間ランキング、友達招待、シェア機能）
  - `js/config.js` - APIエンドポイント、LIFF ID設定
  - `css/style.css` - 基本スタイル定義

### ローカル開発環境

1. **静的サーバーの起動**
```bash
cd frontend/liff-app
python3 -m http.server 8000
```

2. **ngrokでトンネル作成**
```bash
ngrok http 8000
```

3. **LIFF URL設定**
   - LINE Developersコンソールで、ngrokのHTTPS URLをLIFF URLに設定
   - 詳細は [`docs/ngrok動作確認手順.md`](./docs/ngrok動作確認手順.md) を参照

### 設定ファイル

環境変数は`js/config.js`で管理（ビルド不要のため `.env` は未使用）:
- `LIFF_ID`: LIFFアプリID（LINE Developersで取得）
- `API_BASE_URL`: API Gatewayエンドポイント（メインAPI: `https://c5nmu4q3di.execute-api.us-east-1.amazonaws.com/dev`）
- `API_ENDPOINTS`: 各APIエンドポイントのパス定義（`/auth/verify`, `/stamps`, `/stamps/award`, `/gps/verify`, `/s3/upload-url`）

**注意**: ランキングAPIは別のAPI Gateway（`https://2bm71jvfs6.execute-api.us-east-1.amazonaws.com/dev`）を使用しています。

## バックエンド（Lambda / API Gateway）

### 実装済み

- **位置**: `backend/`
- **言語**: Python 3.11
- **デプロイ**: AWS Console（現時点）
- **実装済み機能**:
  - ✅ `auth`: LINE IDトークン検証、ユーザー登録、セッショントークン生成
  - ✅ `stamps`: スタンプ一覧取得
  - ✅ `award`: スタンプ授与（重複チェック、有効期間検証、GPS/IMAGE両対応）
  - ✅ `gps-verify`: GPS位置情報検証（Haversine公式による距離計算）
  - ✅ `objectCustomLabel`: 画像認識（Amazon Rekognition Custom Labels）
  - ✅ `s3-upload`: S3アップロード用Presigned URL生成
  - ✅ `ranking`: ランキング計算・取得（週間/月間、友達ランキング）
  - ✅ `friends`: 友達管理（友達追加、友達リスト取得）
  - ✅ `notify`: 通知送信（スタンプ獲得通知）
  - ✅ `richmenu`: リッチメニュー管理

### デプロイ方法

各Lambda関数は`build.sh`スクリプトでZIPファイルを作成後、AWS Consoleからデプロイします。

詳細は各関数の実装手順書を参照:
- [`docs/AWS-Console実装手順-auth関数.md`](./docs/AWS-Console実装手順-auth関数.md)
- [`docs/AWS-Console実装手順-award関数.md`](./docs/AWS-Console実装手順-award関数.md)
- [`docs/AWS-Console実装手順-objectCustomLabel関数.md`](./docs/AWS-Console実装手順-objectCustomLabel関数.md)
- [`docs/AWS-Console実装手順-s3-upload関数.md`](./docs/AWS-Console実装手順-s3-upload関数.md)
- [`docs/ランキング機能実装手順.md`](./docs/ランキング機能実装手順.md)

### 環境変数

各Lambda関数で設定が必要な環境変数:
- **共通**: `TABLE_USERS`, `TABLE_STAMPMASTERS`, `TABLE_USERSTAMPS`（テーブル名）
- **objectCustomLabel**: `MODEL_ARN`（Rekognition Custom LabelsモデルARN）、`NOTIFY_FUNCTION_NAME`（通知関数名、オプション）
- **ranking**: `TABLE_RANKINGS`, `TABLE_FRIENDS`（テーブル名）
- **friends**: `TABLE_FRIENDS`（テーブル名）
- **notify**: `LINE_CHANNEL_ACCESS_TOKEN`（LINE Messaging APIチャネルアクセストークン）
- **richmenu**: `LINE_CHANNEL_ACCESS_TOKEN`（LINE Messaging APIチャネルアクセストークン）

詳細は [`docs/環境変数設定ガイド.md`](./docs/環境変数設定ガイド.md) を参照

### IAM権限

各Lambda関数には以下のIAM権限が必要:
- `auth`: DynamoDB読み書き権限（Usersテーブル）
- `stamps`: DynamoDB読み取り権限（UserStamps, StampMastersテーブル）
- `award`: DynamoDB読み書き権限（UserStamps, StampMastersテーブル）
- `gps-verify`: DynamoDB読み取り権限（StampMastersテーブル）
- `objectCustomLabel`: DynamoDB読み書き権限（UserStamps, StampMastersテーブル）、Rekognition Custom Labels権限、Lambda呼び出し権限（notify関数）
- `s3-upload`: S3 PutObject権限
- `ranking`: DynamoDB読み書き権限（Rankings, UserStamps, Users, Friendsテーブル）
- `friends`: DynamoDB読み書き権限（Friendsテーブル）
- `notify`: LINE Messaging API権限
- `richmenu`: LINE Messaging API権限

詳細は [`docs/Lambda-IAMロール作成手順.md`](./docs/Lambda-IAMロール作成手順.md) を参照してください。

## AI処理（GPS/画像認識）

- **GPS検証**: 実装済み ✅
  - **位置**: `backend/lambda/gps-verify/`
  - **機能**: Haversine公式による距離計算、範囲判定
  - **状態**: 実装完了・デプロイ済み
- **画像認識**: 実装済み ✅
  - **位置**: `backend/lambda/objectCustomLabel/`
  - **機能**: Amazon Rekognition Custom Labelsによる画像認識、スタンプ自動授与
  - **状態**: 実装完了・デプロイ済み
  - **S3連携**: 画像アップロード時に自動的に画像認識を実行

## インフラ（IaC）

- **位置**: `infrastructure/`
- **予定**: CloudFormation/SAM テンプレートで DynamoDB / S3 / API Gateway / Lambda を構築
- **状態**: 未実装（現時点はAWS Consoleで手動作成）

## APIエンドポイント

### ベースURL
```
https://{api-id}.execute-api.{region}.amazonaws.com/dev
```

### 実装済みエンドポイント

#### 認証・ユーザー管理
- **POST /auth/verify** - LINE IDトークン検証、ユーザー登録、セッショントークン生成

#### スタンプ管理
- **GET /stamps?userId={userId}** - ユーザーの保有スタンプ一覧を取得
- **POST /stamps/award** - スタンプをユーザーに授与（重複チェック、有効期間検証、GPS/IMAGE両対応）

#### GPS検証
- **POST /gps/verify** - GPS位置情報を検証し、指定スタンプの範囲内かどうかを判定

#### 画像認識・アップロード
- **POST /s3/upload-url** - S3アップロード用Presigned URL生成
- **S3イベントトリガー** - 画像アップロード時に自動的に画像認識を実行（objectCustomLabel関数）

#### ランキング
- **POST /ranking/calculate** - ランキング計算（週間/月間）
- **GET /ranking/friends/weekly** - 友達週間ランキング取得
- **GET /ranking/friends/monthly** - 友達月間ランキング取得
- **GET /ranking/compare** - ユーザー比較

#### 友達管理
- **POST /friends/add** - 友達関係を追加
- **GET /friends/list** - 友達リストを取得

#### その他
- **POST /notify** - 通知送信（スタンプ獲得通知）
- **GET /richmenu/list** - リッチメニュー一覧取得
- **POST /richmenu/set** - リッチメニュー設定

詳細なAPI仕様は [`docs/API仕様書.md`](./docs/API仕様書.md) を参照してください。  
ランキング関連のAPI仕様は [`docs/ランキング機能実装手順.md`](./docs/ランキング機能実装手順.md) を参照してください。

## 開発環境セットアップ（ローカル）

### 1. 共通設定

1. AWS CLIの設定
```bash
aws configure
```

2. リポジトリのクローン
```bash
git clone <repository-url>
cd CC
```

### 2. フロントエンド開発

1. ローカルサーバー起動
```bash
cd frontend/liff-app
python3 -m http.server 8000
```

2. ngrokでトンネル作成
```bash
ngrok http 8000
```

3. LINE DevelopersでLIFF URLを設定（ngrokのHTTPS URL）

4. LINEアプリからLIFFアプリを開いて動作確認

詳細は [`docs/ngrok動作確認手順.md`](./docs/ngrok動作確認手順.md) を参照

### 3. バックエンド開発

1. Lambda関数のローカル開発
```bash
cd backend/lambda/{function-name}
# コード編集
```

2. 依存関係のインストール（必要に応じて）
```bash
pip install -r requirements.txt -t .
```

3. ZIPファイル作成
```bash
./build.sh
# または
zip -r lambda-{function-name}.zip . -x "*.git*" "*.md" "*.sh"
```

4. AWS Consoleからデプロイ

### 4. バックエンド（SAM）（将来）

```bash
brew install aws-sam-cli  # macOS
cd infrastructure/sam
sam build && sam deploy --guided
```

## ブランチ戦略

- `main`: 安定版（本番環境用）
- `dev`: 開発統合ブランチ
- 機能ブランチ: `feature/<name>`（例: `feature/gps-verification`）

詳細は [`work-assignment/Git運用ルール.md`](./work-assignment/Git運用ルール.md) を参照

## コミット規約

- Conventional Commits に準拠
- 例:
  - `feat: add gps verification lambda`
  - `fix: cors error in stamps endpoint`
  - `docs: update API documentation`

## セキュリティ / 秘密情報

- `.env` / シークレットはコミット禁止（`.gitignore`に含まれています）
- 環境変数はAWS Systems Manager Parameter StoreもしくはSecrets Managerを使用（将来実装予定）
- API GatewayのエンドポイントURLは`js/config.js`で管理（現時点）

## トラブルシューティング

### CORSエラー
- API GatewayでCORS設定を確認
- Lambda関数でOPTIONSリクエストを処理しているか確認
- 詳細は [`docs/CORSエラー診断と解決チェックリスト.md`](./docs/CORSエラー診断と解決チェックリスト.md) を参照

### 認証エラー
- LIFF SDKが正しく読み込まれているか確認
- IDトークンが正しく取得できているか確認
- 詳細は [`docs/LIFFログインエラー解決手順.md`](./docs/LIFFログインエラー解決手順.md) を参照

### ランキングが表示されない
- ランキング計算が実行されているか確認
- 詳細は [`docs/ランキング表示されない問題の解決方法.md`](./docs/ランキング表示されない問題の解決方法.md) を参照

### S3アップロードエラー
- S3バケットのCORS設定を確認
- Lambda関数のIAM権限を確認
- 詳細は [`docs/S3-CORS設定手順.md`](./docs/S3-CORS設定手順.md) と [`docs/s3-upload-IAM権限追加手順.md`](./docs/s3-upload-IAM権限追加手順.md) を参照

## 参照ドキュメント

### プロジェクト概要
- [`docs/01-プロジェクト概要.md`](./docs/01-プロジェクト概要.md)
- [`docs/02-アーキテクチャ設計.md`](./docs/02-アーキテクチャ設計.md)
- [`docs/03-データベース設計.md`](./docs/03-データベース設計.md)

### 実装手順
- [`docs/AWS-Console実装手順-auth関数.md`](./docs/AWS-Console実装手順-auth関数.md)
- [`docs/AWS-Console実装手順-award関数.md`](./docs/AWS-Console実装手順-award関数.md)
- [`docs/AWS-Console実装手順-objectCustomLabel関数.md`](./docs/AWS-Console実装手順-objectCustomLabel関数.md)
- [`docs/AWS-Console実装手順-s3-upload関数.md`](./docs/AWS-Console実装手順-s3-upload関数.md)
- [`docs/ランキング機能実装手順.md`](./docs/ランキング機能実装手順.md)
- [`docs/LIFFアプリ基本構造作成手順.md`](./docs/LIFFアプリ基本構造作成手順.md)
- [`docs/DynamoDB-スタンプマスターデータ投入手順.md`](./docs/DynamoDB-スタンプマスターデータ投入手順.md)

### API・技術仕様
- [`docs/API仕様書.md`](./docs/API仕様書.md) ⭐ **NEW**
- [`docs/環境変数設定ガイド.md`](./docs/環境変数設定ガイド.md)

### 開発・運用
- [`docs/残りのタスク整理.md`](./docs/残りのタスク整理.md)
- [`docs/14-次のアクション.md`](./docs/14-次のアクション.md)
- [`docs/実装完了機能一覧.md`](./docs/実装完了機能一覧.md)

### トラブルシューティング
- [`docs/CORSエラー診断と解決チェックリスト.md`](./docs/CORSエラー診断と解決チェックリスト.md)
- [`docs/CORS設定-MOCK統合の完全手順.md`](./docs/CORS設定-MOCK統合の完全手順.md)
- [`docs/ランキング表示されない問題の解決方法.md`](./docs/ランキング表示されない問題の解決方法.md)
- [`docs/S3-CORS設定手順.md`](./docs/S3-CORS設定手順.md)
- [`docs/s3-upload-IAM権限追加手順.md`](./docs/s3-upload-IAM権限追加手順.md)
- [`docs/API-Gateway統合設定確認.md`](./docs/API-Gateway統合設定確認.md)
- [`docs/LIFFログインエラー解決手順.md`](./docs/LIFFログインエラー解決手順.md)

## ライセンス

未定（必要に応じて設定）

---

**最終更新**: 2025年1月（画像認識機能・ランキング機能・友達機能実装完了）  
**バージョン**: 2.0

