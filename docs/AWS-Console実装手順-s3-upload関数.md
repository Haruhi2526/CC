# AWS Console実装手順 - s3-upload関数

## 概要

このドキュメントでは、AWS Consoleを使用してs3-upload関数（S3アップロード用Presigned URL生成）をLambdaにデプロイする手順を説明します。

この関数は、フロントエンドからS3に直接画像をアップロードするためのPresigned URLを生成します。

---

## 事前準備

### 必要なもの
- AWSアカウントへのアクセス権限
- Lambda、S3、IAM、API Gatewayの操作権限
- S3バケットが作成済みであること

### 確認事項
- S3バケット名
- 画像アップロード先のパス構造（デフォルト: `users/{userId}/images/`）

---

## 手順1: ZIPファイルの作成

### 1-1. 作業ディレクトリに移動

```bash
cd /Users/takenouchiharuhi/CC/backend/lambda/s3-upload
```

### 1-2. build.shスクリプトを実行

```bash
./build.sh
```

このスクリプトは以下を実行します：
- 必要なPythonファイルをコピー
- 依存ライブラリをインストール（requirements.txtがある場合）
- ZIPファイルを作成（`lambda-s3-upload.zip`）

---

## 手順2: Lambda関数の作成

### 2-1. Lambdaコンソールを開く

1. AWSコンソールにログイン
2. サービス検索で「Lambda」と入力して選択
3. 「関数を作成」ボタンをクリック

### 2-2. 関数の基本設定

#### 関数の作成方法
- 「一から作成」を選択

#### 基本情報
- **関数名**: `stamp-rally-s3-upload` （または任意の名前）
- **ランタイム**: `Python 3.11`
- **アーキテクチャ**: `x86_64` （デフォルト）

#### 実行ロールの変更
- **デフォルトの実行ロールを使用**: 選択しない
- **既存のロールを使用**: 既存のロールがある場合
- **新しいロールを作成**: 新規作成する場合

**新しいロールを作成する場合:**
- ロール名: `stamp-rally-s3-upload-role`
- 許可ポリシー: 後で設定（まずは基本ロールを作成）

#### 「関数を作成」をクリック

---

## 手順3: コードのアップロード

### 3-1. 関数コードセクションを開く

作成したLambda関数の画面で、「コード」タブが開いていることを確認します。

### 3-2. ZIPファイルをアップロード

1. 「アップロード元」ドロップダウンをクリック
2. 「.zipファイル」を選択
3. 「アップロード」ボタンをクリック
4. 作成した `lambda-s3-upload.zip` を選択
5. 「保存」をクリック

### 3-3. ハンドラーの設定

「ランタイム設定」セクションで以下を確認:

- **ハンドラー**: `lambda_function.lambda_handler`

---

## 手順4: 環境変数の設定

### 4-1. 環境変数セクションを開く

「設定」タブ → 「環境変数」をクリック

### 4-2. 環境変数を追加

「環境変数の追加」をクリックして、以下の環境変数を追加:

| キー | 値 | 説明 |
|-----|-----|------|
| `S3_BUCKET` | `your-bucket-name` | S3バケット名（必須） |
| `S3_PREFIX` | `users/` | S3キーのプレフィックス（オプション、デフォルト: `users/`） |
| `PRESIGNED_URL_EXPIRATION` | `3600` | Presigned URLの有効期限（秒、オプション、デフォルト: 3600秒=1時間） |

### 4-3. 環境変数の保存

すべて追加したら「保存」をクリック

---

## 手順5: IAMロールの設定

### 5-1. IAMロールを確認

「設定」タブ → 「実行ロール」をクリック
- ロール名をクリックしてIAMコンソールを開く

### 5-2. 必要な権限ポリシーをアタッチ

#### S3アクセス権限

「許可を追加」→「ポリシーをアタッチ」をクリック

以下のポリシーをアタッチまたは作成:

**ポリシー名例**: `stamp-rally-s3-upload-policy`

**JSONポリシー例**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name/users/*"
      ]
    }
  ]
}
```

**簡易版（開発環境のみ）**:
- AWS管理ポリシー: `AmazonS3FullAccess` をアタッチ
- **注意**: 本番環境では上記のように最小権限を設定してください

### 5-3. CloudWatch Logs権限（オプション）

ログを出力する場合、以下のポリシーも必要:

- AWS管理ポリシー: `AWSLambdaBasicExecutionRole` をアタッチ

---

## 手順6: タイムアウトとメモリの設定

### 6-1. 一般設定を開く

「設定」タブ → 「一般設定」→「編集」をクリック

### 6-2. 推奨設定

- **タイムアウト**: `30秒` （デフォルト3秒で問題ありませんが、余裕を持たせる）
- **メモリ**: `256 MB` （デフォルト128MBで問題ありませんが、256MBを推奨）

「保存」をクリック

---

## 手順7: API Gatewayとの統合

### 7-1. API Gatewayの確認

既にAPI Gatewayが作成されている場合、以下を設定します。

1. API Gatewayコンソールを開く
2. 対象のREST APIを選択
3. 「リソース」から `/s3` リソースを確認（なければ作成）
4. `/s3/upload-url` にPOSTメソッドを追加

### 7-2. Lambda関数の統合

1. POSTメソッドを選択
2. 「統合リクエスト」をクリック
3. **統合タイプ**: Lambda関数
4. **Lambda関数**: `stamp-rally-s3-upload` を選択
5. 「保存」をクリック
6. 権限の追加を求められたら「OK」をクリック

### 7-3. CORS設定（必要に応じて）

1. `/s3/upload-url` リソースを選択
2. 「アクション」→「CORSを有効化」
3. 設定:
   - **Access-Control-Allow-Origin**: `*` （開発環境）または特定のドメイン（本番環境）
   - **Access-Control-Allow-Headers**: `Content-Type,Authorization`
   - **Access-Control-Allow-Methods**: `POST,OPTIONS`
4. 「CORSを有効化して既存のCORSヘッダーを置き換える」をクリック

### 7-4. APIのデプロイ

1. 「アクション」→「APIのデプロイ」
2. **デプロイされるステージ**: `dev` または既存のステージを選択
3. 「デプロイ」をクリック
4. **呼び出しURL**をメモ（例: `https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/dev/s3/upload-url`）

---

## 手順8: S3バケットポリシーの設定（オプション）

### 8-1. CORS設定

S3バケットにCORS設定を追加する必要がある場合:

1. S3コンソールでバケットを選択
2. 「アクセス許可」タブを開く
3. 「CORS」セクションを編集

**CORS設定例**:
```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["POST", "PUT"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": ["ETag"],
        "MaxAgeSeconds": 3000
    }
]
```

---

## 手順9: テスト実行

### 9-1. Lambda関数の直接テスト

1. Lambda関数の画面で「テスト」タブをクリック
2. 「新しいイベントを作成」をクリック
3. イベント名: `test-s3-upload-event`

#### テストイベントJSON例:

```json
{
  "httpMethod": "POST",
  "body": "{\"user_id\": \"U1234567890abcdefghijklmnopqrstuv\", \"file_name\": \"test-image.jpg\"}",
  "headers": {
    "Content-Type": "application/json"
  }
}
```

4. 「保存」をクリック
5. 「テスト」ボタンをクリック

### 9-2. テスト結果の確認

**成功時のレスポンス例**:
```json
{
  "statusCode": 200,
  "body": "{\"ok\": true, \"upload_url\": \"https://...\", \"fields\": {...}, \"key\": \"users/U1234567890abcdefghijklmnopqrstuv/images/test-image.jpg\"}"
}
```

---

## 手順10: 動作確認チェックリスト

- [ ] Lambda関数が正常に作成された
- [ ] ZIPファイルが正常にアップロードされた
- [ ] 環境変数が正しく設定された（特に`S3_BUCKET`）
- [ ] IAMロールにS3権限が付与された
- [ ] Lambda関数の直接テストが成功した
- [ ] API Gateway経由のテストが成功した（API Gatewayを使用する場合）
- [ ] CORS設定が正しく行われた（API Gatewayを使用する場合）
- [ ] S3バケットのCORS設定が正しく行われた

---

## トラブルシューティング

### エラー1: `AccessDeniedException: Access Denied`
- **原因**: IAMロールにS3権限がない
- **対処**: 手順5でIAMロールにS3権限を追加

### エラー2: `InvalidParameterException: Bucket name is required`
- **原因**: `S3_BUCKET`環境変数が設定されていない
- **対処**: 環境変数`S3_BUCKET`を設定

### エラー3: CORSエラー
- **原因**: CORS設定が正しく行われていない
- **対処**: API GatewayとS3バケットの両方でCORS設定を確認

---

## 次のステップ

1. **セキュリティ強化**: 
   - Presigned URLの有効期限を短くする
   - ファイルサイズ制限の追加
   - ファイルタイプの検証強化
2. **モニタリング**: 
   - CloudWatchアラームの設定
   - メトリクスの監視

---

## 参考リンク

- [AWS Lambda Python ランタイム](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)
- [S3 Presigned POST](https://docs.aws.amazon.com/AmazonS3/latest/userguide/PresignedUrlUploadObject.html)
- [S3 CORS設定](https://docs.aws.amazon.com/AmazonS3/latest/userguide/cors.html)

---

**最終更新**: 2024年
**作成者**: 開発チーム

