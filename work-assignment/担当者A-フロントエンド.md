# 担当者A - フロントエンド・LIFF開発

## 担当範囲
- LIFFアプリケーション全体のUI/UX実装
- 画面遷移とインタラクション設計
- フロントエンドとバックエンドAPI連携
- ブラウザ互換性対応

## 作業内容

### Phase 1: 環境構築・準備（Week 1-2）
- [ ] LIFF開発環境のセットアップ
- [ ] LINE Developersコンソールでのチャネル設定
- [ ] GitHubリポジトリのクローン
- [ ] 必要なツールのインストール

### Phase 2: 基本機能実装（Week 3-4）
- [ ] LIFFアプリの基本構造作成
- [ ] LINEログイン機能（担当者Bと連携）
- [ ] ナビゲーション設計
- [ ] レスポンシブデザイン適用

### Phase 3: 画面実装（Week 5-6）
- [ ] **ホーム・ダッシュボード画面**
  - スタンプ収集状況の一覧表示
  - 進捗バーの実装
  - 統計情報の表示
  
- [ ] **GPSスタンプ画面**
  - 現在地取得ボタン
  - 目標地点までの距離表示
  - 到達判定UI
  - 地図表示（任意）
  
- [ ] **カメラスタンプ画面**
  - カメラ起動・撮影機能
  - プレビュー画面
  - アップロード進行状況表示
  - リトライ機能

- [ ] **スタンプ詳細画面**
  - 各スタンプの詳細情報表示
  - 獲得日時の表示
  - スタンプ画像の表示

### Phase 4: API連携（Week 5-6）
- [ ] Fetch API実装
- [ ] エラーハンドリング実装
- [ ] ローディング状態の管理
- [ ] リトライロジック実装

### Phase 5: テスト・調整（Week 7）
- [ ] 各画面のユニットテスト
- [ ] ブラウザ互換性テスト
- [ ] UI/UX改善
- [ ] パフォーマンス最適化

## 使用技術
- LIFF SDK 2.x
- HTML5/CSS3/JavaScript (ES6+)
- Fetch API
- Geolocation API
- MediaDevices.getUserMedia()
- CSS Framework（任意）

## 担当ファイル
```
frontend/liff-app/
├── index.html
├── login.html
├── home.html
├── gps-stamp.html
├── camera-stamp.html
├── stamp-detail.html
├── css/
│   ├── style.css
│   └── responsive.css
├── js/
│   ├── app.js
│   ├── api.js
│   ├── gps.js
│   ├── camera.js
│   └── utils.js
└── assets/
    ├── images/
    └── icons/
```

## 連携先
- **担当者B**: 認証トークンの受け取り、API仕様の確認
- **担当者C**: LIFF URLの確認、デプロイ環境の確認
- **担当者D**: 画像アップロード形式の確認

## 成果物
- LIFFアプリのソースコード
- UI/UXデザインモックアップ
- ブラウザ互換性チェックシート
- 画面遷移図

## 注意事項
- LINE内ブラウザでの動作確認必須
- GPS機能はHTTPS必須
- カメラ機能はユーザー許可必須
- セキュリティ: APIトークンはメモリにのみ保持


