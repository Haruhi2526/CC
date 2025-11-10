# AWS Console実装手順 - auth関数

## 概要

このドキュメントでは、AWS Consoleを使用してauth関数（LINE認証）をLambdaにデプロイする手順を説明します。

**注意**: Mac環境でビルドしたものをLinux環境（Lambda）で動作させるため、依存ライブラリのビルドには注意が必要です。現在の実装は標準ライブラリのみを使用しているため、問題ありません。

---

## 事前準備

### 必要なもの
- AWSアカウントへのアクセス権限
- Lambda、DynamoDB、IAM、API Gatewayの操作権限
- 既に作成済みのDynamoDBテーブル（`Users`テーブル）

### 確認事項
- DynamoDBテーブルが作成済みであること
- テーブル名（デフォルト: `Users`）

---

## 手順1: ZIPファイルの作成

### 1-1. 作業ディレクトリに移動

```bash
cd /Users/takenouchiharuhi/Downloads/CC/backend/lambda/auth
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

将来的にPyJWTやline-bot-sdkなどのネイティブ依存関係がある場合:

```bash
# Dockerfileを作成してLinux環境でビルド
docker run --rm -v $(pwd):/var/task \
  public.ecr.aws/lambda/python:3.11 \
  /bin/bash -c "pip install -r requirements.txt -t python/lib/python3.11/site-packages/"
```

### 1-3. ZIPファイルの作成

Lambda関数に必要なファイルのみをZIPに含めます。

```bash
# 必要なファイルをZIP化
zip -r lambda-auth.zip \
  lambda_function.py \
  dynamodb_utils.py \
  response_utils.py \
  token_utils.py

# 依存ライブラリがある場合は、それらも含める
# （ただし、現在は標準ライブラリのみのため不要）
```

**ZIPファイルに含めるファイル:**
- `lambda_function.py` (メイン関数)
- `dynamodb_utils.py` (DynamoDBユーティリティ)
- `response_utils.py` (レスポンスユーティリティ)
- `token_utils.py` (トークン生成ユーティリティ)
- `boto3` (インストールした場合のみ、`boto3/` ディレクトリと `botocore/` ディレクトリ)

**含めないもの:**
- `requirements.txt` (デプロイには不要)
- `tests/` ディレクトリ
- `venv/` ディレクトリ
- `.pyc` ファイル（あれば）

### 1-4. ZIPファイルの確認

```bash
# ZIPファイルの内容を確認
unzip -l lambda-auth.zip
```

期待される出力例:
```
Archive:  lambda-auth.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
     5000  2024-01-01 10:00   lambda_function.py
     3000  2024-01-01 10:00   dynamodb_utils.py
     2000  2024-01-01 10:00   response_utils.py
     3500  2024-01-01 10:00   token_utils.py
---------                     -------
    13500                     4 files
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
- **関数名**: `stamp-rally-auth` （または任意の名前）
- **ランタイム**: `Python 3.11`
- **アーキテクチャ**: `x86_64` （デフォルト）

#### 実行ロールの変更
- **デフォルトの実行ロールを使用**: 選択しない
- **既存のロールを使用**: 既存のロールがある場合
- **新しいロールを作成**: 新規作成する場合

**新しいロールを作成する場合:**
- ロール名: `stamp-rally-auth-role`
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
4. 作成した `lambda-auth.zip` を選択
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
| `TABLE_USERS` | `Users` | DynamoDB Usersテーブル名 |
| `TOKEN_SECRET_KEY` | `your-secret-key-change-this-in-production` | セッショントークン署名用のシークレットキー（本番では必ず変更） |

**注意**: `TOKEN_SECRET_KEY` は本番環境では必ず強力なランダムな文字列に変更してください。

例: ランダムなキーを生成する場合:
```bash
# ターミナルで実行
openssl rand -hex 32
```

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

**ポリシー名例**: `stamp-rally-auth-dynamodb-policy`

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
        "arn:aws:dynamodb:*:*:table/Users",
        "arn:aws:dynamodb:*:*:table/Users/index/*"
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
3. 「リソース」から `/auth` リソースを確認（なければ作成）
4. `/auth/verify` または `/auth` にPOSTメソッドを追加

### 7-2. Lambda関数の統合

1. POSTメソッドを選択
2. 「統合リクエスト」をクリック
3. **統合タイプ**: Lambda関数
4. **Lambda関数**: `stamp-rally-auth` を選択
5. 「保存」をクリック
6. 権限の追加を求められたら「OK」をクリック

### 7-3. CORS設定（必要に応じて）

1. `/auth` リソースを選択
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
4. **呼び出しURL**をメモ（例: `https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/dev/auth/verify`）

---

## 手順8: テスト実行

### 8-1. Lambda関数の直接テスト

1. Lambda関数の画面で「テスト」タブをクリック
2. 「新しいイベントを作成」または既存のイベントを選択
3. イベント名: `test-auth-event`

#### テストイベントJSON例:

```json
{
  "httpMethod": "POST",
  "body": "{\"id_token\": \"test_token_12345\"}",
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
  "body": "{\"ok\": true, \"user_id\": \"test_token_12345\", \"display_name\": \"LINE User\", \"access_token\": \"...\"}"
}
```

**エラーが発生した場合:**
- エラーメッセージを確認
- CloudWatch Logsを確認（「モニタリング」タブ → 「CloudWatch Logsの表示」）

### 8-3. よくあるエラーと対処法

#### エラー1: `Unable to import module 'lambda_function'`
- **原因**: ZIPファイルに必要なファイルが含まれていない
- **対処**: ZIPファイルの内容を確認し、すべての`.py`ファイルが含まれていることを確認

#### エラー2: `AccessDeniedException: User is not authorized to perform: dynamodb:UpdateItem`
- **原因**: IAMロールにDynamoDBの書き込み権限がない
- **対処**: 手順5でIAMロールにDynamoDB権限を追加

#### エラー3: `ResourceNotFoundException: Requested resource not found`
- **原因**: DynamoDBテーブル名が間違っている、またはテーブルが存在しない
- **対処**: 環境変数`TABLE_USERS`の値を確認し、DynamoDBコンソールでテーブルが存在することを確認

### 8-4. API Gateway経由のテスト

1. API Gatewayの呼び出しURLを取得（手順7-4でメモしたURL）
2. curlコマンドまたはPostmanでテスト:

```bash
curl -X POST https://c5nmu4q3di.execute-api.us-east-1.amazonaws.com/dev/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"id_token": "test_token_12345"}'
```

---

## 手順9: 動作確認チェックリスト

- [ ] Lambda関数が正常に作成された
- [ ] ZIPファイルが正常にアップロードされた
- [ ] 環境変数が正しく設定された
- [ ] IAMロールにDynamoDB権限が付与された
- [ ] Lambda関数の直接テストが成功した
- [ ] DynamoDBのUsersテーブルにユーザーデータが保存された
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

---

## 次のステップ

1. **LINE IDトークン検証の実装**: モック実装から実際の検証ロジックに置き換える
2. **セキュリティ強化**: 
   - `TOKEN_SECRET_KEY`をAWS Systems Manager Parameter StoreやSecrets Managerに移動
   - API Gatewayに認証を追加
3. **エラーハンドリングの改善**: より詳細なエラーレスポンスとログ出力
4. **パフォーマンス最適化**: コールドスタート対策など

---

## 参考リンク

- [AWS Lambda Python ランタイム](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)
- [Lambda 関数の Python ハンドラー](https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html)
- [Lambda 環境変数の使用](https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html)
- [Docker を使用した Lambda デプロイパッケージの作成](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html#python-package-create-package-with-dependency)

---

**最終更新**: 2024年
**作成者**: 開発チーム

