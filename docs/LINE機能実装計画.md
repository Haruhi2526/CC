# LINE機能実装計画

**作成日**: 2025年11月  
**対象機能**:
1. LINE Messaging API（プッシュ通知機能）
2. リッチメニュー実装
3. 友達シェア・ランキング機能
4. グループ連携機能

---

## 📋 実装概要

本計画では、4つのLINE機能を段階的に実装します。各機能は独立して動作しますが、連携することでより強力な体験を提供します。

---

## 🎯 Phase 1: 基盤整備（Week 1-2）

### 1.1 LINE Messaging API設定
**期間**: 1-2日  
**担当**: 全員（初期設定）

#### 作業内容
1. **LINE Developers Console設定**
   - Messaging APIチャンネルの有効化確認
   - Channel Access Tokenの発行・取得
   - Webhook URLの設定（ngrok経由で初期テスト）

2. **AWS Secrets Manager設定**
   - Channel Access Tokenの安全な保存
   - 環境変数からの移行準備

3. **環境変数追加**
   - `LINE_CHANNEL_ACCESS_TOKEN`: Secrets Manager ARN参照
   - `LINE_CHANNEL_SECRET`: Secrets Manager ARN参照（将来的に使用）

#### 成果物
- [ ] Secrets Managerにトークン保存完了
- [ ] 環境変数設定ドキュメント更新

---

### 1.2 リッチメニュー実装（最優先）
**期間**: 2-3日  
**担当**: フロントエンド担当者A

#### 作業内容

**Step 1: リッチメニューデザイン作成**
- メニュー構造の設計
  ```
  メニュー1: ホーム | スタンプ一覧
  メニュー2: マップ | ランキング
  ```
- 画像アセットの準備（必要に応じて）

**Step 2: LINE Developers Console設定**
- リッチメニューA（通常時）の作成
  - 「ホーム」: LIFF URL遷移
  - 「スタンプ一覧」: LIFF URL遷移（stamps.html）
  - 「マップ」: LIFF URL遷移（map.html）- 将来実装
  - 「ランキング」: LIFF URL遷移（ranking.html）- Phase 3で実装
- リッチメニューB（イベント時）の作成（オプション）

**Step 3: Lambda関数実装（リッチメニュー切り替え）**
- `backend/lambda/richmenu/lambda_function.py` 作成
  - リッチメニュー一覧取得
  - リッチメニュー設定（ユーザー別・イベント別）
  - リッチメニュー削除

#### 実装ファイル

**`backend/lambda/richmenu/lambda_function.py`**
```python
import json
import os
import requests
from response_utils import create_response

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
LINE_API_BASE_URL = 'https://api.line.me/v2/bot'

def lambda_handler(event, context):
    """リッチメニュー管理API"""
    try:
        if event.get('httpMethod') == 'OPTIONS':
            return create_response(200, {})
        
        method = event.get('httpMethod')
        path = event.get('path', '')
        
        if method == 'GET' and '/richmenu/list' in path:
            # リッチメニュー一覧取得
            return get_richmenu_list()
        elif method == 'POST' and '/richmenu/set' in path:
            # リッチメニュー設定
            body = json.loads(event.get('body', '{}'))
            user_id = body.get('user_id')
            richmenu_id = body.get('richmenu_id')
            return set_richmenu(user_id, richmenu_id)
        else:
            return create_response(404, {'error': 'Not Found'})
    except Exception as e:
        return create_response(500, {'error': str(e)})

def get_richmenu_list():
    """リッチメニュー一覧を取得"""
    url = f'{LINE_API_BASE_URL}/richmenu/list'
    headers = {'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'}
    response = requests.get(url, headers=headers)
    return create_response(200, response.json())

def set_richmenu(user_id, richmenu_id):
    """ユーザーにリッチメニューを設定"""
    url = f'{LINE_API_BASE_URL}/user/{user_id}/richmenu/{richmenu_id}'
    headers = {'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'}
    response = requests.post(url, headers=headers)
    return create_response(200, {'ok': True})
```

**`backend/lambda/richmenu/requirements.txt`**
```
boto3>=1.28.0
requests>=2.31.0
```

#### API Gateway設定
- `/richmenu/list` (GET)
- `/richmenu/set` (POST)

#### 成果物
- [ ] リッチメニュー作成完了（LINE Developers Console）
- [ ] Lambda関数実装完了
- [ ] API Gateway統合完了
- [ ] 動作確認完了

---

## 🎯 Phase 2: プッシュ通知機能（Week 2-3）

### 2.1 notify Lambda関数実装
**期間**: 3-4日  
**担当**: バックエンド担当者B

#### 作業内容

**Step 1: 依存ライブラリの準備**
- `line-bot-sdk-python` を Lambdaレイヤーまたはパッケージに含める
- Docker環境でのビルド（Mac環境の場合）

**Step 2: notify Lambda関数実装**
- `backend/lambda/notify/lambda_function.py` 作成
  - スタンプ取得通知
  - イベント通知
  - リマインド通知

**Step 3: award関数との統合**
- スタンプ授与完了時にnotify関数を呼び出す
- エラーハンドリング（通知失敗でもスタンプ授与は成功）

#### 実装ファイル

**`backend/lambda/notify/lambda_function.py`**
```python
import json
import os
from linebot import LineBotApi
from linebot.models import TextSendMessage, FlexSendMessage
from response_utils import create_response

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

def lambda_handler(event, context):
    """
    プッシュ通知を送信
    POST /notify
    {
        "user_id": "USER_ID",
        "type": "stamp_awarded" | "event_started" | "reminder",
        "data": {
            "stamp_id": "STAMP_ID",
            "stamp_name": "スタンプ名",
            ...
        }
    }
    """
    try:
        if event.get('httpMethod') == 'OPTIONS':
            return create_response(200, {})
        
        body = json.loads(event.get('body', '{}'))
        user_id = body.get('user_id')
        notify_type = body.get('type', 'stamp_awarded')
        data = body.get('data', {})
        
        if not user_id:
            return create_response(400, {'error': 'user_id is required'})
        
        # 通知タイプに応じてメッセージを生成
        if notify_type == 'stamp_awarded':
            message = create_stamp_flex_message(data.get('stamp_name', 'スタンプ'))
        elif notify_type == 'event_started':
            message = create_event_text_message(data.get('event_name', 'イベント'))
        elif notify_type == 'reminder':
            message = create_reminder_text_message(data.get('stamp_name', 'スタンプ'))
        else:
            return create_response(400, {'error': 'Invalid notification type'})
        
        # プッシュ通知送信
        line_bot_api.push_message(user_id, message)
        
        return create_response(200, {'ok': True})
        
    except Exception as e:
        # 通知失敗はログに記録するが、エラーは返さない（非同期処理のため）
        print(f'Notification failed: {str(e)}')
        return create_response(200, {'ok': False, 'error': str(e)})

def create_stamp_flex_message(stamp_name):
    """スタンプ取得通知用のFlex Messageを生成"""
    return FlexSendMessage(
        alt_text=f"{stamp_name}を獲得しました！",
        contents={
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": "https://example.com/stamp-icon.png",
                "size": "full",
                "aspectRatio": "20:13"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "🎉 スタンプ獲得！",
                        "weight": "bold",
                        "size": "xl",
                        "color": "#1DB446"
                    },
                    {
                        "type": "text",
                        "text": stamp_name,
                        "size": "md",
                        "margin": "md",
                        "wrap": True
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "スタンプ一覧を見る",
                            "uri": f"{os.environ.get('LIFF_BASE_URL', '')}/stamps.html"
                        },
                        "style": "primary"
                    }
                ]
            }
        }
    )

def create_event_text_message(event_name):
    """イベント開始通知"""
    return TextSendMessage(text=f"📢 新イベント開始！\n{event_name}")

def create_reminder_text_message(stamp_name):
    """リマインド通知"""
    return TextSendMessage(text=f"⏰ まだ取得していないスタンプがあります\n{stamp_name}")
```

**`backend/lambda/notify/requirements.txt`**
```
boto3>=1.28.0
line-bot-sdk>=3.0.0
```

**`backend/lambda/award/lambda_function.py` への統合**
```python
# award関数の成功時に通知を送信（非同期）
import boto3

lambda_client = boto3.client('lambda')

# スタンプ授与成功後
try:
    lambda_client.invoke(
        FunctionName='notify',
        InvocationType='Event',  # 非同期実行
        Payload=json.dumps({
            'httpMethod': 'POST',
            'body': json.dumps({
                'user_id': user_id,
                'type': 'stamp_awarded',
                'data': {
                    'stamp_id': stamp_id,
                    'stamp_name': stamp_master.get('Name', 'スタンプ')
                }
            })
        })
    )
except Exception as e:
    # 通知失敗はログのみ（スタンプ授与は成功）
    print(f'Failed to send notification: {str(e)}')
```

#### DynamoDB: 通知設定テーブル追加（オプション）
**テーブル名**: NotificationSettings
- パーティションキー: UserId
- 属性: PushEnabled (Boolean), NotificationTypes (List)

#### API Gateway設定
- `/notify` (POST)

#### 成果物
- [ ] notify Lambda関数実装完了
- [ ] award関数との統合完了
- [ ] Flex Messageテンプレート作成完了
- [ ] 動作確認完了

---

## 🎯 Phase 3: 友達シェア・ランキング機能（Week 3-4）

### 3.1 ランキング機能実装
**期間**: 5-6日  
**担当**: バックエンド担当者B + フロントエンド担当者A

#### 作業内容

**Step 1: DynamoDBテーブル設計・作成**
- Rankingsテーブル
  - パーティションキー: Period (例: "2025-11" 月間, "2025-W45" 週間)
  - ソートキー: Rank (数値)
  - GSI: UserId-Timestamp-index
    - パーティションキー: UserId
    - ソートキー: Timestamp

**Step 2: ranking Lambda関数実装**
- `backend/lambda/ranking/lambda_function.py` 作成
  - ランキング計算（日次バッチ処理）
  - ランキング取得（週間・月間）
  - 友達との比較

**Step 3: フロントエンド実装**
- ランキング表示画面（`ranking.html`）
- シェア機能（`liff.shareTargetPicker()`）

#### 実装ファイル

**`backend/lambda/ranking/lambda_function.py`**
```python
import json
import boto3
from datetime import datetime, timedelta
from response_utils import create_response

dynamodb = boto3.resource('dynamodb')
rankings_table = dynamodb.Table('Rankings')
user_stamps_table = dynamodb.Table('UserStamps')

def lambda_handler(event, context):
    """
    ランキング関連API
    GET /ranking/calculate - ランキング計算（バッチ処理用）
    GET /ranking/weekly?period=2025-W45 - 週間ランキング取得
    GET /ranking/monthly?period=2025-11 - 月間ランキング取得
    GET /ranking/compare?user_id=XXX&friend_id=YYY - 友達比較
    """
    try:
        if event.get('httpMethod') == 'OPTIONS':
            return create_response(200, {})
        
        method = event.get('httpMethod')
        path = event.get('path', '')
        query_params = event.get('queryStringParameters') or {}
        
        if method == 'POST' and '/ranking/calculate' in path:
            # ランキング計算
            period_type = query_params.get('type', 'weekly')  # weekly or monthly
            return calculate_rankings(period_type)
        elif method == 'GET' and '/ranking/weekly' in path:
            # 週間ランキング取得
            period = query_params.get('period') or get_current_week_period()
            return get_weekly_rankings(period)
        elif method == 'GET' and '/ranking/monthly' in path:
            # 月間ランキング取得
            period = query_params.get('period') or get_current_month_period()
            return get_monthly_rankings(period)
        elif method == 'GET' and '/ranking/compare' in path:
            # 友達比較
            user_id = query_params.get('user_id')
            friend_id = query_params.get('friend_id')
            return compare_users(user_id, friend_id)
        else:
            return create_response(404, {'error': 'Not Found'})
            
    except Exception as e:
        return create_response(500, {'error': str(e)})

def calculate_rankings(period_type='weekly'):
    """ランキングを計算してDynamoDBに保存"""
    period = get_current_week_period() if period_type == 'weekly' else get_current_month_period()
    
    # UserStampsテーブルから全ユーザーのスタンプ数を集計
    # （スキャンは非効率なので、実際はCloudWatch Eventsで日次実行）
    # ここでは簡略化した実装
    
    # ランキングデータを保存
    # ...実装...
    
    return create_response(200, {'ok': True, 'period': period})

def get_weekly_rankings(period):
    """週間ランキングを取得"""
    response = rankings_table.query(
        KeyConditionExpression='Period = :period',
        ExpressionAttributeValues={
            ':period': f'weekly-{period}'
        },
        Limit=100,
        ScanIndexForward=False  # 降順（ランク1から）
    )
    
    rankings = []
    for item in response.get('Items', []):
        rankings.append({
            'rank': item.get('Rank'),
            'user_id': item.get('UserId'),
            'stamp_count': item.get('StampCount'),
            'display_name': item.get('DisplayName')
        })
    
    return create_response(200, {
        'ok': True,
        'period': period,
        'rankings': rankings
    })

def get_monthly_rankings(period):
    """月間ランキングを取得"""
    # 週間と同様の実装
    pass

def compare_users(user_id, friend_id):
    """2人のユーザーを比較"""
    # 両ユーザーのスタンプ数を取得して比較
    pass

def get_current_week_period():
    """現在の週の期間文字列を返す（例: "2025-W45"）"""
    now = datetime.now()
    year, week, _ = now.isocalendar()
    return f"{year}-W{week:02d}"

def get_current_month_period():
    """現在の月の期間文字列を返す（例: "2025-11"）"""
    now = datetime.now()
    return f"{now.year}-{now.month:02d}"
```

**`backend/lambda/ranking/requirements.txt`**
```
boto3>=1.28.0
```

**フロントエンド: `frontend/liff-app/ranking.html`**
```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ランキング - スタンプラリー</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container">
        <h1>🏆 ランキング</h1>
        
        <div class="tabs">
            <button class="tab active" data-period="weekly">週間</button>
            <button class="tab" data-period="monthly">月間</button>
        </div>
        
        <div id="rankingsContainer">
            <div class="loading">読み込み中...</div>
        </div>
        
        <button id="shareButton" class="primary-button">結果をシェア</button>
    </div>
    
    <script src="https://static.line-scdn.net/liff/edge/2/sdk.js"></script>
    <script src="js/config.js"></script>
    <script src="js/api.js"></script>
    <script src="js/ranking.js"></script>
</body>
</html>
```

**フロントエンド: `frontend/liff-app/js/ranking.js`**
```javascript
// ランキング画面のロジック
const elements = {
    rankingsContainer: document.getElementById('rankingsContainer'),
    shareButton: document.getElementById('shareButton'),
    tabs: document.querySelectorAll('.tab')
};

let currentPeriod = 'weekly';

// タブ切り替え
elements.tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        elements.tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        currentPeriod = tab.dataset.period;
        loadRankings(currentPeriod);
    });
});

// ランキング読み込み
async function loadRankings(period) {
    try {
        const endpoint = period === 'weekly' 
            ? '/ranking/weekly' 
            : '/ranking/monthly';
        const response = await api.getRankings(endpoint);
        displayRankings(response.rankings);
    } catch (error) {
        console.error('ランキング取得失敗:', error);
        elements.rankingsContainer.innerHTML = '<p class="error">ランキングの取得に失敗しました</p>';
    }
}

// ランキング表示
function displayRankings(rankings) {
    if (!rankings || rankings.length === 0) {
        elements.rankingsContainer.innerHTML = '<p>ランキングデータがありません</p>';
        return;
    }
    
    let html = '<ol class="ranking-list">';
    rankings.forEach(entry => {
        html += `
            <li class="ranking-item">
                <span class="rank">${entry.rank}位</span>
                <span class="name">${entry.display_name}</span>
                <span class="count">${entry.stamp_count}個</span>
            </li>
        `;
    });
    html += '</ol>';
    
    elements.rankingsContainer.innerHTML = html;
}

// シェア機能
elements.shareButton.addEventListener('click', async () => {
    if (typeof liff !== 'undefined' && liff.isApiAvailable('shareTargetPicker')) {
        const shareUrl = `${CONFIG.LIFF_BASE_URL}/ranking.html`;
        await liff.shareTargetPicker([
            {
                type: 'text',
                text: `スタンプラリーランキングを見てみて！\n${shareUrl}`
            }
        ]);
    } else {
        // フォールバック: URLをクリップボードにコピー
        navigator.clipboard.writeText(shareUrl);
        alert('URLをクリップボードにコピーしました');
    }
});

// 初期化
liff.init({ liffId: CONFIG.LIFF_ID })
    .then(() => {
        if (liff.isLoggedIn()) {
            loadRankings(currentPeriod);
        } else {
            liff.login();
        }
    });
```

**`frontend/liff-app/js/api.js` への追加**
```javascript
// api.jsに追加
async function getRankings(endpoint) {
    const response = await fetch(`${CONFIG.API_BASE_URL}${endpoint}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    });
    // ... エラーハンドリング ...
    return await response.json();
}
```

#### API Gateway設定
- `/ranking/calculate` (POST)
- `/ranking/weekly` (GET)
- `/ranking/monthly` (GET)
- `/ranking/compare` (GET)

#### CloudWatch Events設定（ランキング計算の自動実行）
- 日次バッチ処理（毎日午前1時）
- EventBridgeルールでLambda関数を定期実行

#### 成果物
- [ ] Rankingsテーブル作成完了
- [ ] ranking Lambda関数実装完了
- [ ] ランキング画面実装完了
- [ ] シェア機能実装完了
- [ ] バッチ処理設定完了

---

## 🎯 Phase 4: グループ連携機能（Week 4-5）

### 4.1 Webhook実装
**期間**: 4-5日  
**担当**: バックエンド担当者B

#### 作業内容

**Step 1: Webhook Lambda関数実装**
- `backend/lambda/webhook/lambda_function.py` 作成
  - LINE Webhookイベントの受信・検証
  - グループイベントの処理
  - メッセージイベントの処理（自動応答）

**Step 2: DynamoDBテーブル設計**
- Groupsテーブル
  - パーティションキー: GroupId
  - 属性: GroupName, CreatedAt, MemberCount
- GroupMembersテーブル
  - パーティションキー: GroupId
  - ソートキー: UserId

**Step 3: グループ機能実装**
- グループ内スタンプ共有
- グループ単位ランキング

#### 実装ファイル

**`backend/lambda/webhook/lambda_function.py`**
```python
import json
import os
import hmac
import hashlib
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, GroupSource, 
    TextSendMessage, FollowEvent, JoinEvent, LeaveEvent
)
from response_utils import create_response

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

def lambda_handler(event, context):
    """
    LINE Webhookイベントを処理
    POST /webhook
    """
    try:
        # 署名検証
        signature = event.get('headers', {}).get('x-line-signature', '')
        body = event.get('body', '')
        
        if not verify_signature(body, signature):
            return create_response(401, {'error': 'Invalid signature'})
        
        # イベント処理
        @handler.add(MessageEvent, message=TextMessage)
        def handle_message(event):
            # グループ内メッセージの場合
            if isinstance(event.source, GroupSource):
                group_id = event.source.group_id
                user_id = event.source.user_id
                text = event.message.text
                
                # スタンプ一覧などの自動応答
                if text in ['スタンプ一覧', 'スタンプ']:
                    reply_with_stamp_list(user_id, group_id)
                elif text == 'ランキング':
                    reply_with_group_ranking(group_id)
            
            # プライベートメッセージの場合
            else:
                user_id = event.source.user_id
                text = event.message.text
                handle_private_message(user_id, text)
        
        @handler.add(FollowEvent)
        def handle_follow(event):
            # 友達追加時の処理
            user_id = event.source.user_id
            welcome_message = TextSendMessage(
                text='スタンプラリーアプリへようこそ！\n「スタンプ一覧」と送信すると、あなたのスタンプを確認できます。'
            )
            line_bot_api.reply_message(event.reply_token, welcome_message)
        
        @handler.add(JoinEvent)
        def handle_join(event):
            # グループ参加時の処理
            if isinstance(event.source, GroupSource):
                group_id = event.source.group_id
                save_group(group_id)
                reply_message = TextSendMessage(
                    text='スタンプラリーアプリがグループに参加しました！\n「スタンプ」や「ランキング」と送信してみてください。'
                )
                line_bot_api.reply_message(event.reply_token, reply_message)
        
        @handler.add(LeaveEvent)
        def handle_leave(event):
            # グループ退出時の処理
            if isinstance(event.source, GroupSource):
                group_id = event.source.group_id
                delete_group(group_id)
        
        # Webhookイベントをパースして処理
        events = json.loads(body).get('events', [])
        for event_data in events:
            handler.handle(body, json.dumps(event_data))
        
        return create_response(200, {'ok': True})
        
    except InvalidSignatureError:
        return create_response(401, {'error': 'Invalid signature'})
    except Exception as e:
        print(f'Webhook error: {str(e)}')
        return create_response(500, {'error': str(e)})

def verify_signature(body, signature):
    """Webhook署名を検証"""
    hash_value = hmac.new(
        LINE_CHANNEL_SECRET.encode('utf-8'),
        body.encode('utf-8'),
        hashlib.sha256
    ).digest()
    expected_signature = base64.b64encode(hash_value).decode('utf-8')
    return hmac.compare_digest(expected_signature, signature)

def reply_with_stamp_list(user_id, group_id):
    """スタンプ一覧を返信"""
    # ユーザーのスタンプ数を取得
    stamp_count = get_user_stamp_count(user_id)
    message = TextSendMessage(
        text=f'あなたのスタンプ数: {stamp_count}個\n'
             f'スタンプ一覧を見る: {os.environ.get("LIFF_BASE_URL")}/stamps.html'
    )
    line_bot_api.push_message(user_id, message)

def reply_with_group_ranking(group_id):
    """グループ内ランキングを返信"""
    # グループメンバーのランキングを取得
    rankings = get_group_rankings(group_id)
    # ... ランキングを整形して返信 ...

def handle_private_message(user_id, text):
    """プライベートメッセージの処理"""
    if text in ['スタンプ一覧', 'スタンプ']:
        reply_with_stamp_list(user_id, None)
    elif text == 'ヘルプ':
        help_message = TextSendMessage(
            text='【使い方】\n'
                 '・「スタンプ一覧」: あなたのスタンプを確認\n'
                 '・「ランキング」: ランキングを確認（グループ内のみ）\n'
                 '・「ヘルプ」: このメッセージを表示'
        )
        line_bot_api.push_message(user_id, help_message)

def save_group(group_id):
    """グループ情報を保存"""
    # DynamoDBに保存
    pass

def delete_group(group_id):
    """グループ情報を削除"""
    # DynamoDBから削除
    pass

def get_user_stamp_count(user_id):
    """ユーザーのスタンプ数を取得"""
    # DynamoDBから取得
    pass

def get_group_rankings(group_id):
    """グループ内ランキングを取得"""
    # DynamoDBから取得
    pass
```

**`backend/lambda/webhook/requirements.txt`**
```
boto3>=1.28.0
line-bot-sdk>=3.0.0
```

#### DynamoDBテーブル

**Groupsテーブル**
- パーティションキー: GroupId
- 属性: GroupName, CreatedAt, UpdatedAt, MemberCount

**GroupMembersテーブル**
- パーティションキー: GroupId
- ソートキー: UserId
- 属性: JoinedAt, DisplayName

#### API Gateway設定
- `/webhook` (POST)
- Webhook URLをLINE Developers Consoleに設定

#### 成果物
- [ ] webhook Lambda関数実装完了
- [ ] Groups/GroupMembersテーブル作成完了
- [ ] Webhook URL設定完了
- [ ] 自動応答動作確認完了
- [ ] グループ機能動作確認完了

---

## 📅 実装スケジュール

| Phase | 機能 | 期間 | 担当 |
|-------|------|------|------|
| Phase 1 | リッチメニュー | Week 1-2 (3日) | 担当者A |
| Phase 2 | プッシュ通知 | Week 2-3 (4日) | 担当者B |
| Phase 3 | シェア・ランキング | Week 3-4 (6日) | 担当者A+B |
| Phase 4 | グループ連携 | Week 4-5 (5日) | 担当者B |

**合計期間**: 約5週間（並行作業により短縮可能）

---

## 🔧 共通実装項目

### 1. LINE Messaging API SDKセットアップ
- Docker環境でのビルド
- Lambdaレイヤーまたはパッケージ化

### 2. 環境変数設定
- `LINE_CHANNEL_ACCESS_TOKEN`: Secrets Manager ARN
- `LINE_CHANNEL_SECRET`: Secrets Manager ARN
- `LIFF_BASE_URL`: LIFFアプリのベースURL

### 3. IAM権限追加
- Lambda関数にSecrets Manager読み取り権限
- Lambda関数間の呼び出し権限（award → notify）

### 4. API Gateway設定
- 新規エンドポイント追加
- CORS設定
- リクエスト/レスポンス変換

---

## 🧪 テスト計画

### 1. リッチメニュー
- [ ] メニュー表示確認
- [ ] メニュー切り替え動作確認
- [ ] LIFF URL遷移確認

### 2. プッシュ通知
- [ ] スタンプ取得時の通知送信確認
- [ ] Flex Message表示確認
- [ ] 通知失敗時のエラーハンドリング確認

### 3. ランキング
- [ ] ランキング計算の正確性確認
- [ ] 週間/月間切り替え確認
- [ ] シェア機能動作確認

### 4. グループ連携
- [ ] Webhook受信確認
- [ ] グループ参加/退出イベント確認
- [ ] 自動応答動作確認
- [ ] グループ内ランキング確認

---

## 📝 ドキュメント更新項目

- [ ] API仕様書更新
- [ ] 環境変数設定ガイド更新
- [ ] 実装完了機能一覧更新
- [ ] 運用マニュアル作成

---

## 🚨 注意事項

### 1. LINE Messaging API制限
- プッシュ通知: 1秒あたり最大200メッセージ
- Webhook: リクエストサイズ制限あり
- レート制限の監視が必要

### 2. コスト管理
- プッシュ通知の送信量監視
- CloudWatchアラーム設定
- DynamoDB読み書き容量の監視

### 3. セキュリティ
- Channel Access Tokenの適切な管理
- Webhook署名検証の実装
- ユーザー情報の適切な取り扱い

---

**最終更新**: 2025年11月

