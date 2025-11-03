// API呼び出しラッパー

/**
 * 汎用API呼び出し関数
 * @param {string} endpoint - APIエンドポイント
 * @param {object} options - fetchオプション
 * @returns {Promise} APIレスポンス
 */
async function apiCall(endpoint, options = {}) {
    const url = CONFIG.API_BASE_URL + endpoint;
    
    // デフォルトヘッダー
    const defaultHeaders = {
        'Content-Type': 'application/json'
    };
    
    // セッショントークンがあれば追加
    const accessToken = sessionStorage.getItem(CONFIG.STORAGE_KEYS.ACCESS_TOKEN);
    if (accessToken) {
        defaultHeaders['Authorization'] = `Bearer ${accessToken}`;
    }
    
    // オプションをマージ
    const fetchOptions = {
        ...options,
        headers: {
            ...defaultHeaders,
            ...(options.headers || {})
        }
    };
    
    // bodyがある場合、JSON文字列に変換（まだ文字列でない場合のみ）
    if (fetchOptions.body && typeof fetchOptions.body !== 'string') {
        fetchOptions.body = JSON.stringify(fetchOptions.body);
    }
    
    console.log('API呼び出し:', {
        url: url,
        method: fetchOptions.method || 'GET',
        headers: fetchOptions.headers,
        body: fetchOptions.body
    });
    
    try {
        const response = await fetch(url, fetchOptions);
        
        // レスポンスボディを取得
        const contentType = response.headers.get('content-type');
        let data;
        
        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            const text = await response.text();
            // JSON文字列の可能性があるのでパースを試みる
            try {
                data = JSON.parse(text);
            } catch (e) {
                data = text;
            }
        }
        
        // API Gateway経由の場合、bodyプロパティにデータが入っている可能性
        if (data && typeof data.body === 'string') {
            try {
                data = JSON.parse(data.body);
            } catch (e) {
                console.error('bodyのパースに失敗:', e);
            }
        }
        
        // HTTPエラーステータスの場合
        if (!response.ok) {
            // API Gateway形式の場合、statusCodeプロパティで判定
            if (data && data.statusCode && data.statusCode >= 400) {
                const errorBody = data.body ? (typeof data.body === 'string' ? JSON.parse(data.body) : data.body) : data;
                const errorMessage = (errorBody && errorBody.message) ? errorBody.message : `HTTP error! status: ${data.statusCode}`;
                const error = new Error(errorMessage);
                error.status = data.statusCode;
                error.data = errorBody;
                throw error;
            } else {
                const errorMessage = (data && data.message) ? data.message : `HTTP error! status: ${response.status}`;
                const error = new Error(errorMessage);
                error.status = response.status;
                error.data = data;
                throw error;
            }
        }
        
        return data;
    } catch (error) {
        // ネットワークエラーなどの場合
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            throw new Error('ネットワークエラーが発生しました。インターネット接続を確認してください。');
        }
        throw error;
    }
}

/**
 * API呼び出しモジュール
 */
const api = {
    /**
     * LINE認証
     * @param {string} idToken - LINE IDトークン
     * @returns {Promise} 認証結果
     */
    async auth(idToken) {
        const response = await apiCall(CONFIG.API_ENDPOINTS.AUTH, {
            method: 'POST',
            body: JSON.stringify({
                id_token: idToken
            })
        });
        
        console.log('api.auth レスポンス:', response);
        
        // セッションストレージに保存
        if (response && response.ok && response.access_token) {
            sessionStorage.setItem(CONFIG.STORAGE_KEYS.ACCESS_TOKEN, response.access_token);
            if (response.user_id) {
                sessionStorage.setItem(CONFIG.STORAGE_KEYS.USER_ID, response.user_id);
            }
            if (response.display_name) {
                sessionStorage.setItem(CONFIG.STORAGE_KEYS.USER_NAME, response.display_name);
            }
        }
        
        return response;
    },
    
    /**
     * スタンプ一覧を取得
     * @param {string} userId - ユーザーID
     * @returns {Promise} スタンプ一覧
     */
    async getStamps(userId) {
        const endpoint = `${CONFIG.API_ENDPOINTS.STAMPS}?userId=${encodeURIComponent(userId)}`;
        return await apiCall(endpoint, {
            method: 'GET'
        });
    },
    
    /**
     * スタンプを授与
     * @param {string} userId - ユーザーID
     * @param {string} stampId - スタンプID
     * @param {string} method - 収集方法（GPS/IMAGE）
     * @returns {Promise} 授与結果
     */
    async awardStamp(userId, stampId, method) {
        return await apiCall(CONFIG.API_ENDPOINTS.AWARD, {
            method: 'POST',
            body: JSON.stringify({
                user_id: userId,
                stamp_id: stampId,
                method: method
            })
        });
    },
    
    /**
     * リッチメニュー一覧を取得
     * @returns {Promise} リッチメニュー一覧
     */
    async getRichMenuList() {
        return await apiCall(CONFIG.API_ENDPOINTS.RICHMENU_LIST, {
            method: 'GET'
        });
    },
    
    /**
     * ユーザーにリッチメニューを設定
     * @param {string} userId - ユーザーID
     * @param {string} richmenuId - リッチメニューID
     * @returns {Promise} 設定結果
     */
    async setRichMenu(userId, richmenuId) {
        return await apiCall(CONFIG.API_ENDPOINTS.RICHMENU_SET, {
            method: 'POST',
            body: JSON.stringify({
                user_id: userId,
                richmenu_id: richmenuId
            })
        });
    }
};

// グローバルスコープにエクスポート
window.api = api;

