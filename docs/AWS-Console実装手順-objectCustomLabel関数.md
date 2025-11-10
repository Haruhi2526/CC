# AWS Console実装手順 - objectCustomLabel関数

## 概要

このドキュメントでは、AWS Consoleを使用してobjectCustomLabel関数（画像認識によるスタンプ自動付与）をLambdaにデプロイする手順を説明します。

この関数は、S3に画像がアップロードされると自動的にトリガーされ、Amazon Rekognition Custom Labelsで画像認識を実行し、検出されたラベルに基づいてスタンプを自動付与します。

**注意**: Mac環境でビルドしたものをLinux環境（Lambda）で動作させるため、依存ライブラリのビルドには注意が必要です。現在の実装は標準ライブラリのみを使用しているため、問題ありません。

---

## 事前準備

### 必要なもの
- AWSアカウントへのアクセス権限
- Lambda、DynamoDB、IAM、S3、Rekognitionの操作権限
- 既に作成済みのDynamoDBテーブル（`UserStamps`テーブル、`StampMasters`テーブル）
- Amazon Rekognition Custom Labelsプロジェクトとモデルが作成済みであること
- S3バケットが作成済みであること

### 確認事項
- DynamoDBテーブルが作成済みであること
- テーブル名（デフォルト: `UserStamps`, `StampMasters`）
- Rekognition Custom LabelsモデルのARN
- S3バケット名と画像アップロード先のパス構造

---

## 手順1: ZIPファイルの作成

### 1-1. 作業ディレクトリに移動

```bash
cd /Users/takenouchiharuhi/CC/backend/lambda/objectCustomLabel
```

### 1-2. build.shスクリプトを実行

```bash
./build.sh
```

このスクリプトは以下を実行します：
- 必要なPythonファイルをコピー
- 依存ライブラリをインストール（requirements.txtがある場合）
- ZIPファイルを作成（`lambda-objectCustomLabel.zip`）

### 1-3. ZIPファイルの確認

```bash
# ZIPファイルの内容を確認
unzip -l lambda-objectCustomLabel.zip
```

期待される出力例:
```
Archive:  lambda-objectCustomLabel.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
     8000  2024-01-01 10:00   lambda_function.py
     5000  2024-01-01 10:00   dynamodb_utils.py
     2000  2024-01-01 10:00   response_utils.py
---------                     -------
    15000                     3 files
```

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
- **関数名**: `stamp-rally-objectCustomLabel` （または任意の名前）
- **ランタイム**: `Python 3.11`
- **アーキテクチャ**: `x86_64` （デフォルト）

#### 実行ロールの変更
- **デフォルトの実行ロールを使用**: 選択しない
- **既存のロールを使用**: 既存のロールがある場合
- **新しいロールを作成**: 新規作成する場合

**新しいロールを作成する場合:**
- ロール名: `stamp-rally-objectCustomLabel-role`
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
4. 作成した `lambda-objectCustomLabel.zip` を選択
5. 「保存」をクリック

### 3-3. ハンドラーの設定

「ランタイム設定」セクションで以下を確認:

- **ハンドラー**: `lambda_function.lambda_handler`
  - 形式: `ファイル名.関数名`
  - `lambda_function.py` の `lambda_handler` 関数を指す

---

## 手順4: 環境変数の設定

### 4-1. 環境変数セクションを開く

「設定」タブ → 「環境変数」をクリック

### 4-2. 環境変数を追加

「環境変数の追加」をクリックして、以下の環境変数を追加:

| キー | 値 | 説明 |
|-----|-----|------|
| `MODEL_ARN` | `arn:aws:rekognition:region:account-id:project/project-name/version/version-id` | Rekognition Custom LabelsモデルのARN（必須） |
| `TABLE_USERSTAMPS` | `UserStamps` | DynamoDB UserStampsテーブル名（オプション、デフォルト: `UserStamps`） |
| `TABLE_STAMPMASTERS` | `StampMasters` | DynamoDB StampMastersテーブル名（オプション、デフォルト: `StampMasters`） |
| `NOTIFY_FUNCTION_NAME` | `stamp-rally-notify` | 通知送信用Lambda関数名（オプション、デフォルト: `notify`） |

**MODEL_ARNの取得方法:**
1. Amazon Rekognitionコンソールを開く
2. 「カスタムラベル」→「プロジェクト」を選択
3. 対象のプロジェクトを選択
4. 「モデル」タブを選択
5. 使用するモデルバージョンのARNをコピー

### 4-3. 環境変数の保存

すべて追加したら「保存」をクリック

---

## 手順5: IAMロールの設定

### 5-1. IAMロールを確認

「設定」タブ → 「実行ロール」をクリック
- ロール名をクリックしてIAMコンソールを開く

### 5-2. 必要な権限ポリシーをアタッチ

#### Rekognitionアクセス権限

「許可を追加」→「ポリシーをアタッチ」をクリック

以下のポリシーをアタッチまたは作成:

**ポリシー名例**: `stamp-rally-objectCustomLabel-rekognition-policy`

**JSONポリシー例**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "rekognition:DetectCustomLabels"
      ],
      "Resource": [
        "arn:aws:rekognition:*:*:project/*/version/*"
      ]
    }
  ]
}
```

#### DynamoDBアクセス権限

**ポリシー名例**: `stamp-rally-objectCustomLabel-dynamodb-policy`

**JSONポリシー例**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": [
        "arn:aws:dynamodb:*:*:table/UserStamps",
        "arn:aws:dynamodb:*:*:table/UserStamps/index/*",
        "arn:aws:dynamodb:*:*:table/StampMasters",
        "arn:aws:dynamodb:*:*:table/StampMasters/index/*"
      ]
    }
  ]
}
```

#### Lambda関数呼び出し権限（通知用）

**ポリシー名例**: `stamp-rally-objectCustomLabel-lambda-policy`

**JSONポリシー例**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:InvokeFunction"
      ],
      "Resource": [
        "arn:aws:lambda:*:*:function:stamp-rally-notify",
        "arn:aws:lambda:*:*:function:notify"
      ]
    }
  ]
}
```

**簡易版（開発環境のみ）**:
- AWS管理ポリシー: `AmazonRekognitionFullAccess`, `AmazonDynamoDBFullAccess`, `AWSLambda_FullAccess` をアタッチ
- **注意**: 本番環境では上記のように最小権限を設定してください

### 5-3. CloudWatch Logs権限（オプション）

ログを出力する場合、以下のポリシーも必要:

- AWS管理ポリシー: `AWSLambdaBasicExecutionRole` をアタッチ

---

## 手順6: タイムアウトとメモリの設定

### 6-1. 一般設定を開く

「設定」タブ → 「一般設定」→「編集」をクリック

### 6-2. 推奨設定

- **タイムアウト**: `60秒` （画像認識処理に時間がかかる可能性があるため）
- **メモリ**: `512 MB` （Rekognition処理には十分なメモリが必要）

「保存」をクリック

---

## 手順7: S3イベント通知の設定

### 7-1. S3コンソールを開く

1. AWSコンソールで「S3」を検索して選択
2. 画像をアップロードするバケットを選択

### 7-2. イベント通知の設定

1. バケットの「プロパティ」タブを開く
2. 「イベント通知」セクションまでスクロール
3. 「イベント通知を作成」をクリック

### 7-3. イベント通知の設定

#### 基本設定
- **イベント通知名**: `image-upload-trigger` （任意の名前）
- **プレフィックス**: `users/` （画像がアップロードされるパス、オプション）
- **サフィックス**: `.jpg` または `.png` （画像ファイルの拡張子、オプション）

#### イベントタイプ
以下のイベントタイプを選択:
- `s3:ObjectCreated:*` （すべてのオブジェクト作成イベント）
  - または `s3:ObjectCreated:Put` （PUT操作のみ）

#### 送信先
- **送信先タイプ**: Lambda関数
- **Lambda関数**: `stamp-rally-objectCustomLabel` を選択

### 7-4. 権限の確認

S3からLambda関数を呼び出すための権限が自動的に追加されます。確認メッセージが表示されたら「許可」をクリック。

### 7-5. イベント通知の保存

「イベント通知を保存」をクリック

---

## 手順8: S3キー構造の確認

### 8-1. 想定されるS3キー構造

この関数は、S3キーからユーザーIDを抽出します。以下のいずれかの形式を想定しています:

- `users/{userId}/images/{filename}`
- `{userId}/images/{filename}`
- `{userId}/{filename}`

### 8-2. 画像アップロード時の注意

フロントエンドや他のLambda関数から画像をアップロードする際は、上記の形式に従ってキーを設定してください。

例:
```python
s3_client.put_object(
    Bucket='your-bucket-name',
    Key=f'users/{user_id}/images/{image_id}.jpg',
    Body=image_data
)
```

---

## 手順9: スタンプマスターデータの準備

### 9-1. ImageLabelフィールドの設定

`StampMasters`テーブルに、画像認識用のスタンプを追加する必要があります。

**必要なフィールド:**
- `StampId`: スタンプID（例: `IMAGE-001`）
- `Name`: スタンプ名
- `Type`: `IMAGE` （必須）
- `ImageLabel`: Rekognition Custom Labelsで検出されるラベル名（必須）
- `ValidFrom`: 有効開始日時（オプション）
- `ValidTo`: 有効終了日時（オプション）

### 9-2. データ投入例

DynamoDBコンソールまたはAWS CLIで以下のようなデータを投入:

```json
{
  "StampId": "IMAGE-001",
  "Name": "建物14号館",
  "Description": "建物14号館の画像を認識してスタンプを獲得",
  "Type": "IMAGE",
  "ImageLabel": "building-14",
  "ValidFrom": 1704067200,
  "ValidTo": 1735689600
}
```

**注意**: `ImageLabel`の値は、Rekognition Custom Labelsモデルで学習したラベル名と完全に一致する必要があります。

---

## 手順10: テスト実行

### 10-1. Lambda関数の直接テスト

1. Lambda関数の画面で「テスト」タブをクリック
2. 「新しいイベントを作成」をクリック
3. イベント名: `test-s3-event`

#### テストイベントJSON例:

```json
{
  "Records": [
    {
      "eventVersion": "2.1",
      "eventSource": "aws:s3",
      "awsRegion": "ap-northeast-1",
      "eventTime": "2024-01-01T10:00:00.000Z",
      "eventName": "ObjectCreated:Put",
      "s3": {
        "bucket": {
          "name": "your-bucket-name"
        },
        "object": {
          "key": "users/U1234567890abcdefghijklmnopqrstuv/images/test-image.jpg"
        }
      }
    }
  ]
}
```

4. 「保存」をクリック
5. 「テスト」ボタンをクリック

### 10-2. テスト結果の確認

**成功時のレスポンス例**:
```json
{
  "statusCode": 200,
  "body": "{\"image\": \"users/U1234567890abcdefghijklmnopqrstuv/images/test-image.jpg\", \"detected_labels\": [{\"Name\": \"building-14\", \"Confidence\": 95.5}], \"awarded_stamps\": [{\"stamp_id\": \"IMAGE-001\", \"stamp_name\": \"建物14号館\", \"label\": \"building-14\", \"collected_at\": 1704067200}], \"message\": \"Successfully awarded 1 stamp(s)\"}"
}
```

**エラーが発生した場合:**
- エラーメッセージを確認
- CloudWatch Logsを確認（「モニタリング」タブ → 「CloudWatch Logsの表示」）

### 10-3. よくあるエラーと対処法

#### エラー1: `Unable to import module 'lambda_function'`
- **原因**: ZIPファイルに必要なファイルが含まれていない
- **対処**: ZIPファイルの内容を確認し、すべての`.py`ファイルが含まれていることを確認

#### エラー2: `AccessDeniedException: User is not authorized to perform: rekognition:DetectCustomLabels`
- **原因**: IAMロールにRekognition権限がない
- **対処**: 手順5でIAMロールにRekognition権限を追加

#### エラー3: `ResourceNotFoundException: Requested resource not found`
- **原因**: DynamoDBテーブル名が間違っている、またはテーブルが存在しない
- **対処**: 環境変数の値を確認し、DynamoDBコンソールでテーブルが存在することを確認

#### エラー4: `InvalidParameterException: Invalid model ARN`
- **原因**: `MODEL_ARN`環境変数が正しく設定されていない
- **対処**: 環境変数`MODEL_ARN`の値を確認し、正しいARNを設定

#### エラー5: `No labels detected`
- **原因**: 画像からラベルが検出されなかった、または信頼度が70%未満
- **対処**: 
  - 画像が正しくアップロードされているか確認
  - Rekognition Custom Labelsモデルが正しく学習されているか確認
  - 信頼度の閾値（MinConfidence）を調整（lambda_function.py内）

### 10-4. 実際のS3アップロードでテスト

1. S3コンソールでバケットを開く
2. テスト用の画像をアップロード（パス: `users/{userId}/images/test.jpg`）
3. Lambda関数の「モニタリング」タブで実行を確認
4. CloudWatch Logsでログを確認

---

## 手順11: 動作確認チェックリスト

- [ ] Lambda関数が正常に作成された
- [ ] ZIPファイルが正常にアップロードされた
- [ ] 環境変数が正しく設定された（特に`MODEL_ARN`）
- [ ] IAMロールに必要な権限が付与された
  - [ ] Rekognition権限
  - [ ] DynamoDB権限
  - [ ] Lambda呼び出し権限（通知用）
- [ ] S3イベント通知が正しく設定された
- [ ] Lambda関数の直接テストが成功した
- [ ] `StampMasters`テーブルに`IMAGE`タイプのスタンプが登録されている
- [ ] `ImageLabel`フィールドが正しく設定されている
- [ ] 実際のS3アップロードでスタンプが付与されることを確認
- [ ] DynamoDBの`UserStamps`テーブルにスタンプが保存されることを確認
- [ ] 通知が送信されることを確認（通知関数が設定されている場合）

---

## トラブルシューティング

### CloudWatch Logsの確認方法

1. Lambda関数の「モニタリング」タブ
2. 「CloudWatch Logsの表示」をクリック
3. 最新のログストリームを開いてエラーログを確認

### ログ出力の確認

`lambda_function.py`では以下のログが出力されます:
- 受信した画像のS3キー
- 検出されたラベル
- スタンプ付与結果
- エラーメッセージ

### S3キーからユーザーIDが抽出できない場合

S3キーが想定外の形式の場合、`extract_user_id_from_s3_key`関数を修正するか、S3オブジェクトのメタデータからユーザーIDを取得する方法に変更してください。

### スタンプが付与されない場合

1. 検出されたラベル名が`StampMasters`テーブルの`ImageLabel`と完全に一致しているか確認
2. スタンプの`Type`が`IMAGE`であることを確認
3. 有効期間内であることを確認
4. ユーザーが既にそのスタンプを持っていないか確認（重複チェック）

---

## 次のステップ

1. **パフォーマンス最適化**: 
   - バッチ処理の実装
   - コールドスタート対策
2. **エラーハンドリングの改善**: 
   - より詳細なエラーレスポンスとログ出力
   - リトライロジックの追加
3. **セキュリティ強化**: 
   - S3バケットポリシーの設定
   - 画像検証の追加
4. **モニタリング**: 
   - CloudWatchアラームの設定
   - メトリクスの監視

---

## 参考リンク

- [AWS Lambda Python ランタイム](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)
- [Lambda 関数の Python ハンドラー](https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html)
- [Lambda 環境変数の使用](https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html)
- [Amazon Rekognition Custom Labels](https://docs.aws.amazon.com/rekognition/latest/customlabels-dg/what-is.html)
- [S3 イベント通知](https://docs.aws.amazon.com/AmazonS3/latest/userguide/NotificationHowTo.html)
- [Lambda と S3 の統合](https://docs.aws.amazon.com/lambda/latest/dg/with-s3.html)

---

**最終更新**: 2024年
**作成者**: 開発チーム

