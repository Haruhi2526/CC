# DynamoDB スタンプマスターデータ投入手順

AWS Console経由でStampMastersテーブルにデータを追加する手順です。

## 前提条件

- AWS Consoleにアクセスできること
- StampMastersテーブルが作成済みであること

## データ構造

StampMastersテーブルのスキーマ：

| 項目名 | 型 | 必須 | 説明 |
|--------|-----|------|------|
| StampId | String (パーティションキー) | ✅ | スタンプID |
| Name | String | ✅ | スタンプ名 |
| Description | String | - | 説明（オプション） |
| Type | String | ✅ | 収集タイプ（GPS/IMAGE） |
| Location | Map | ✅ | GPS座標（lat, lon, radius） |
| ImageLabel | String | - | 画像認識用ラベル（GPSの場合は不要） |
| ValidFrom | Number | - | 有効開始日時（Unixタイムスタンプ、オプション） |
| ValidTo | Number | - | 有効終了日時（Unixタイムスタンプ、オプション） |

## 投入するデータ

以下の6つのスタンプを追加します：

1. **STATUE-001** - Statue
2. **MONU-075** - 75th Monument
3. **SEV-001** - 7-Eleven
4. **YIL-001** - Yagami Innovation Laboratory
5. **BLD14-RM213** - Bldg 14 Room 213
6. **CUSTOM-001** - Custom Spot（テスト用/カスタムスポット）

## 手順

### 1. AWS Consoleにログイン

1. [AWS Console](https://console.aws.amazon.com/)にログイン
2. リージョンを確認（例: `us-east-1`）

### 2. DynamoDBコンソールを開く

1. 検索バーで「DynamoDB」と検索
2. 「DynamoDB」をクリック

### 3. StampMastersテーブルを開く

1. 左メニューの「テーブル」をクリック
2. テーブル一覧から「StampMasters」をクリック

### 4. アイテムを追加

各スタンプについて、以下の手順でアイテムを追加します。

#### 4.1. 「アイテムを作成」をクリック

テーブル画面の右上にある「アイテムを作成」ボタンをクリック

#### 4.2. JSONビューでアイテムを作成

AWS Consoleでは、JSONビューで直接編集できます。

1. **「JSON」タブを選択**
   - アイテム作成画面で「JSON」タブをクリック

2. **以下のJSON形式で記述**

各スタンプについて、以下の形式でJSONを入力してください：

```json
{
  "StampId": {
    "S": "STATUE-001"
  },
  "Name": {
    "S": "Statue"
  },
  "Type": {
    "S": "GPS"
  },
  "Location": {
    "M": {
      "lat": {
        "N": "35.55548"
      },
      "lon": {
        "N": "139.65428"
      },
      "radiusM": {
        "N": "15"
      }
    }
  }
}
```

**型の指定方法：**
- `"S"`: String（文字列）
- `"N"`: Number（数値）
- `"M"`: Map（オブジェクト）

#### 4.3. フォームビューでアイテムを作成（代替方法）

JSONビューではなく、フォームビューで入力する場合：

##### 必須フィールド

1. **StampId** (String)
   - パーティションキーとして設定
   - 値: スタンプID（例: `STATUE-001`）

2. **Name** (String)
   - 値: スタンプ名（例: `Statue`）

3. **Type** (String)
   - 値: `GPS`

4. **Location** (Map)
   - 「型を追加」→「Map」を選択
   - 「Location」という名前でフィールドを追加
   - Locationフィールドをクリックして展開
   - 「キーを追加」で以下を追加：
     - `lat` (Number型): 緯度（例: `35.55548`）
     - `lon` (Number型): 経度（例: `139.65428`）
     - `radiusM` (Number型): 半径（メートル）（例: `15`）

##### オプションフィールド

- **Description** (String): 説明があれば追加

### 5. 各スタンプのデータ（JSON形式）

以下のデータを順番に追加してください。AWS Consoleの「JSON」タブに貼り付けて使用できます。

#### スタンプ1: STATUE-001

```json
{
  "StampId": {
    "S": "STATUE-001"
  },
  "Name": {
    "S": "Statue"
  },
  "Type": {
    "S": "GPS"
  },
  "Location": {
    "M": {
      "lat": {
        "N": "35.55548"
      },
      "lon": {
        "N": "139.65428"
      },
      "radiusM": {
        "N": "15"
      }
    }
  }
}
```

#### スタンプ2: MONU-075

```json
{
  "StampId": {
    "S": "MONU-075"
  },
  "Name": {
    "S": "75th Monument"
  },
  "Type": {
    "S": "GPS"
  },
  "Location": {
    "M": {
      "lat": {
        "N": "35.55603"
      },
      "lon": {
        "N": "139.65371"
      },
      "radiusM": {
        "N": "15"
      }
    }
  }
}
```

#### スタンプ3: SEV-001

```json
{
  "StampId": {
    "S": "SEV-001"
  },
  "Name": {
    "S": "7-Eleven"
  },
  "Type": {
    "S": "GPS"
  },
  "Location": {
    "M": {
      "lat": {
        "N": "35.55578"
      },
      "lon": {
        "N": "139.65394"
      },
      "radiusM": {
        "N": "15"
      }
    }
  }
}
```

#### スタンプ4: YIL-001

```json
{
  "StampId": {
    "S": "YIL-001"
  },
  "Name": {
    "S": "Yagami Innovation Laboratory"
  },
  "Type": {
    "S": "GPS"
  },
  "Location": {
    "M": {
      "lat": {
        "N": "35.55536"
      },
      "lon": {
        "N": "139.65503"
      },
      "radiusM": {
        "N": "15"
      }
    }
  }
}
```

#### スタンプ5: BLD14-RM213

```json
{
  "StampId": {
    "S": "BLD14-RM213"
  },
  "Name": {
    "S": "Bldg 14 Room 213"
  },
  "Type": {
    "S": "GPS"
  },
  "Location": {
    "M": {
      "lat": {
        "N": "35.55542"
      },
      "lon": {
        "N": "139.65404"
      },
      "radiusM": {
        "N": "15"
      }
    }
  }
}
```

#### スタンプ6: CUSTOM-001

```json
{
  "StampId": {
    "S": "CUSTOM-001"
  },
  "Name": {
    "S": "Custom Spot"
  },
  "Type": {
    "S": "GPS"
  },
  "Location": {
    "M": {
      "lat": {
        "N": "35.57146607574908"
      },
      "lon": {
        "N": "139.64540828242127"
      },
      "radiusM": {
        "N": "15"
      }
    }
  }
}
```

### 6. アイテムの保存

各アイテムの入力が完了したら：

1. 画面下部の「アイテムを作成」ボタンをクリック
2. 確認画面で「作成」をクリック
3. 成功メッセージが表示されることを確認

### 7. 全データの確認

1. テーブル画面に戻る
2. 「アイテムを探索」タブを確認
3. 6つのアイテムが追加されていることを確認

## 補足：Pythonスクリプトを使用した一括投入（推奨）

AWS Consoleで1つずつ入力する代わりに、Pythonスクリプトを使用して一括でデータを投入できます。

### 前提条件

- Python 3.7以上がインストールされていること
- boto3がインストールされていること
- AWS CLIが設定されていること

### 手順

1. **スクリプトとデータファイルの場所を確認**

```bash
cd backend/scripts
ls -la
# add_stamp_masters.py と stamp_masters_data.json が存在することを確認
```

2. **boto3をインストール（未インストールの場合）**

```bash
pip3 install boto3
```

3. **スクリプトを実行**

```bash
python3 add_stamp_masters.py
```

4. **確認メッセージに「y」と入力**

スクリプトが実行され、5つのスタンプマスターが追加されます。

### カスタマイズ

環境変数でテーブル名やリージョンを指定できます：

```bash
export TABLE_STAMPMASTERS=StampMasters
export AWS_REGION=us-east-1
python3 add_stamp_masters.py
```

### AWS CLIを使用する場合

AWS CLIを使用して1つずつ追加する場合：

```bash
# 例: 1つのアイテムを追加
aws dynamodb put-item \
  --table-name StampMasters \
  --item '{
    "StampId": {"S": "STATUE-001"},
    "Name": {"S": "Statue"},
    "Type": {"S": "GPS"},
    "Location": {
      "M": {
        "lat": {"N": "35.55548"},
        "lon": {"N": "139.65428"},
        "radiusM": {"N": "15"}
      }
    }
  }'
```

## トラブルシューティング

### Locationフィールドの入力方法

1. 「型を追加」→「Map」を選択
2. 「Location」という名前でフィールドを追加
3. Locationフィールドをクリックして展開
4. 「キーを追加」で以下を追加：
   - `lat` (Number型): 緯度の値
   - `lon` (Number型): 経度の値
   - `radiusM` (Number型): 半径の値

### 型の指定方法

- **String**: 文字列
- **Number**: 数値（整数または小数）
- **Map**: オブジェクト（キー・値のペア）

### エラーが出る場合

- StampIdが重複していないか確認（パーティションキーは一意である必要がある）
- 必須フィールド（StampId, Name, Type, Location）がすべて入力されているか確認
- Locationの各フィールド（lat, lon, radiusM）が正しく入力されているか確認

## 次のステップ

データ投入後、以下を確認してください：

1. GPS検証Lambda関数から正しくデータが取得できるか
2. フロントエンドからGPS検証が正常に動作するか

テスト方法：
- API Gateway経由でGPS検証エンドポイントを呼び出し
- 各スタンプの座標付近でGPS検証を実行

---

**更新日**: 2025年11月

