# 担当者C - AWSインフラ・データベース

## 担当範囲
- AWSインフラの構築・設定
- DynamoDBテーブル設計・作成
- S3バケット設定
- API Gateway設定
- デプロイパイプライン構築
- セキュリティ設定

## 作業内容

### Phase 1: インフラ基盤構築（Week 1-2）
- [ ] **DynamoDBテーブル作成**
  - UserStamps テーブル
  - StampMasters テーブル
  - Users テーブル
  - グローバルセカンダリインデックス設定
  - ポイントインタイムリカバリ有効化

- [ ] **S3バケット作成**
  - 画像アップロード用バケット
  - CORS設定
  - バケットポリシー設定
  - ライフサイクルポリシー設定

- [ ] **API Gateway設定**
  - REST API作成
  - リソース・メソッド定義
  - Lambda統合設定
  - CORS設定
  - 認証設定（Cognito）

- [ ] **CloudWatch設定**
  - ロググループ作成
  - ダッシュボード作成
  - アラーム設定

### Phase 2: セキュリティ設定（Week 2）
- [ ] **Amazon Cognito設定**
  - ユーザープール作成
  - IDプール作成（必要に応じて）
  - 認証フロー設定

- [ ] **シークレット管理**
  - Systems Manager Parameter Store使用
  - 暗号化設定

### Phase 3: デプロイ自動化（Week 3-4）
- [ ] **SAM/CloudFormationテンプレート作成**
  - インフラ全体をコード化
  - 環境ごとのパラメータ設定（dev/stg/prod）
  - 依存関係の定義

- [ ] **CI/CDパイプライン**
  - GitHub Actions設定
  - 自動デプロイ設定
  - ロールバック手順作成

### Phase 4: 保守性向上（Week 4）
- [ ] **ドキュメント整備**
  - インフラ構成図作成
  - 設定変更手順書作成
  - トラブルシューティングガイド

- [ ] **バックアップ設定**
  - DynamoDB バックアップ設定
  - S3バージョニング有効化
  - 復旧テスト実施

### Phase 5: 運用準備（Week 7-8）
- [ ] 本番環境へのデプロイ
- [ ] モニタリング設定
- [ ] アラート通知設定
- [ ] コスト監視設定

## 使用技術
- AWS CloudFormation
- AWS SAM (Serverless Application Model)
- AWS CLI
- Terraform (任意)
- GitHub Actions

## 担当ファイル
```
infrastructure/
├── cfn/
│   ├── dynamodb.yaml
│   ├── s3.yaml
│   ├── api-gateway.yaml
├── sam/
│   ├── template.yaml
│   └── samconfig.toml
├── terraform/ (任意)
│   └── main.tf
└── scripts/
    ├── deploy.sh
    └── backup.sh
```

## 環境構成

### 開発環境 (dev)
- リソース命名: `stamp-rally-dev-*`
- マルチAZ無効
- 最小スペック

### ステージング環境 (stg)
- リソース命名: `stamp-rally-stg-*`
- マルチAZ有効
- 本番相当

### 本番環境 (prod)
- リソース命名: `stamp-rally-prod-*`
- マルチAZ必須
- 最高スペック

## 連携先
- **担当者A**: LIFF URLの提供、CORS設定の確認
- **担当者B**: Lambda関数のデプロイ、権限設定
- **担当者D**: S3バケットアクセス権限、Rekognition権限

## 成果物
- CloudFormation/SAMテンプレート
- インフラ構成図
- デプロイ手順書
- 運用マニュアル
- コスト見積もりシート

## 注意事項
- セキュリティ: 最小権限の原則
- コスト: 使用していないリソースの定期削除
- 可観測性: すべてのリソースにログ設定


