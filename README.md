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
- **フロントエンド実装**: 100%完了（基本機能）
  - LIFFアプリ基本構造 ✅
  - LINEログイン機能 ✅
  - スタンプ一覧表示機能 ✅
  - API統合（認証、スタンプ取得、スタンプ授与）✅

### ⏳ 次のステップ
1. GPS検証関数の実装
2. 画像認識関数の実装
3. GPS/カメラスタンプ画面の実装
4. ホーム画面の改善

詳細は [`docs/残りのタスク整理.md`](./docs/残りのタスク整理.md) を参照してください。

## ディレクトリ構成

```
frontend/liff-app/         # LIFFフロントエンド（HTML/CSS/JS）
backend/                   # Lambda関数と共通モジュール
  ├─ lambda/               # 各機能のLambda
  │   ├─ auth/            # LINE認証関数 ✅
  │   ├─ award/           # スタンプ授与関数 ✅
  │   └─ stamps/          # スタンプ一覧取得関数 ✅
  └─ common/               # 共通ユーティリティ
ai-processing/             # GPS/画像認識関連ロジック（未実装）
infrastructure/            # IaC（CloudFormation/SAM等）（未実装）
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
  - `js/app.js` - LIFF初期化、認証フロー、スタンプ一覧表示
  - `js/api.js` - API呼び出しラッパー（認証、スタンプ取得、スタンプ授与）
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
- `API_BASE_URL`: API Gatewayエンドポイント（例: `https://xxxxx.execute-api.us-east-1.amazonaws.com/dev`）

## バックエンド（Lambda / API Gateway）

### 実装済み

- **位置**: `backend/`
- **言語**: Python 3.11
- **デプロイ**: AWS Console（現時点）
- **実装済み機能**:
  - ✅ `auth`: LINE IDトークン検証、ユーザー登録、セッショントークン生成
  - ✅ `stamps`: スタンプ一覧取得
  - ✅ `award`: スタンプ授与（重複チェック、有効期間検証）

### デプロイ方法

各Lambda関数は`build.sh`スクリプトでZIPファイルを作成後、AWS Consoleからデプロイします。

詳細は各関数の実装手順書を参照:
- [`docs/AWS-Console実装手順-auth関数.md`](./docs/AWS-Console実装手順-auth関数.md)
- [`docs/AWS-Console実装手順-award関数.md`](./docs/AWS-Console実装手順-award関数.md)

### 環境変数

各Lambda関数で設定が必要な環境変数:
- `USERS_TABLE_NAME`: Usersテーブル名
- `STAMP_MASTERS_TABLE_NAME`: StampMastersテーブル名
- `USER_STAMPS_TABLE_NAME`: UserStampsテーブル名

詳細は [`docs/環境変数設定ガイド.md`](./docs/環境変数設定ガイド.md) を参照

### IAM権限

各Lambda関数には以下のIAM権限が必要:
- `auth`: DynamoDB読み書き権限（Usersテーブル）
- `stamps`: DynamoDB読み取り権限（UserStamps, StampMastersテーブル）
- `award`: DynamoDB読み書き権限（UserStamps, StampMastersテーブル）

## AI処理（GPS/画像認識）

- **位置**: `ai-processing/`
- **機能**: GPS距離判定、Rekognitionによる画像判定
- **状態**: 未実装

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

#### 1. LINE認証
- **エンドポイント**: `POST /auth/verify`
- **説明**: LINE IDトークンを検証し、ユーザー情報をDynamoDBに保存、セッショントークンを生成
- **詳細**: [`docs/API仕様書.md`](./docs/API仕様書.md) を参照

#### 2. スタンプ一覧取得
- **エンドポイント**: `GET /stamps?userId={userId}`
- **説明**: ユーザーの保有スタンプ一覧を取得
- **詳細**: [`docs/API仕様書.md`](./docs/API仕様書.md) を参照

#### 3. スタンプ授与
- **エンドポイント**: `POST /stamps/award`
- **説明**: スタンプをユーザーに授与（重複チェック、有効期間検証含む）
- **詳細**: [`docs/API仕様書.md`](./docs/API仕様書.md) を参照

詳細なAPI仕様は [`docs/API仕様書.md`](./docs/API仕様書.md) を参照してください。

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
- 詳細は [`docs/CORS設定修正手順.md`](./docs/CORS設定修正手順.md) を参照

### 認証エラー
- LIFF SDKが正しく読み込まれているか確認
- IDトークンが正しく取得できているか確認
- 詳細は [`docs/デバッグ手順.md`](./docs/デバッグ手順.md) を参照

## 参照ドキュメント

### プロジェクト概要
- [`docs/01-プロジェクト概要.md`](./docs/01-プロジェクト概要.md)
- [`docs/02-アーキテクチャ設計.md`](./docs/02-アーキテクチャ設計.md)
- [`docs/03-データベース設計.md`](./docs/03-データベース設計.md)

### 実装手順
- [`docs/AWS-Console実装手順-auth関数.md`](./docs/AWS-Console実装手順-auth関数.md)
- [`docs/AWS-Console実装手順-award関数.md`](./docs/AWS-Console実装手順-award関数.md)
- [`docs/LIFFアプリ基本構造作成手順.md`](./docs/LIFFアプリ基本構造作成手順.md)

### API・技術仕様
- [`docs/API仕様書.md`](./docs/API仕様書.md) ⭐ **NEW**
- [`docs/環境変数設定ガイド.md`](./docs/環境変数設定ガイド.md)

### 開発・運用
- [`docs/残りのタスク整理.md`](./docs/残りのタスク整理.md)
- [`docs/14-次のアクション.md`](./docs/14-次のアクション.md)
- [`docs/実装完了機能一覧.md`](./docs/実装完了機能一覧.md)

### トラブルシューティング
- [`docs/CORS設定修正手順.md`](./docs/CORS設定修正手順.md)
- [`docs/API-Gateway統合設定確認.md`](./docs/API-Gateway統合設定確認.md)
- [`docs/デバッグ手順.md`](./docs/デバッグ手順.md)

## ライセンス

未定（必要に応じて設定）

---

**最終更新**: 2025年11月  
**バージョン**: 1.0
