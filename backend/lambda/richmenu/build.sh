#!/bin/bash

# richmenu Lambda関数のパッケージ作成スクリプト

set -e

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

echo "=== richmenu Lambda関数のパッケージ作成 ==="

# クリーンアップ
echo "既存のファイルをクリーンアップ..."
rm -rf package
rm -f lambda-richmenu.zip

# パッケージディレクトリを作成
mkdir -p package

# Lambda関数ファイルをコピー
echo "Lambda関数ファイルをコピー..."
cp lambda_function.py package/
cp response_utils.py package/

# 依存ライブラリをインストール
echo "依存ライブラリをインストール..."
# 警告を抑制するために --no-warn-conflicts オプションを追加
# richmenu関数ではaiobotocoreを使用しないため、依存関係の警告は無視して問題ない
pip install -r requirements.txt -t package/ --quiet --no-warn-conflicts 2>&1 | grep -v "dependency conflicts" || true

# 不要なファイルを削除
echo "不要なファイルを削除..."
find package -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
find package -type d -name "*.dist-info" -exec rm -r {} + 2>/dev/null || true
find package -type d -name "tests" -exec rm -r {} + 2>/dev/null || true
find package -type f -name "*.pyc" -delete 2>/dev/null || true

# ZIPファイルを作成
echo "ZIPファイルを作成..."
cd package
zip -r ../lambda-richmenu.zip . -q
cd ..

echo "=== パッケージ作成完了: lambda-richmenu.zip ==="
echo "ファイルサイズ: $(ls -lh lambda-richmenu.zip | awk '{print $5}')"

