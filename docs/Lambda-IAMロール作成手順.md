# Lambda IAMロール作成手順

このドキュメントでは、Lambda関数を実行するために必要な権限を全て持ったIAMロールの作成方法を説明します。

## 目次

1. [概要](#概要)
2. [必要な権限](#必要な権限)
3. [IAMロール作成手順（AWS Console）](#iamロール作成手順aws-console)
4. [IAMロール作成手順（AWS CLI）](#iamロール作成手順aws-cli)
5. [IAMポリシーJSON（完全版）](#iamポリシーjson完全版)
6. [各Lambda関数へのロール割り当て](#各lambda関数へのロール割り当て)
7. [トラブルシューティング](#トラブルシューティング)

---

## 概要

このプロジェクトのLambda関数は以下のAWSサービスを使用します：

- **DynamoDB**: データの保存・取得（Users, UserStamps, StampMasters, Friends, Rankingsテーブル）
- **Lambda**: 他のLambda関数の呼び出し（award関数がnotify関数を呼び出す）
- **CloudWatch Logs**: ログの書き込み（Lambdaのデフォルト機能）

---

## 必要な権限

### 1. DynamoDB権限

以下のテーブルへのアクセス権限が必要です：

| テーブル名 | 必要な操作 |
|-----------|-----------|
| **Users** | GetItem, PutItem, UpdateItem, Query |
| **UserStamps** | GetItem, PutItem, Query, Scan |
| **StampMasters** | GetItem |
| **Friends** | PutItem, Query |
| **Rankings** | PutItem, Query, DeleteItem |

### 2. Lambda権限

- 他のLambda関数の呼び出し（InvokeFunction）

### 3. CloudWatch Logs権限

- ログストリームの作成
- ログイベントの書き込み

---

## IAMロール作成手順（AWS Console）

この手順では、AWS Consoleを使用してIAMロールとポリシーを作成します。手順は2つのパートに分かれています：
1. **カスタムポリシーの作成**（先にポリシーを作成）
2. **IAMロールの作成**（作成したポリシーをアタッチ）

---

### パート1: カスタムポリシーの作成

#### ステップ1: IAMコンソールを開く

1. [AWS Console](https://console.aws.amazon.com/)にログイン
2. 画面上部の検索バーで「IAM」と入力
3. 検索結果から「IAM」をクリック

#### ステップ2: ポリシー作成画面を開く

1. 左メニューの「ポリシー」をクリック
2. 右上の「ポリシーを作成」ボタンをクリック

#### ステップ3: ポリシーエディタを選択

1. 「JSON」タブをクリック（デフォルトで「ビジュアルエディタ」が選択されています）
2. 既存のJSONを全て削除
3. 以下のJSONポリシーをコピーして貼り付け：

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Query",
                "dynamodb:Scan"
            ],
            "Resource": [
                "arn:aws:dynamodb:*:*:table/Users",
                "arn:aws:dynamodb:*:*:table/Users/*",
                "arn:aws:dynamodb:*:*:table/UserStamps",
                "arn:aws:dynamodb:*:*:table/UserStamps/*",
                "arn:aws:dynamodb:*:*:table/StampMasters",
                "arn:aws:dynamodb:*:*:table/StampMasters/*",
                "arn:aws:dynamodb:*:*:table/Friends",
                "arn:aws:dynamodb:*:*:table/Friends/*",
                "arn:aws:dynamodb:*:*:table/Rankings",
                "arn:aws:dynamodb:*:*:table/Rankings/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "lambda:InvokeFunction"
            ],
            "Resource": "arn:aws:lambda:*:*:function:*"
        }
    ]
}
```

**重要**: 環境変数でテーブル名にプレフィックス（例: `dev-Users`, `prod-Users`）を使用している場合は、以下のJSONを使用してください：

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Query",
                "dynamodb:Scan"
            ],
            "Resource": [
                "arn:aws:dynamodb:*:*:table/*Users",
                "arn:aws:dynamodb:*:*:table/*Users/*",
                "arn:aws:dynamodb:*:*:table/*UserStamps",
                "arn:aws:dynamodb:*:*:table/*UserStamps/*",
                "arn:aws:dynamodb:*:*:table/*StampMasters",
                "arn:aws:dynamodb:*:*:table/*StampMasters/*",
                "arn:aws:dynamodb:*:*:table/*Friends",
                "arn:aws:dynamodb:*:*:table/*Friends/*",
                "arn:aws:dynamodb:*:*:table/*Rankings",
                "arn:aws:dynamodb:*:*:table/*Rankings/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "lambda:InvokeFunction"
            ],
            "Resource": "arn:aws:lambda:*:*:function:*"
        }
    ]
}
```

4. JSONを貼り付けた後、「次へ」ボタンをクリック

#### ステップ4: ポリシーの検証と名前の設定

1. ポリシーが正しく検証されたことを確認（エラーメッセージが表示されないことを確認）
2. **ポリシー名**: `LambdaExecutionPolicy` を入力
3. **説明（オプション）**: `Lambda functions execution policy for stamp rally application` を入力
4. 「次へ」ボタンをクリック

#### ステップ5: ポリシーの確認と作成

1. ポリシーの内容を確認
2. 問題がなければ「ポリシーを作成」ボタンをクリック
3. 「ポリシーが正常に作成されました」というメッセージが表示されることを確認

---

### パート2: IAMロールの作成

#### ステップ1: ロール作成画面を開く

1. 左メニューの「ロール」をクリック
2. 右上の「ロールを作成」ボタンをクリック

#### ステップ2: 信頼されたエンティティタイプを選択

1. **信頼されたエンティティタイプ**: 「AWS のサービス」を選択
2. **ユースケース**: 下のリストから「Lambda」を選択
   - もし「Lambda」が表示されない場合は、検索バーで「Lambda」と検索
3. 「次へ」ボタンをクリック

#### ステップ3: 権限ポリシーを追加

1. 検索バーに「LambdaExecutionPolicy」と入力
2. 作成したポリシー `LambdaExecutionPolicy` にチェックを入れる
3. 「次へ」ボタンをクリック

**注意**: もしポリシーが表示されない場合は、ページをリロードするか、少し待ってから再度検索してください。

#### ステップ4: ロール名と説明を設定

1. **ロール名**: `LambdaExecutionRole` を入力
2. **説明（オプション）**: `IAM role for Lambda functions in stamp rally application` を入力
3. 「ロールを作成」ボタンをクリック

#### ステップ5: ロールの確認

1. 「ロールが正常に作成されました」というメッセージが表示されることを確認
2. 作成されたロール `LambdaExecutionRole` をクリックして詳細を確認

**確認項目**:

- **信頼関係タブ**:
  - 「信頼関係」タブをクリック
  - 「信頼ポリシーを編集」ボタンの下に、以下のような信頼ポリシーが表示されることを確認：

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
```

- **アクセス権限タブ**:
  - 「アクセス権限」タブをクリック
  - 「許可されたポリシー」セクションに `LambdaExecutionPolicy` が表示されることを確認
  - ポリシーの種類が「カスタマー管理」であることを確認

---

## 補足: AWS CLIでの作成方法（参考）

AWS Consoleでの作成が難しい場合や、自動化が必要な場合は、AWS CLIを使用することもできます。詳細は以下のコマンドを参考にしてください。

### ポリシーの作成

```bash
aws iam create-policy \
    --policy-name LambdaExecutionPolicy \
    --policy-document file://lambda-execution-policy.json \
    --description "Lambda functions execution policy for stamp rally application"
```

### ロールの作成とポリシーのアタッチ

```bash
# ロールを作成
aws iam create-role \
    --role-name LambdaExecutionRole \
    --assume-role-policy-document file://trust-policy.json \
    --description "IAM role for Lambda functions in stamp rally application"

# ポリシーをアタッチ（Arnは上記のコマンドで取得したものを使用）
aws iam attach-role-policy \
    --role-name LambdaExecutionRole \
    --policy-arn arn:aws:iam::123456789012:policy/LambdaExecutionPolicy
```

---

## 環境変数でテーブル名にプレフィックスを使用している場合

Lambda関数の環境変数でテーブル名にプレフィックス（例: `dev-Users`, `prod-Users`）を設定している場合、IAMポリシーのリソースARNも対応する必要があります。

### 確認方法

1. Lambda関数の「設定」タブ → 「環境変数」を確認
2. `TABLE_USERS`, `TABLE_USERSTAMPS` などの環境変数を確認
3. テーブル名にプレフィックスが含まれているか確認

### 対応方法

テーブル名にプレフィックスが含まれている場合は、ポリシー作成時に以下のJSONを使用してください（パート1のステップ3で使用）：

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Query",
                "dynamodb:Scan"
            ],
            "Resource": [
                "arn:aws:dynamodb:*:*:table/*Users",
                "arn:aws:dynamodb:*:*:table/*Users/*",
                "arn:aws:dynamodb:*:*:table/*UserStamps",
                "arn:aws:dynamodb:*:*:table/*UserStamps/*",
                "arn:aws:dynamodb:*:*:table/*StampMasters",
                "arn:aws:dynamodb:*:*:table/*StampMasters/*",
                "arn:aws:dynamodb:*:*:table/*Friends",
                "arn:aws:dynamodb:*:*:table/*Friends/*",
                "arn:aws:dynamodb:*:*:table/*Rankings",
                "arn:aws:dynamodb:*:*:table/*Rankings/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "lambda:InvokeFunction"
            ],
            "Resource": "arn:aws:lambda:*:*:function:*"
        }
    ]
}
```

**注意**: 既にポリシーを作成済みの場合は、ポリシーを編集してリソースARNを更新する必要があります。

---

## 各Lambda関数へのロール割り当て

すべてのLambda関数に作成したIAMロールを割り当てる必要があります。以下の手順で各関数にロールを設定します。

### AWS Consoleでの設定手順

#### ステップ1: Lambdaコンソールを開く

1. [AWS Console](https://console.aws.amazon.com/)にログイン
2. 画面上部の検索バーで「Lambda」と入力
3. 検索結果から「Lambda」をクリック

#### ステップ2: Lambda関数を選択

1. 左メニューの「関数」をクリック
2. 関数一覧から対象のLambda関数をクリック（例: `auth`）

#### ステップ3: 設定タブを開く

1. 関数の詳細画面で「設定」タブをクリック
2. 左側のメニューから「アクセス権限」をクリック

#### ステップ4: ロールを編集

1. 「実行ロール」セクションを確認
2. 「ロールを編集」ボタンをクリック

#### ステップ5: 既存のロールを選択

1. 「既存のロールを使用」を選択
2. 「既存のロール」のドロップダウンをクリック
3. リストから `LambdaExecutionRole` を選択
   - もし表示されない場合は、検索バーに「LambdaExecutionRole」と入力
4. 「保存」ボタンをクリック

#### ステップ6: 設定の確認

1. 「実行ロール」セクションに `LambdaExecutionRole` が表示されることを確認
2. ロールのARNが表示されていることを確認

### 設定が必要なLambda関数一覧

以下のすべてのLambda関数に対して、上記の手順を繰り返してロールを設定してください：

1. **auth** - 認証処理
2. **award** - スタンプ授与処理
3. **friends** - 友達管理処理
4. **gps-verify** - GPS検証処理
5. **notify** - 通知送信処理
6. **ranking** - ランキング処理
7. **richmenu** - リッチメニュー管理処理
8. **stamps** - スタンプ一覧取得処理

**注意**: 各関数の設定が完了したら、必ず「保存」ボタンをクリックしてください。

### 設定完了の確認

すべてのLambda関数にロールを設定した後、以下の方法で確認できます：

1. Lambda関数一覧画面で、各関数の「実行ロール」列を確認
2. すべての関数で `LambdaExecutionRole` が表示されていることを確認

**注意**: ロールの設定が反映されるまで数秒かかる場合があります。反映されない場合は、ページをリロードしてください。

---

## トラブルシューティング

### エラー: AccessDeniedException

**症状**: Lambda関数の実行時に `AccessDeniedException` が発生する

**原因**: IAMロールに必要な権限が不足している

**解決方法**:
1. Lambda関数のロールが正しく設定されているか確認
2. ロールにアタッチされているポリシーを確認
3. DynamoDBテーブル名が正しいか確認（環境変数でプレフィックスが設定されている場合）

### エラー: ResourceNotFoundException

**症状**: DynamoDBテーブルが見つからない

**原因**: 
- テーブル名が間違っている
- リージョンが間違っている
- 環境変数でテーブル名が設定されているが、IAMポリシーに含まれていない

**解決方法**:
1. 環境変数 `TABLE_USERS`, `TABLE_USERSTAMPS` などを確認
2. IAMポリシーのリソースARNに環境変数で設定されたテーブル名を含める
3. または、ワイルドカードを使用してすべてのテーブル名に対応

### エラー: Lambda関数の呼び出しに失敗

**症状**: `award` 関数から `notify` 関数の呼び出しに失敗する

**原因**: Lambda関数の呼び出し権限が不足している

**解決方法**:
1. IAMポリシーに `lambda:InvokeFunction` 権限が含まれているか確認
2. 呼び出すLambda関数のARNが正しいか確認
3. 環境変数 `NOTIFY_FUNCTION_NAME` が正しく設定されているか確認

### ログが出力されない

**症状**: CloudWatch Logsにログが表示されない

**原因**: CloudWatch Logsへの書き込み権限が不足している

**解決方法**:
1. IAMポリシーに `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents` 権限が含まれているか確認
2. Lambda関数のロールが正しく設定されているか確認

---

## セキュリティのベストプラクティス

1. **最小権限の原則**: 必要な権限のみを付与する
2. **リソースの特定**: 可能な限り特定のリソースARNを指定する（ワイルドカードの使用を最小限に）
3. **定期的な監査**: 定期的にIAMロールとポリシーを確認し、不要な権限を削除する
4. **環境ごとの分離**: 開発環境と本番環境で異なるロールを使用する

---

## 参考リンク

- [AWS IAM ロールの作成](https://docs.aws.amazon.com/ja_jp/IAM/latest/UserGuide/id_roles_create.html)
- [Lambda 実行ロール](https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/lambda-intro-execution-role.html)
- [DynamoDB アクセス制御](https://docs.aws.amazon.com/ja_jp/amazondynamodb/latest/developerguide/access-control.html)

