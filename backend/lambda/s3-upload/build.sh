#!/bin/bash

# s3-upload Lambda関数のZIPファイル作成スクリプト
# Mac環境からLinux環境（Lambda）にデプロイするための準備

set -e

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# 出力ファイル名
ZIP_FILE="lambda-s3-upload.zip"

# 既存のZIPファイルを削除
if [ -f "$ZIP_FILE" ]; then
    echo "既存のZIPファイルを削除: $ZIP_FILE"
    rm "$ZIP_FILE"
fi

# 一時ディレクトリを作成
TEMP_DIR=$(mktemp -d)
echo "一時ディレクトリ: $TEMP_DIR"

# 必要なPythonファイルをコピー
echo "Pythonファイルをコピー中..."
cp lambda_function.py "$TEMP_DIR/"
cp response_utils.py "$TEMP_DIR/"

# 依存ライブラリをインストール（オプション）
if [ -f "requirements.txt" ]; then
    echo "依存ライブラリをインストール中..."
    # Mac環境でインストール（現在は標準ライブラリのみなので問題なし）
    pip3 install -r requirements.txt -t "$TEMP_DIR/" --upgrade 2>/dev/null || {
        echo "警告: pip3でのインストールに失敗しました。標準ライブラリのみで続行します。"
    }
fi

# ZIPファイルを作成
echo "ZIPファイルを作成中: $ZIP_FILE"
cd "$TEMP_DIR"
zip -r "$OLDPWD/$ZIP_FILE" . -x "*.pyc" -x "__pycache__/*" -x "*.dist-info/*" -x "*.egg-info/*" 2>/dev/null || {
    # zipコマンドがない場合の代替（macOS標準）
    ditto -ck . "$OLDPWD/$ZIP_FILE"
}
cd "$OLDPWD"

# 一時ディレクトリを削除
rm -rf "$TEMP_DIR"

# ZIPファイルの内容を表示
echo ""
echo "ZIPファイルが作成されました: $ZIP_FILE"
echo ""
echo "ZIPファイルの内容:"
unzip -l "$ZIP_FILE" 2>/dev/null || {
    echo "（内容の表示に失敗しましたが、ZIPファイルは作成されています）"
}

echo ""
echo "✅ ビルド完了!"
echo ""
echo "次のステップ:"
echo "1. AWS Lambdaコンソールで関数を作成または更新"
echo "2. ZIPファイルをアップロード"
echo "3. 環境変数を設定（S3_BUCKET, S3_PREFIX, PRESIGNED_URL_EXPIRATION）"
echo "4. IAMロールにS3権限を追加（s3:PutObject）"
echo ""

