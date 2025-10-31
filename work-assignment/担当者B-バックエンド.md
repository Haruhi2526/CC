# 担当者B - バックエンド・認証システム

## 担当範囲
- Lambda関数の実装（認証、スタンプ管理、API）
- ユーザー認証・認可の実装
- APIエンドポイントの設計・実装
- バックエンドのビジネスロジック

## 作業内容

### Phase 1: 環境構築（Week 1-2）
- [ ] AWS SAM CLIのインストール
- [ ] ローカル開発環境のセットアップ
- [ ] テスト用AWSアカウントの確認
- [ ] boto3の学習と基本実装

### Phase 2: 認証システム（Week 3）
- [ ] **LINE認証Lambda関数** (`lambda/auth`)
  - LINE IDトークンの検証
  - ユーザー情報の取得
  - セッショントークンの生成
  - Cognito連携（担当者Cと連携）

- [ ] **ユーザー管理Lambda関数** (`lambda/users`)
  - 新規ユーザー登録
  - ユーザー情報更新
  - ログイン履歴の記録

### Phase 3: スタンプ管理API（Week 3-4）
- [ ] **スタンプ取得API** (`lambda/stamps`)
  - ユーザーの保有スタンプ一覧取得
  - スタンプ詳細情報取得
  - スタンプ収集状況の集計

- [ ] **スタンプ授与API** (`lambda/award`)
  - GPS/画像認証後のスタンプ授与処理
  - 重複チェックロジック
  - DynamoDBへの書き込み（担当者Cと連携）

### Phase 4: エラーハンドリング・ログ（Week 4）
- [ ] CloudWatch Logs出力
- [ ] 標準的なエラーレスポンス作成
- [ ] リトライロジック実装
- [ ] レート制限実装

### Phase 5: テスト・統合（Week 7）
- [ ] ユニットテスト作成
- [ ] API統合テスト
- [ ] 負荷テスト
- [ ] セキュリティテスト

## 使用技術
- Python 3.9+
- boto3 (AWS SDK)
- AWS SAM
- LINE Messaging API SDK
- CloudWatch Logs

## 担当ファイル
```
backend/
├── lambda/
│   ├── auth/
│   │   ├── lambda_function.py
│   │   ├── requirements.txt
│   │   └── tests/
│   ├── users/
│   │   ├── lambda_function.py
│   │   └── requirements.txt
│   ├── stamps/
│   │   ├── lambda_function.py
│   │   └── requirements.txt
│   └── award/
│       ├── lambda_function.py
│       └── requirements.txt
├── common/
│   ├── auth_utils.py
│   ├── dynamodb_utils.py
│   └── response_utils.py
└── sam/
    └── template.yaml
```

## API仕様

### POST /auth/verify
LINE IDトークンを検証し、セッショントークンを返す

### GET /stamps/{userId}
ユーザーの保有スタンプ一覧を取得

### POST /stamps/award
スタンプを授与（GPS/画像認証後の処理）

## 連携先
- **担当者A**: API仕様の共有、エンドポイントURLの提供
- **担当者C**: DynamoDBテーブル構造の確認、権限設定
- **担当者D**: 認証判定結果の受け取り

## 成果物
- Lambda関数のソースコード
- API仕様書
- テストコード
- SAMテンプレート

## 注意事項
- セキュリティ: トークンは暗号化保存
- パフォーマンス: コールドスタート対策
- エラー処理: 詳細なログ出力

