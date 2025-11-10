# S3バケットCORS設定手順

## 問題

S3への直接アップロード時に以下のエラーが発生します：

```
Access to fetch at 'https://input-image-backets.s3.amazonaws.com/' from origin '...' 
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present 
on the requested resource.
```

## 原因

S3バケットにCORS設定がされていないため、ブラウザからの直接アップロードがブロックされています。

## 解決手順

### 手順1: S3コンソールを開く

1. AWSコンソールにログイン
2. サービス検索で「S3」と入力して選択
3. 対象のバケット（例: `input-image-backets`）を選択

### 手順2: CORS設定を追加

1. バケットの「アクセス許可」タブを開く
2. 「Cross-origin resource sharing (CORS)」セクションまでスクロール
3. 「編集」ボタンをクリック

### 手順3: CORS設定を入力

以下のCORS設定を入力します：

```json
[
    {
        "AllowedHeaders": [
            "*"
        ],
        "AllowedMethods": [
            "POST",
            "PUT",
            "GET",
            "HEAD"
        ],
        "AllowedOrigins": [
            "*"
        ],
        "ExposeHeaders": [
            "ETag",
            "x-amz-server-side-encryption",
            "x-amz-request-id",
            "x-amz-id-2"
        ],
        "MaxAgeSeconds": 3000
    }
]
```

**本番環境の場合**:
`AllowedOrigins`を特定のドメインに制限してください：

```json
[
    {
        "AllowedHeaders": [
            "*"
        ],
        "AllowedMethods": [
            "POST",
            "PUT",
            "GET",
            "HEAD"
        ],
        "AllowedOrigins": [
            "https://your-domain.com",
            "https://your-ngrok-url.ngrok-free.dev"
        ],
        "ExposeHeaders": [
            "ETag",
            "x-amz-server-side-encryption",
            "x-amz-request-id",
            "x-amz-id-2"
        ],
        "MaxAgeSeconds": 3000
    }
]
```

### 手順4: 設定を保存

1. 「変更を保存」をクリック
2. 設定が正しく保存されたことを確認

## 設定項目の説明

- **AllowedHeaders**: リクエストで許可されるヘッダー（`*`はすべて許可）
- **AllowedMethods**: 許可されるHTTPメソッド（Presigned POSTには`POST`が必要）
- **AllowedOrigins**: 許可されるオリジン（開発環境では`*`、本番環境では特定のドメイン）
- **ExposeHeaders**: ブラウザに公開されるレスポンスヘッダー
- **MaxAgeSeconds**: プリフライトリクエストのキャッシュ時間（秒）

## 動作確認

1. ブラウザの開発者ツール（F12）を開く
2. 「ネットワーク」タブを開く
3. 画像をアップロード
4. S3へのリクエストが成功することを確認
5. レスポンスヘッダーに`Access-Control-Allow-Origin`が含まれていることを確認

## トラブルシューティング

### エラーが続く場合

1. **CORS設定の確認**
   - S3バケットのCORS設定が正しく保存されているか確認
   - JSONの構文エラーがないか確認

2. **ブラウザのキャッシュをクリア**
   - ブラウザのキャッシュをクリアして再試行

3. **プリフライトリクエストの確認**
   - ネットワークタブでOPTIONSリクエストが成功しているか確認
   - OPTIONSリクエストが失敗している場合、CORS設定を見直す

4. **Presigned POSTのfieldsの確認**
   - Presigned POSTのfieldsが正しくFormDataに含まれているか確認
   - コンソールログで`formDataKeys`を確認

## 参考リンク

- [S3 CORS設定](https://docs.aws.amazon.com/AmazonS3/latest/userguide/cors.html)
- [Presigned POST](https://docs.aws.amazon.com/AmazonS3/latest/userguide/PresignedUrlUploadObject.html)

---

**最終更新**: 2024年
**作成者**: 開発チーム

