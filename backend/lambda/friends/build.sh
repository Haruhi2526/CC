#!/bin/bash

# Lambda関数のパッケージングスクリプト
# このスクリプトは、Lambda関数とその依存関係をZIPファイルにパッケージ化します

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 一時ディレクトリを作成
TEMP_DIR=$(mktemp -d)
echo "一時ディレクトリ: $TEMP_DIR"

# Lambda関数ファイルをコピー
cp lambda_function.py "$TEMP_DIR/"
cp response_utils.py "$TEMP_DIR/"

# 依存関係をインストール
if [ -f requirements.txt ]; then
    pip install -r requirements.txt -t "$TEMP_DIR" --upgrade
fi

# ZIPファイルを作成
ZIP_FILE="friends.zip"
cd "$TEMP_DIR"
zip -r "$SCRIPT_DIR/$ZIP_FILE" . -x "*.pyc" "__pycache__/*" "*.dist-info/*"

# 一時ディレクトリを削除
cd "$SCRIPT_DIR"
rm -rf "$TEMP_DIR"

echo "パッケージング完了: $ZIP_FILE"
echo "ファイルサイズ: $(du -h $ZIP_FILE | cut -f1)"

