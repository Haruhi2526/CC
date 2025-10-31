# スタンプラリー LIFF アプリ

本リポジトリは、LINEのLIFFを用いたスタンプラリーアプリのモノリポ構成です。フロントエンド（LIFF）、バックエンド（AWS Lambda / API Gateway）、AI処理（Amazon Rekognition）、インフラ（CloudFormation/SAM）で構成されます。

## ディレクトリ構成

```
frontend/liff-app/         # LIFFフロントエンド（HTML/CSS/JS）
backend/                   # Lambda関数と共通モジュール
  ├─ lambda/               # 各機能のLambda
  └─ common/               # 共通ユーティリティ
ai-processing/             # GPS/画像認識関連ロジック
infrastructure/            # IaC（CloudFormation/SAM等）
docs/                      # 仕様・設計ドキュメント
work-assignment/           # 体制・担当・運用ルール
```

## 事前準備

- AWSアカウント: 作成済み（IAMは後日設定）
- LINE Developers: チャネルおよびLIFFアプリの基本設定は完了済み
- GitHubリポジトリ: 作成済み

## フロントエンド（LIFF）

- 位置: `frontend/liff-app/`
- 想定スタック: HTML/CSS/JavaScript（LIFF SDK 2.x）
- 初期実装の目安:
  - `index.html`（ログイン/遷移導線）
  - `js/app.js`（LIFF初期化、トークン取得）
  - `js/api.js`（API呼び出しラッパ）

環境変数例（ビルド不要のため `.env` はコミットしない）:
- LIFF_ID（LIFFアプリID）
- API_BASE_URL（API Gatewayエンドポイント）

## バックエンド（Lambda / API Gateway）

- 位置: `backend/`
- 言語: Python 3.9+
- デプロイ: AWS SAM 予定
- 主な機能:
  - `auth`: LINE IDトークン検証
  - `users`: ユーザー管理
  - `stamps`: スタンプ一覧/詳細取得
  - `award`: スタンプ授与（GPS/画像認証後）

## AI処理（GPS/画像認識）

- 位置: `ai-processing/`
- 機能: GPS距離判定、Rekognitionによる画像判定

## インフラ（IaC）

- 位置: `infrastructure/`
- 予定: CloudFormation/SAM テンプレートで DynamoDB / S3 / API Gateway / Lambda を構築

## 開発環境セットアップ（ローカル）

1) 共通
- Git, AWS CLI をインストール
- `aws configure` で一時的にルート認証情報を設定（IAM整備後に切替）

2) フロントエンド
- VSCode等の静的サーバ拡張、もしくは簡易サーバで `frontend/liff-app/` を配信

3) バックエンド（SAM）
- `brew install aws-sam-cli`（macOS）
- 後日 `infrastructure/sam/template.yaml` に従い `sam build && sam deploy --guided`

## ブランチ戦略（提案）
- `main`: 安定版
- `dev`: 開発統合
- 機能ブランチ: `feature/<name>`

## コミット規約（推奨）
- Conventional Commits に準拠（例: `feat: add gps verification lambda`）

## セキュリティ / 秘密情報
- `.env` / シークレットはコミット禁止
- 後日、Parameter Store もしくは Secrets Manager へ移行

## 参照ドキュメント
- `docs/01-プロジェクト概要.md`
- `docs/02-アーキテクチャ設計.md`
- `docs/03-データベース設計.md`
- `docs/14-次のアクション.md`

## ライセンス
- 未定（必要に応じて設定）
