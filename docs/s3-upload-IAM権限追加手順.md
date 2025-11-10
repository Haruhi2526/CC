# s3-upload Lambda関数のIAM権限追加手順

## 問題

S3アップロード時に以下のエラーが発生します：

```
User: arn:aws:sts::182066454118:assumed-role/stamp-rally-s3-upload-role-18mrc4zv/stamp-rally-s3-upload 
is not authorized to perform: s3:PutObject on resource: "arn:aws:s3:::input-image-backets/users/..." 
because no identity-based policy allows the s3:PutObject action
```

## 原因

Lambda関数のIAMロールにS3への`PutObject`権限がないため、Presigned POST URLを生成できません。

**重要**: Presigned POST URLを生成するには、Lambda関数に`s3:PutObject`権限が必要です。これは、Presigned URLを生成する際に、S3がその権限をチェックするためです。

## 解決手順

### 手順1: Lambda関数のIAMロールを確認

1. AWS Lambdaコンソールを開く
2. `stamp-rally-s3-upload`関数を選択
3. 「設定」タブ → 「実行ロール」をクリック
4. ロール名（例: `stamp-rally-s3-upload-role-18mrc4zv`）をクリックしてIAMコンソールを開く

### 手順2: カスタムポリシーを作成

#### 2-1. IAMコンソールでポリシーを作成

1. IAMコンソールの左メニューから「ポリシー」をクリック
2. 「ポリシーを作成」ボタンをクリック
3. 「JSON」タブをクリック
4. 以下のJSONポリシーを貼り付け：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::input-image-backets/users/*"
      ]
    }
  ]
}
```

**注意**: バケット名（`input-image-backets`）は実際のバケット名に置き換えてください。

#### 2-2. ポリシー名を設定

1. 「次のステップ: タグ」をクリック（タグはオプション）
2. 「次のステップ: 確認」をクリック
3. **ポリシー名**: `stamp-rally-s3-upload-s3-policy` を入力
4. **説明**: `S3アップロード用Presigned URL生成権限` を入力
5. 「ポリシーの作成」をクリック

### 手順3: ポリシーをIAMロールにアタッチ

1. 作成したポリシー（`stamp-rally-s3-upload-s3-policy`）を選択
2. 「アクション」→「アタッチ」をクリック
3. Lambda関数のIAMロール（`stamp-rally-s3-upload-role-18mrc4zv`）を検索して選択
4. 「ポリシーをアタッチ」をクリック

### 手順4: 動作確認

1. フロントエンドで画像をアップロード
2. エラーが解消されることを確認

## 簡易版（開発環境のみ）

開発環境で迅速に動作確認したい場合：

1. Lambda関数のIAMロールを開く
2. 「許可を追加」→「ポリシーをアタッチ」をクリック
3. `AmazonS3FullAccess` を検索して選択
4. 「ポリシーをアタッチ」をクリック

**注意**: 本番環境では、上記のカスタムポリシーを使用して最小権限を設定してください。

## トラブルシューティング

### エラーが続く場合

1. **IAMロールの確認**
   - 正しいIAMロールにポリシーがアタッチされているか確認
   - ポリシーが正しく保存されているか確認

2. **バケット名の確認**
   - ポリシーのResourceに正しいバケット名が設定されているか確認
   - バケット名にタイポがないか確認

3. **権限の反映待ち**
   - IAM権限の変更は通常すぐに反映されますが、数秒待ってから再試行してください

## 参考リンク

- [IAMポリシーの作成](https://docs.aws.amazon.com/iam/latest/userguide/access_policies_create.html)
- [S3 Presigned POST](https://docs.aws.amazon.com/AmazonS3/latest/userguide/PresignedUrlUploadObject.html)

---

**最終更新**: 2024年
**作成者**: 開発チーム

