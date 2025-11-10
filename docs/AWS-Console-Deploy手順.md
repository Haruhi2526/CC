# AWS Console - Deploy手順

AWS Consoleを使用してスタンプラリーアプリケーション全体をデプロイする手順です。

## 目次

1. [概要](#概要)
2. [前提条件](#前提条件)
3. [デプロイフロー](#デプロイフロー)
4. [手順1: DynamoDBテーブルの作成](#手順1-dynamodbテーブルの作成)
5. [手順2: Lambda関数のデプロイ](#手順2-lambda関数のデプロイ)
6. [手順3: API Gatewayの設定](#手順3-api-gatewayの設定)
7. [手順4: 動作確認](#手順4-動作確認)
8. [トラブルシューティング](#トラブルシューティング)
9. [次のステップ](#次のステップ)

---

## 概要

このドキュメントでは、AWS Consoleを使用して以下のリソースをデプロイする手順を説明します：

- **DynamoDBテーブル**: データストレージ（Users, UserStamps, StampMasters）
- **Lambda関数**: バックエンドAPI（auth, award, gps-verify, notify, ranking, richmenu, stamps）
- **API Gateway**: REST APIエンドポイント
- **IAMロール**: Lambda関数の実行権限

> **注意**: 本手順はAWS Consoleを使用した手動デプロイです。  
> 将来的にはCloudFormationやSAMを使用した自動デプロイに移行することを推奨します。

---

## 前提条件

### 必要なもの

- AWSアカウントへのアクセス権限
- 以下のAWSサービスへの操作権限:
  - Lambda
  - DynamoDB
  - API Gateway
  - IAM
  - CloudWatch Logs
- ローカル開発環境:
  - Python 3.11以上
  - AWS CLI（オプション）
  - zipコマンド（macOS標準で利用可能）

### 確認事項

- AWS Consoleにログインできること
- 適切なリージョンが選択されていること（例: `ap-northeast-1`, `us-east-1`）
- プロジェクトのソースコードがローカルに存在すること

---

## デプロイフロー

デプロイは以下の順序で実行します：

```
1. DynamoDBテーブル作成
   ↓
2. Lambda関数のデプロイ（各関数を順次）
   ├─ auth
   ├─ award
   ├─ gps-verify
   ├─ notify
   ├─ ranking
   ├─ richmenu
   └─ stamps
   ↓
3. API Gatewayの設定
   ├─ REST API作成
   ├─ リソース・メソッド作成
   ├─ Lambda統合
   └─ CORS設定
   ↓
4. 動作確認
```

**推定所要時間**: 初回デプロイで約1〜2時間

---

## 手順1: DynamoDBテーブルの作成

### 1-1. テーブル一覧

以下の3つのテーブルを作成します：

| テーブル名 | パーティションキー | ソートキー | 説明 |
|-----------|------------------|-----------|------|
| **Users** | UserId (String) | - | ユーザー基本情報 |
| **UserStamps** | UserId (String) | StampId (String) | ユーザーのスタンプ収集状況 |
| **StampMasters** | StampId (String) | - | スタンプマスタ情報 |

### 1-2. 作成手順

詳細な手順は以下のドキュメントを参照してください：

📖 **[AWS-Console-DynamoDB設定手順.md](./AWS-Console-DynamoDB設定手順.md)**

### 1-3. 確認

- [ ] `Users`テーブルが作成されている
- [ ] `UserStamps`テーブルが作成されている
- [ ] `StampMasters`テーブルが作成されている
- [ ] すべてのテーブルが「アクティブ」状態である

---

## 手順2: Lambda関数のデプロイ

### 2-1. デプロイ対象のLambda関数

以下のLambda関数をデプロイします：

| 関数名 | 説明 | エンドポイント |
|--------|------|---------------|
| `stamp-rally-auth` | LINE認証 | `POST /auth/verify` |
| `stamp-rally-award` | スタンプ授与 | `POST /stamps/award` |
| `stamp-rally-gps-verify` | GPS位置情報検証 | `POST /gps/verify` |
| `stamp-rally-notify` | プッシュ通知 | `POST /notify` |
| `stamp-rally-ranking` | ランキング取得 | `GET /ranking/*` |
| `stamp-rally-richmenu` | リッチメニュー管理 | `GET/POST/DELETE /richmenu/*` |
| `stamp-rally-stamps` | スタンプ一覧取得 | `GET /stamps` |

### 2-2. 共通デプロイ手順

各Lambda関数は以下の共通手順でデプロイします：

#### Step 1: ZIPファイルの作成

各Lambda関数のディレクトリで`build.sh`スクリプトを実行します：

```bash
# 例: auth関数の場合
cd backend/lambda/auth
./build.sh
```

**build.shスクリプトの動作**:
- 必要なPythonファイルをコピー
- 依存ライブラリをインストール（requirements.txtがある場合）
- ZIPファイルを作成（例: `lambda-auth.zip`）

**各関数のZIPファイル名**:
- `lambda-auth.zip`
- `lambda-award.zip`
- `lambda-gps-verify.zip`
- `lambda-notify.zip`
- `lambda-ranking.zip`
- `lambda-richmenu.zip`
- `lambda-stamps.zip`

#### Step 2: Lambda関数の作成

1. **Lambdaコンソールを開く**
   - AWS Consoleで「Lambda」を検索
   - 「関数を作成」ボタンをクリック

2. **基本設定**
   - **関数の作成方法**: 「一から作成」を選択
   - **関数名**: 上記の関数名を入力（例: `stamp-rally-auth`）
   - **ランタイム**: `Python 3.11`
   - **アーキテクチャ**: `x86_64`（デフォルト）

3. **実行ロール**
   - 「新しいロールを作成」を選択
   - ロール名: `stamp-rally-{関数名}-role`（例: `stamp-rally-auth-role`）
   - 許可ポリシー: 後で設定（まずは基本ロールを作成）

4. **「関数を作成」をクリック**

#### Step 3: コードのアップロード

1. 作成したLambda関数の画面で「コード」タブを確認
2. 「アップロード元」ドロップダウンをクリック
3. 「.zipファイル」を選択
4. 「アップロード」ボタンをクリック
5. 作成したZIPファイルを選択（例: `lambda-auth.zip`）
6. 「保存」をクリック

#### Step 4: ハンドラーの確認

「ランタイム設定」セクションで以下を確認：

- **ハンドラー**: `lambda_function.lambda_handler`
  - 形式: `ファイル名.関数名`
  - すべての関数で共通

#### Step 5: 環境変数の設定

「設定」タブ → 「環境変数」→「編集」をクリック

**共通環境変数**:

| キー | 値 | 説明 |
|-----|-----|------|
| `TABLE_USERS` | `Users` | Usersテーブル名 |
| `TABLE_USERSTAMPS` | `UserStamps` | UserStampsテーブル名 |
| `TABLE_STAMPMASTERS` | `StampMasters` | StampMastersテーブル名 |

**関数固有の環境変数**:

| 関数名 | 追加環境変数 | 値 | 説明 |
|--------|------------|-----|------|
| `auth` | `TOKEN_SECRET_KEY` | `your-secret-key` | セッショントークン署名用キー（本番では必ず変更） |
| `notify` | `LINE_CHANNEL_ACCESS_TOKEN` | `{LINEトークン}` | LINE Messaging APIアクセストークン |
| `richmenu` | `LINE_CHANNEL_ACCESS_TOKEN` | `{LINEトークン}` | LINE Messaging APIアクセストークン |
| `award` | `NOTIFY_FUNCTION_NAME` | `stamp-rally-notify` | 通知関数名（オプション） |

> **重要**: `TOKEN_SECRET_KEY`は本番環境では必ず強力なランダムな文字列に変更してください。  
> 生成方法: `openssl rand -hex 32`

#### Step 6: IAMロールの設定

1. 「設定」タブ → 「実行ロール」をクリック
2. ロール名をクリックしてIAMコンソールを開く
3. 「許可を追加」→「ポリシーをアタッチ」をクリック

**必要な権限ポリシー**:

##### DynamoDBアクセス権限

各関数に必要なDynamoDBテーブルへのアクセス権限を付与します。

**JSONポリシー例**（最小権限）:

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
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": [
        "arn:aws:dynamodb:*:*:table/Users",
        "arn:aws:dynamodb:*:*:table/Users/index/*",
        "arn:aws:dynamodb:*:*:table/UserStamps",
        "arn:aws:dynamodb:*:*:table/UserStamps/index/*",
        "arn:aws:dynamodb:*:*:table/StampMasters",
        "arn:aws:dynamodb:*:*:table/StampMasters/index/*"
      ]
    }
  ]
}
```

**簡易版（開発環境のみ）**:
- AWS管理ポリシー: `AmazonDynamoDBReadWriteAccess` をアタッチ

##### CloudWatch Logs権限

- AWS管理ポリシー: `AWSLambdaBasicExecutionRole` をアタッチ

##### Lambda呼び出し権限（award関数のみ）

`award`関数が`notify`関数を呼び出す場合、以下の権限も必要：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "lambda:InvokeFunction",
      "Resource": "arn:aws:lambda:*:*:function:stamp-rally-notify"
    }
  ]
}
```

#### Step 7: タイムアウトとメモリの設定

「設定」タブ → 「一般設定」→「編集」をクリック

**推奨設定**:
- **タイムアウト**: `30秒`（デフォルト3秒では不足する可能性があるため）
- **メモリ**: `256 MB`（デフォルト128MBで問題ありませんが、256MBを推奨）

「保存」をクリック

### 2-3. 各関数の個別設定

#### auth関数

- **詳細手順**: [AWS-Console実装手順-auth関数.md](./AWS-Console実装手順-auth関数.md)
- **必要な環境変数**: `TABLE_USERS`, `TOKEN_SECRET_KEY`
- **必要な権限**: DynamoDB（Usersテーブル）

#### award関数

- **詳細手順**: [AWS-Console実装手順-award関数.md](./AWS-Console実装手順-award関数.md)
- **必要な環境変数**: `TABLE_USERSTAMPS`, `TABLE_STAMPMASTERS`, `NOTIFY_FUNCTION_NAME`（オプション）
- **必要な権限**: DynamoDB（UserStamps, StampMastersテーブル）、Lambda呼び出し（オプション）

#### gps-verify関数

- **必要な環境変数**: `TABLE_STAMPMASTERS`
- **必要な権限**: DynamoDB（StampMastersテーブル、読み取りのみ）

#### notify関数

- **詳細手順**: [LINE機能実装手順.md](./LINE機能実装手順.md)
- **必要な環境変数**: `LINE_CHANNEL_ACCESS_TOKEN`
- **必要な権限**: CloudWatch Logs

#### ranking関数

- **詳細手順**: [ランキング機能実装手順.md](./ランキング機能実装手順.md)
- **必要な環境変数**: `TABLE_RANKINGS`（存在する場合）, `TABLE_USERSTAMPS`, `TABLE_USERS`
- **必要な権限**: DynamoDB（UserStamps, Usersテーブル）

#### richmenu関数

- **詳細手順**: [LINE機能実装手順.md](./LINE機能実装手順.md)
- **必要な環境変数**: `LINE_CHANNEL_ACCESS_TOKEN`
- **必要な権限**: CloudWatch Logs

#### stamps関数

- **必要な環境変数**: `TABLE_USERSTAMPS`, `TABLE_STAMPMASTERS`
- **必要な権限**: DynamoDB（UserStamps, StampMastersテーブル）

### 2-4. デプロイ確認チェックリスト

各関数について以下を確認：

- [ ] ZIPファイルが正常にアップロードされた
- [ ] ハンドラーが正しく設定されている（`lambda_function.lambda_handler`）
- [ ] 環境変数が正しく設定された
- [ ] IAMロールに必要な権限が付与された
- [ ] タイムアウトとメモリが適切に設定された
- [ ] Lambda関数の直接テストが成功した（「テスト」タブで確認）

---

## 手順3: API Gatewayの設定

### 3-1. REST APIの作成

1. **API Gatewayコンソールを開く**
   - AWS Consoleで「API Gateway」を検索
   - 「APIを作成」ボタンをクリック

2. **APIタイプの選択**
   - **REST API**を選択
   - 「構築」をクリック

3. **APIの設定**
   - **プロトコル**: REST
   - **API名**: `stamp-rally-api`（または任意の名前）
   - **説明**: スタンプラリーAPI（オプション）
   - **エンドポイントタイプ**: リージョン（デフォルト）

4. **「APIの作成」をクリック**

### 3-2. リソースとメソッドの作成

以下のエンドポイントを作成します：

| リソースパス | HTTPメソッド | Lambda関数 | 説明 |
|------------|------------|-----------|------|
| `/auth/verify` | POST | `stamp-rally-auth` | LINE認証 |
| `/stamps` | GET | `stamp-rally-stamps` | スタンプ一覧取得 |
| `/stamps/award` | POST | `stamp-rally-award` | スタンプ授与 |
| `/gps/verify` | POST | `stamp-rally-gps-verify` | GPS位置情報検証 |
| `/notify` | POST | `stamp-rally-notify` | プッシュ通知 |
| `/ranking/weekly` | GET | `stamp-rally-ranking` | 週間ランキング |
| `/ranking/monthly` | GET | `stamp-rally-ranking` | 月間ランキング |
| `/richmenu/list` | GET | `stamp-rally-richmenu` | リッチメニュー一覧 |
| `/richmenu/set` | POST | `stamp-rally-richmenu` | リッチメニュー設定 |
| `/richmenu/unset` | DELETE | `stamp-rally-richmenu` | リッチメニュー解除 |

#### リソース作成手順（例: `/auth/verify`）

1. **リソースの作成**
   - 左メニューの「リソース」を選択
   - 「アクション」→「リソースの作成」をクリック
   - **リソースパス**: `auth`
   - 「リソースの作成」をクリック

2. **子リソースの作成**
   - 作成した`/auth`リソースを選択
   - 「アクション」→「リソースの作成」をクリック
   - **リソースパス**: `verify`
   - 「リソースの作成」をクリック

3. **メソッドの追加**
   - `/auth/verify`リソースを選択
   - 「アクション」→「メソッドの作成」→「POST」を選択
   - 「チェックマーク」をクリック

4. **Lambda統合の設定**
   - **統合タイプ**: Lambda関数
   - **Lambdaプロキシ統合を使用**: ✅ **チェックを入れる（重要！）**
   - **Lambda関数**: `stamp-rally-auth`を選択
   - **Lambdaリージョン**: 関数が作成されているリージョン
   - 「保存」をクリック
   - 権限の追加を求められたら「OK」をクリック

> **重要**: 「Lambdaプロキシ統合を使用」にチェックが入っていることを必ず確認してください。  
> チェックがないと、リクエストボディがLambda関数に正しく渡されません。

### 3-3. CORS設定

各リソースに対してCORSを有効化します。

#### CORS有効化手順

1. 対象のリソースを選択（例: `/auth/verify`）
2. 「アクション」→「CORSを有効化」をクリック
3. 以下の設定を確認:
   - **Access-Control-Allow-Origin**: `*`（開発環境）または特定のドメイン（本番環境）
   - **Access-Control-Allow-Headers**: `Content-Type,Authorization`
   - **Access-Control-Allow-Methods**: `POST,OPTIONS`（または該当するメソッド）
4. 「CORSを有効化して既存のCORSヘッダーを置き換える」をクリック

> **注意**: CORS設定後は必ずAPIを再デプロイしてください。

### 3-4. APIのデプロイ

1. **ステージの作成**
   - 「アクション」→「APIのデプロイ」をクリック
   - **デプロイされるステージ**: 「新しいステージ」を選択
   - **ステージ名**: `dev`（開発環境）または`prod`（本番環境）
   - **ステージの説明**: 開発環境（オプション）
   - 「デプロイ」をクリック

2. **呼び出しURLの確認**
   - デプロイ後、**呼び出しURL**が表示されます
   - 例: `https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/dev`
   - このURLをメモしてください

3. **エンドポイントURLの構築**
   - ベースURL: `https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/dev`
   - エンドポイント例: `https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/dev/auth/verify`

### 3-5. API Gateway設定確認チェックリスト

- [ ] REST APIが作成された
- [ ] すべてのリソースとメソッドが作成された
- [ ] 各メソッドにLambda統合が設定された
- [ ] 「Lambdaプロキシ統合を使用」にチェックが入っている
- [ ] CORSが有効化された
- [ ] APIがデプロイされた
- [ ] 呼び出しURLが取得できた

---

## 手順4: 動作確認

### 4-1. Lambda関数の直接テスト

各Lambda関数について、Lambdaコンソールの「テスト」タブで直接テストを実行します。

#### テストイベントの作成

1. Lambda関数の画面で「テスト」タブをクリック
2. 「新しいイベントを作成」をクリック
3. イベント名を入力（例: `test-auth-event`）
4. テストイベントJSONを入力

**テストイベント例（auth関数）**:

```json
{
  "httpMethod": "POST",
  "body": "{\"id_token\": \"test_token_12345\"}",
  "headers": {
    "Content-Type": "application/json"
  }
}
```

5. 「保存」をクリック
6. 「テスト」ボタンをクリック

#### テスト結果の確認

- **成功時**: ステータスコード200、適切なレスポンスボディ
- **エラー時**: エラーメッセージを確認、CloudWatch Logsで詳細を確認

### 4-2. API Gateway経由のテスト

#### curlコマンドでのテスト

```bash
# auth関数のテスト
curl -X POST https://{api-id}.execute-api.{region}.amazonaws.com/dev/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"id_token": "test_token_12345"}'

# stamps関数のテスト
curl -X GET "https://{api-id}.execute-api.{region}.amazonaws.com/dev/stamps?userId=test_user_123" \
  -H "Content-Type: application/json"

# award関数のテスト
curl -X POST https://{api-id}.execute-api.{region}.amazonaws.com/dev/stamps/award \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "stamp_id": "stamp_001",
    "method": "GPS"
  }'
```

#### Postmanでのテスト

1. Postmanを開く
2. 新しいリクエストを作成
3. メソッドとURLを設定
4. Headersに`Content-Type: application/json`を追加
5. BodyにJSONを入力
6. 「Send」をクリック

### 4-3. 動作確認チェックリスト

- [ ] すべてのLambda関数が正常に動作する
- [ ] API Gateway経由でエンドポイントにアクセスできる
- [ ] CORS設定が正しく機能する（ブラウザからのアクセスが可能）
- [ ] DynamoDBテーブルにデータが正しく保存される
- [ ] エラーハンドリングが正しく動作する
- [ ] CloudWatch Logsにログが出力される

---

## トラブルシューティング

### よくあるエラーと対処法

#### エラー1: `Unable to import module 'lambda_function'`

**原因**: ZIPファイルに必要なファイルが含まれていない

**対処**:
- ZIPファイルの内容を確認（`unzip -l lambda-{関数名}.zip`）
- すべての`.py`ファイルが含まれていることを確認
- `build.sh`スクリプトを再実行

#### エラー2: `AccessDeniedException: User is not authorized to perform: dynamodb:PutItem`

**原因**: IAMロールにDynamoDBの書き込み権限がない

**対処**:
- IAMロールにDynamoDB権限を追加
- 手順2-2のStep 6を参照

#### エラー3: `ResourceNotFoundException: Requested resource not found`

**原因**: DynamoDBテーブル名が間違っている、またはテーブルが存在しない

**対処**:
- 環境変数のテーブル名を確認
- DynamoDBコンソールでテーブルが存在することを確認
- リージョンが正しいことを確認

#### エラー4: API Gatewayから`{"message": "Internal server error"}`が返される

**原因**: Lambda関数でエラーが発生している、または統合設定が間違っている

**対処**:
1. Lambda関数のCloudWatch Logsを確認
2. 「Lambdaプロキシ統合を使用」にチェックが入っているか確認
3. Lambda関数の直接テストでエラーが発生するか確認

#### エラー5: CORSエラー（ブラウザコンソールに表示）

**原因**: CORS設定が正しく行われていない、またはAPIが再デプロイされていない

**対処**:
1. API GatewayでCORS設定を確認
2. APIを再デプロイ
3. ブラウザのキャッシュをクリア

### CloudWatch Logsの確認方法

1. Lambda関数の「モニタリング」タブ
2. 「CloudWatch Logsの表示」をクリック
3. 最新のログストリームを開いてエラーログを確認

### API Gatewayのログ確認

1. API Gatewayコンソールで対象のAPIを選択
2. 「ステージ」→対象のステージを選択
3. 「ログ/トレース」タブでCloudWatch Logsを確認

---

## 次のステップ

### 1. スタンプマスターデータの投入

`StampMasters`テーブルにスタンプマスターデータを投入します。

📖 **[DynamoDB-スタンプマスターデータ投入手順.md](./DynamoDB-スタンプマスターデータ投入手順.md)**

### 2. LINE Developers Consoleの設定

LINE Messaging APIの設定を行います。

📖 **[LINE機能実装手順.md](./LINE機能実装手順.md)**

### 3. フロントエンドの設定

LIFFアプリの設定とAPIエンドポイントの設定を行います。

📖 **[LIFFアプリ基本構造作成手順.md](./LIFFアプリ基本構造作成手順.md)**

### 4. セキュリティ強化

- `TOKEN_SECRET_KEY`をAWS Systems Manager Parameter StoreやSecrets Managerに移動
- API Gatewayに認証を追加
- レート制限の実装

### 5. モニタリングとアラート

- CloudWatchアラームの設定
- エラー率の監視
- パフォーマンスメトリクスの確認

### 6. 本番環境への移行

📖 **詳細手順**: [本番環境移行手順.md](./本番環境移行手順.md)

本番環境への移行では以下を実施します：
- 別のAWSアカウントまたはリージョンに本番環境を構築
- セキュリティ設定の強化（Secrets Manager、IAM最小権限、暗号化）
- 環境変数の本番用設定
- データ移行
- モニタリングとアラート設定

---

## 参考ドキュメント

### 個別関数の詳細手順

- [AWS-Console実装手順-auth関数.md](./AWS-Console実装手順-auth関数.md)
- [AWS-Console実装手順-award関数.md](./AWS-Console実装手順-award関数.md)
- [ランキング機能実装手順.md](./ランキング機能実装手順.md)
- [LINE機能実装手順.md](./LINE機能実装手順.md)

### その他の関連ドキュメント

- [AWS-Console-DynamoDB設定手順.md](./AWS-Console-DynamoDB設定手順.md)
- [環境変数設定ガイド.md](./環境変数設定ガイド.md)
- [API仕様書.md](./API仕様書.md)
- [API-Gateway統合設定確認.md](./API-Gateway統合設定確認.md)
- [CORS設定修正手順.md](./CORS設定修正手順.md)
- [本番環境移行手順.md](./本番環境移行手順.md)

---

## デプロイチェックリスト（全体）

### 事前準備
- [ ] AWSアカウントにアクセスできる
- [ ] 適切なリージョンが選択されている
- [ ] プロジェクトのソースコードがローカルに存在する

### DynamoDB
- [ ] `Users`テーブルが作成されている
- [ ] `UserStamps`テーブルが作成されている
- [ ] `StampMasters`テーブルが作成されている

### Lambda関数
- [ ] `stamp-rally-auth`がデプロイされている
- [ ] `stamp-rally-award`がデプロイされている
- [ ] `stamp-rally-gps-verify`がデプロイされている
- [ ] `stamp-rally-notify`がデプロイされている
- [ ] `stamp-rally-ranking`がデプロイされている
- [ ] `stamp-rally-richmenu`がデプロイされている
- [ ] `stamp-rally-stamps`がデプロイされている

### API Gateway
- [ ] REST APIが作成されている
- [ ] すべてのリソースとメソッドが作成されている
- [ ] Lambda統合が設定されている
- [ ] CORSが有効化されている
- [ ] APIがデプロイされている

### 動作確認
- [ ] すべてのLambda関数が正常に動作する
- [ ] API Gateway経由でエンドポイントにアクセスできる
- [ ] エラーハンドリングが正しく動作する

---

**最終更新**: 2025年1月  
**作成者**: 開発チーム

