// API設定
const CONFIG = {
    // API Gatewayエンドポイント
    API_BASE_URL: 'https://2bm71jvfs6.execute-api.us-east-1.amazonaws.com/dev',
    
    // LIFF ID（環境に応じて変更）
    // LINE Developersコンソールで取得
    LIFF_ID: window.LIFF_ID || '2008407212-wpMNWMbB',
    
    // セッションストレージのキー
    STORAGE_KEYS: {
        ACCESS_TOKEN: 'stamp_rally_access_token',
        USER_ID: 'stamp_rally_user_id',
        USER_NAME: 'stamp_rally_user_name'
    },
    
    // API エンドポイント
    API_ENDPOINTS: {
        AUTH: '/auth/verify',
        STAMPS: '/stamps',
        AWARD: '/stamps/award'
    }
};

// エクスポート（グローバルスコープ）
window.CONFIG = CONFIG;
