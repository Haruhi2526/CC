# AWS Console実装手順 - award関数

## 概要

このドキュメントでは、AWS Consoleを使用してaward関数（スタンプ授与）をLambdaにデプロイする手順を説明します。

**注意**: Mac環境でビルドしたものをLinux環境（Lambda）で動作させるため、依存ライブラリのビルドには注意が必要です。現在の実装は標準ライブラリのみを使用しているため、問題ありません。

---

## 事前準備

### 必要なもの
- AWSアカウントへのアクセス権限
- Lambda、DynamoDB、IAM、API Gatewayの操作権限
- 既に作成済みのDynamoDBテーブル（`UserStamps`テーブル、`StampMasters`テーブル）

### 確認事項
- DynamoDBテーブルが作成済みであること
- テーブル名（デフォルト: `UserStamps`, `StampMasters`）

---

## 手順1: ZIPファイルの作成

### 1-1. 作業ディレクトリに移動

```bash
cd /Users/takenouchiharuhi/Downloads/CC/backend/lambda/award
```

### 1-2. 依存ライブラリのインストール（必要に応じて）

現在の実装は標準ライブラリのみですが、`boto3`が必要です。

**重要**: Mac環境からLambda（Linux）にデプロイする場合、以下のいずれかの方法を使用してください。

#### 方法A: 既存のboto3をそのまま使用（推奨）

Lambdaランタイムにはboto3がプリインストールされていますが、最新版を使用したい場合のみインストールします。

```bash
# 仮想環境を作成（推奨）
python3 -m venv venv
source venv/bin/activate

# boto3をインストール（Linux互換版を取得）
# 注意: バージョン指定は引用符で囲む必要があります
pip install "boto3>=1.28.0" -t .

# または、requirements.txtを使用する方法（推奨）
pip install -r requirements.txt -t .
```

**注意**: Mac環境で`pip install`した場合、一部のライブラリがMac用にビルドされる可能性があります。現在は標準ライブラリのみ使用しているため問題ありませんが、将来的にC拡張を含むライブラリを使用する場合は、Dockerを使用してLinux環境でビルドしてください。

#### 方法B: Dockerを使用したビルド（将来的な実装時）

将来的にネイティブ依存関係がある場合:

```bash
# Dockerfileを作成してLinux環境でビルド
docker run --rm -v $(pwd):/var/task \
  public.ecr.aws/lambda/python:3.11 \
  /bin/bash -c "pip install -r requirements.txt -t python/lib/python3.11/site-packages/"
```

### 1-3. ZIPファイルの作成（自動化スクリプト使用 - 推奨）

```bash
# build.shスクリプトを実行
./build.sh
```

### 1-4. ZIPファイルの作成（手動）

Lambda関数に必要なファイルのみをZIPに含めます。

```bash
# 必要なファイルをZIP化
zip -r lambda-award.zip \
  lambda_function.py \
  dynamodb_utils.py \
  response_utils.py

# 依存ライブラリがある場合は、それらも含める
# （ただし、現在は標準ライブラリのみのため不要）
```

**ZIPファイルに含めるファイル:**
- `lambda_function.py` (メイン関数)
- `dynamodb_utils.py` (DynamoDBユーティリティ)
- `response_utils.py` (レスポンスユーティリティ)
- `boto3` (インストールした場合のみ、`boto3/` ディレクトリと `botocore/` ディレクトリ)

**含めないもの:**
- `requirements.txt` (デプロイには不要)
- `tests/` ディレクトリ
- `venv/` ディレクトリ
- `.pyc` ファイル（あれば）

### 1-5. ZIPファイルの確認

```bash
# ZIPファイルの内容を確認
unzip -l lambda-award.zip
```

期待される出力例:
```
Archive:  lambda-award.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
     4500  2024-01-01 10:00   lambda_function.py
     3200  2024-01-01 10:00   dynamodb_utils.py
     2000  2024-01-01 10:00   response_utils.py
---------                     -------
     9700                     3 files
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
- **関数名**: `stamp-rally-award` （または任意の名前）
- **ランタイム**: `Python 3.11`
- **アーキテクチャ**: `x86_64` （デフォルト）

#### 実行ロールの変更
- **デフォルトの実行ロールを使用**: 選択しない
- **既存のロールを使用**: 既存のロールがある場合
- **新しいロールを作成**: 新規作成する場合

**新しいロールを作成する場合:**
- ロール名: `stamp-rally-award-role`
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
4. 作成した `lambda-award.zip` を選択
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
| `TABLE_USERSTAMPS` | `UserStamps` | DynamoDB UserStampsテーブル名 |
| `TABLE_STAMPMASTERS` | `StampMasters` | DynamoDB StampMastersテーブル名 |

**注意**: 環境変数が設定されていない場合、デフォルト値（`UserStamps`, `StampMasters`）が使用されます。

### 4-3. 環境変数の保存

すべて追加したら「保存」をクリック

---

## 手順5: IAMロールの設定

### 5-1. IAMロールを確認

「設定」タブ → 「実行ロール」をクリック
- ロール名をクリックしてIAMコンソールを開く

### 5-2. 必要な権限ポリシーをアタッチ

#### DynamoDBアクセス権限

「許可を追加」→「ポリシーをアタッチ」をクリック

以下のポリシーをアタッチまたは作成:

**ポリシー名例**: `stamp-rally-award-dynamodb-policy`

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
        "dynamodb:UpdateItem",
        "dynamodb:Query"
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

**簡易版（すべてのテーブルへのアクセス - 開発環境のみ）**:
- AWS管理ポリシー: `AmazonDynamoDBReadWriteAccess` をアタッチ
- **注意**: 本番環境では上記のように最小権限を設定してください

### 5-3. CloudWatch Logs権限（オプション）

ログを出力する場合、以下のポリシーも必要:

- AWS管理ポリシー: `AWSLambdaBasicExecutionRole` をアタッチ

---

## 手順6: タイムアウトとメモリの設定

### 6-1. 一般設定を開く

「設定」タブ → 「一般設定」→「編集」をクリック

### 6-2. 推奨設定

- **タイムアウト**: `30秒` （デフォルト3秒では不足する可能性があるため）
- **メモリ**: `256 MB` （デフォルト128MBで問題ありませんが、256MBを推奨）

「保存」をクリック

---

## 手順7: API Gatewayとの統合（既存のAPIがある場合）

### 7-1. API Gatewayの確認

既にAPI Gatewayが作成されている場合、以下を設定します。

1. API Gatewayコンソールを開く
2. 対象のREST APIを選択
3. 「リソース」から `/stamps` リソースを確認（なければ作成）
4. `/stamps/award` リソースを作成（なければ）
5. `/stamps/award` にPOSTメソッドを追加

### 7-2. Lambda関数の統合

1. POSTメソッドを選択
2. 「統合リクエスト」をクリック
3. **統合タイプ**: Lambda関数
4. **Lambda関数**: `stamp-rally-award` を選択
5. 「保存」をクリック
6. 権限の追加を求められたら「OK」をクリック

### 7-3. CORS設定（必要に応じて）

1. `/stamps/award` リソースを選択
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
4. **呼び出しURL**をメモ（例: `https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/dev/stamps/award`）

---

## 手順8: テスト実行

### 8-1. Lambda関数の直接テスト

1. Lambda関数の画面で「テスト」タブをクリック
2. 「新しいイベントを作成」または既存のイベントを選択
3. イベント名: `test-award-event`

#### テストイベントJSON例:

```json
{
  "httpMethod": "POST",
  "body": "{\"user_id\": \"test_user_123\", \"stamp_id\": \"stamp_001\", \"method\": \"GPS\"}",
  "headers": {
    "Content-Type": "application/json"
  }
}
```

4. 「保存」をクリック
5. 「テスト」ボタンをクリック

### 8-2. テスト結果の確認

**成功時のレスポンス例**:
```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*"
  },
  "body": "{\"ok\": true, \"user_id\": \"test_user_123\", \"stamp_id\": \"stamp_001\", \"method\": \"GPS\", \"collected_at\": 1234567890, \"message\": \"Stamp awarded successfully\"}"
}
```

**エラーが発生した場合:**
- エラーメッセージを確認
- CloudWatch Logsを確認（「モニタリング」タブ → 「CloudWatch Logsの表示」）

### 8-3. よくあるエラーと対処法

#### エラー1: `Unable to import module 'lambda_function'`
- **原因**: ZIPファイルに必要なファイルが含まれていない
- **対処**: ZIPファイルの内容を確認し、すべての`.py`ファイルが含まれていることを確認

#### エラー2: `AccessDeniedException: User is not authorized to perform: dynamodb:PutItem`
- **原因**: IAMロールにDynamoDBの書き込み権限がない
- **対処**: 手順5でIAMロールにDynamoDB権限を追加

#### エラー3: `ResourceNotFoundException: Requested resource not found`
- **原因**: DynamoDBテーブル名が間違っている、またはテーブルが存在しない
- **対処**: 環境変数`TABLE_USERSTAMPS`、`TABLE_STAMPMASTERS`の値を確認し、DynamoDBコンソールでテーブルが存在することを確認

#### エラー4: `409 STAMP_ALREADY_EXISTS`
- **原因**: 既に同じスタンプを持っているユーザーに再度授与しようとしている（正常な動作）
- **対処**: 別のユーザーIDまたはスタンプIDでテストする

#### エラー5: `404 STAMP_NOT_FOUND`
- **原因**: スタンプマスタが存在しない
- **対処**: DynamoDBのStampMastersテーブルに対象のスタンプIDが存在することを確認

### 8-4. API Gateway経由のテスト

1. API Gatewayの呼び出しURLを取得（手順7-4でメモしたURL）
2. curlコマンドまたはPostmanでテスト:

```bash
curl -X POST https://c5nmu4q3di.execute-api.us-east-1.amazonaws.com/dev/stamps/award \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "stamp_id": "stamp_001",
    "method": "GPS"
  }'
```

**成功時のレスポンス例**:
```json
{
  "ok": true,
  "user_id": "test_user_123",
  "stamp_id": "stamp_001",
  "method": "GPS",
  "collected_at": 1234567890,
  "message": "Stamp awarded successfully"
}
```

---

## 手順9: 動作確認チェックリスト

- [ ] Lambda関数が正常に作成された
- [ ] ZIPファイルが正常にアップロードされた
- [ ] 環境変数が正しく設定された（`TABLE_USERSTAMPS`, `TABLE_STAMPMASTERS`）
- [ ] IAMロールにDynamoDB権限が付与された
- [ ] Lambda関数の直接テストが成功した
- [ ] DynamoDBのUserStampsテーブルにスタンプデータが保存された
- [ ] 重複チェックが正常に動作する（同じスタンプを再度授与しようとするとエラーになる）
- [ ] API Gateway経由のテストが成功した（API Gatewayを使用する場合）
- [ ] CORS設定が正しく行われた（API Gatewayを使用する場合）

---

## トラブルシューティング

### CloudWatch Logsの確認方法

1. Lambda関数の「モニタリング」タブ
2. 「CloudWatch Logsの表示」をクリック
3. 最新のログストリームを開いてエラーログを確認

### ログを追加する場合

`lambda_function.py`に以下のようにログ出力を追加できます:

```python
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    # ...
```

### テストデータの準備

DynamoDBのStampMastersテーブルにテスト用のスタンプマスタを追加する必要があります:

```json
{
  "StampId": "stamp_001",
  "Name": "テストスタンプ1",
  "Description": "これはテスト用のスタンプです",
  "Type": "GPS",
  "Location": {
    "lat": 35.6812,
    "lng": 139.7671,
    "radius": 100
  },
  "ValidFrom": 0,
  "ValidTo": 9999999999
}
```

---

## API仕様

### エンドポイント
`POST /stamps/award`

### リクエストボディ
```json
{
  "user_id": "USER_ID",
  "stamp_id": "STAMP_ID",
  "method": "GPS"  // または "IMAGE"
}
```

### レスポンス（成功時 - 200）
```json
{
  "ok": true,
  "user_id": "USER_ID",
  "stamp_id": "STAMP_ID",
  "method": "GPS",
  "collected_at": 1234567890,
  "message": "Stamp awarded successfully"
}
```

### エラーレスポンス

#### 400 VALIDATION_ERROR
必須パラメータが不足している場合:
```json
{
  "error": "Error",
  "message": "user_id is required",
  "error_code": "VALIDATION_ERROR"
}
```

#### 404 STAMP_NOT_FOUND
スタンプマスタが存在しない場合:
```json
{
  "error": "Error",
  "message": "Stamp not found: stamp_001",
  "error_code": "STAMP_NOT_FOUND"
}
```

#### 409 STAMP_ALREADY_EXISTS
既にスタンプを持っている場合:
```json
{
  "error": "Error",
  "message": "User already has this stamp: stamp_001",
  "error_code": "STAMP_ALREADY_EXISTS"
}
```

#### 400 STAMP_NOT_VALID_YET / STAMP_EXPIRED
有効期間外の場合:
```json
{
  "error": "Error",
  "message": "Stamp is not yet valid. Valid from: 1234567890",
  "error_code": "STAMP_NOT_VALID_YET"
}
```

#### 400 STAMP_TYPE_MISMATCH
スタンプタイプが不一致の場合:
```json
{
  "error": "Error",
  "message": "Stamp type mismatch. Expected: GPS, Got: IMAGE",
  "error_code": "STAMP_TYPE_MISMATCH"
}
```

---

## 次のステップ

1. **統合テスト**: GPS検証関数や画像認識関数との統合テスト
2. **エラーハンドリングの改善**: より詳細なエラーレスポンスとログ出力
3. **パフォーマンス最適化**: コールドスタート対策など
4. **セキュリティ強化**: 
   - リクエストの認証（セッショントークンの検証）
   - レート制限の実装

---

## 参考リンク

- [AWS Lambda Python ランタイム](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)
- [Lambda 関数の Python ハンドラー](https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html)
- [Lambda 環境変数の使用](https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html)
- [Docker を使用した Lambda デプロイパッケージの作成](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html#python-package-create-package-with-dependency)

---

**最終更新**: 2024年
**作成者**: 開発チーム

