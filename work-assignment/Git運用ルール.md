# Git運用ルール - 競合回避ガイド

## ブランチ戦略

### ブランチ構成
```
main (本番環境用)
  │
  ├── develop (開発統合ブランチ)
  │    │
  │    ├── feature/auth (担当者A)
  │    ├── feature/backend-api (担当者B)
  │    ├── feature/infrastructure (担当者C)
  │    └── feature/ai-processing (担当者D)
```

### 各担当者のブランチ

#### 担当者A (フロントエンド)
```
feature/frontend-base         # 基本構造
feature/frontend-auth         # ログイン画面
feature/frontend-gps          # GPS画面
feature/frontend-camera       # カメラ画面
feature/frontend-dashboard    # ダッシュボード
```

#### 担当者B (バックエンド)
```
feature/backend-auth-lambda   # 認証Lambda
feature/backend-user-api      # ユーザーAPI
feature/backend-stamp-api     # スタンプAPI
feature/backend-error-handler # エラーハンドリング
```

#### 担当者C (インフラ)
```
feature/infra-dynamodb        # DynamoDB設定
feature/infra-s3              # S3設定
feature/infra-api-gateway     # API Gateway設定
feature/infra-monitoring      # モニタリング設定
```

#### 担当者D (AI処理)
```
feature/ai-gps-verify         # GPS検証
feature/ai-image-upload       # 画像アップロード
feature/ai-rekognition        # Rekognition連携
feature/ai-custom-labels      # カスタムラベル
```

## 運用ルール

### 1. コミット頻度
- 1つの機能単位でコミット
- 1日1回以上は必ずpush
- 大きな変更は小分けにしてコミット

### 2. コミットメッセージ規約
```
<種別>: <簡潔な説明>

<詳細説明>（必要に応じて）

例:
feat: GPS画面の基本実装

- 現在地取得機能
- 地図表示機能
- スタンプ取得ボタン
```

**種別一覧:**
- `feat`: 新機能
- `fix`: バグ修正
- `refactor`: リファクタリング
- `docs`: ドキュメント更新
- `style`: スタイル変更
- `test`: テスト追加
- `chore`: その他の変更

### 3. プッシュルール
```bash
# 1. 最新のdevelopブランチを取得
git checkout develop
git pull origin develop

# 2. featureブランチに切り替え
git checkout feature/your-branch

# 3. developの変更を取り込む
git merge develop

# 4. コンフリクト解決（発生した場合）

# 5. push
git push origin feature/your-branch
```

### 4. プルリクエスト (PR) ルール

#### PR作成前
- [ ] tamastageブランチとの差分を確認
- [ ] ローカルでテスト完了
- [ ] セルフレビュー実施

#### PR作成時
- タイトル: 機能の概要
- 説明: 変更内容、テスト結果、関連Issue
- レビュアー: 担当者ごとに指定（README.md参照）
- ラベル: `frontend`, `backend`, `infra`, `ai` のいずれか

#### PR承認後
- developへのマージは担当者Cが実施
- マージ後はfeatureブランチを削除

### 5. コンフリクト解決

#### 低リスクファイル（競合しにくい）
- 各自の専用ディレクトリ内のファイル
- 独自機能のファイル

#### 高リスクファイル（競合しやすい）
- `package.json`
- `requirements.txt`
- `samconfig.toml`
- 共通設定ファイル

**対策:**
- 事前に変更予定を共有
- 短時間でマージ
- 担当者Cが調整

### 6. 定期同期

#### 毎日の推奨作業
```bash
# 朝の作業開始時
git fetch origin
git rebase origin/develop

# 作業終了時
git add .
git commit -m "feat: 今日の作業"
git push origin feature/your-branch
```

#### 週次の全体統合
- 毎週金曜日にdevelopブランチを統合
- 全員のPRをレビュー
- 統合テスト実施

## チェックリスト

### コミット前
- [ ] `git status` で変更ファイルを確認
- [ ] 不要なファイルが含まれていないか確認
- [ ] セキュリティ関連情報（トークン等）が含まれていないか確認

### PR前
- [ ] ローカルで動作確認
- [ ] セルフレビュー完了
- [ ] レビュアーに事前連絡

### 統合後
- [ ] 統合テスト実施
- [ ] ドキュメント更新
- [ ] チームに通知

## トラブルシューティング

### コンフリクト発生時
1. 慌てずに現状を把握
2. 担当者Cに連絡
3. 必要に応じて全員で対応

### 履歴を壊してしまった時
```bash
# 危険な操作を避ける
git reflog  # ログを確認
git reset HEAD~1  # 直前のコミット取り消し
```

### 大きな変更を元に戻したい時
```bash
# 安全な方法
git revert <commit-hash>
```

## 禁止事項

- ❌ mainブランチへの直接push
- ❌ 他人のブランチに直接push
- ❌ コミット履歴の強制push（force push）
- ❌ セキュリティ情報のコミット
- ❌ 動かないコードのpush
- ❌ 大きなファイル（100MB以上）のコミット

## 推奨Git設定

```bash
# コミッター情報
git config user.name "Your Name"
git config user.email "your.email@example.com"

# push設定
git config push.default simple

# ブランチ名表示
git config branch.autosetupmerge always

# エディタ設定
git config core.editor "code --wait"  # VS Code使用時
```


