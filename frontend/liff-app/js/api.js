// API呼び出しラッパー

/**
 * 汎用API呼び出し関数
 * @param {string} endpoint - APIエンドポイント
 * @param {object} options - fetchオプション
 * @returns {Promise} APIレスポンス
 */
async function apiCall(endpoint, options = {}) {
    // CONFIGの確認
    if (typeof CONFIG === 'undefined' || !CONFIG || !CONFIG.API_BASE_URL) {
        throw new Error('CONFIGが読み込まれていません。config.jsが正しく読み込まれているか確認してください。');
    }
    
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
        const responseText = await response.text();
        
        // JSONレスポンスのパース
        if (contentType && contentType.includes('application/json')) {
            try {
                data = JSON.parse(responseText);
            } catch (e) {
                console.error('JSONパースエラー:', e);
                throw new Error(`レスポンスのパースに失敗しました: ${e.message}`);
            }
        } else if (responseText.trim().length > 0) {
            // JSONではないが、テキストが存在する場合、JSONとしてパースを試みる
            try {
                data = JSON.parse(responseText);
            } catch (e) {
                // JSONでない場合はテキストのまま
                data = { message: responseText };
            }
        } else {
            // レスポンスボディが空の場合
            data = {};
        }
        
        // API Gateway経由の場合、bodyプロパティにデータが入っている可能性がある
        if (data && typeof data.body === 'string') {
            try {
                const parsedBody = JSON.parse(data.body);
                // bodyの中身を展開
                data = { ...data, ...parsedBody };
                delete data.body;
            } catch (e) {
                console.warn('bodyプロパティのパースに失敗:', e);
            }
        }
        
        // HTTPエラーステータスの処理
        if (!response.ok) {
            let errorMessage = `HTTP error! status: ${response.status}`;
            let errorData = data;
            
            // エラーメッセージの抽出
            if (data) {
                if (data.message) {
                    errorMessage = data.message;
                } else if (data.error && data.message) {
                    errorMessage = data.message;
                } else if (typeof data === 'string') {
                    errorMessage = data;
                }
                
                // API Gateway形式の場合
                if (data.statusCode && data.statusCode >= 400) {
                    const errorBody = (data.body && typeof data.body === 'string') 
                        ? JSON.parse(data.body) 
                        : (data.body || data);
                    
                    errorMessage = errorBody.message || errorMessage;
                    errorData = errorBody;
                }
            }
            
            const error = new Error(errorMessage);
            error.status = data?.statusCode || response.status;
            error.data = errorData;
            throw error;
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
let api;
try {
    api = {
        /**
         * LINE認証
         * @param {string} idToken - LINE IDトークン
         * @returns {Promise<Object>} 認証結果
         * @throws {Error} 認証に失敗した場合
         */
        async auth(idToken) {
            if (!idToken || typeof idToken !== 'string' || idToken.trim().length === 0) {
                throw new Error('IDトークンが無効です');
            }
            
            console.log('認証API呼び出し:', CONFIG.API_ENDPOINTS.AUTH);
            
            try {
                const response = await apiCall(CONFIG.API_ENDPOINTS.AUTH, {
                    method: 'POST',
                    body: JSON.stringify({
                        id_token: idToken.trim()
                    })
                });
                
                console.log('認証APIレスポンス受信:', {
                    ok: response?.ok,
                    user_id: response?.user_id,
                    has_access_token: !!response?.access_token
                });
                
                // 認証成功時、セッションストレージに保存
                if (response && response.ok && response.access_token) {
                    sessionStorage.setItem(CONFIG.STORAGE_KEYS.ACCESS_TOKEN, response.access_token);
                    
                    if (response.user_id) {
                        sessionStorage.setItem(CONFIG.STORAGE_KEYS.USER_ID, response.user_id);
                    }
                    
                    if (response.display_name) {
                        sessionStorage.setItem(CONFIG.STORAGE_KEYS.USER_NAME, response.display_name);
                    }
                    
                    console.log('セッションストレージに認証情報を保存しました');
                } else {
                    // 認証失敗
                    const errorMessage = response?.message || '認証に失敗しました';
                    throw new Error(errorMessage);
                }
                
                return response;
            } catch (error) {
                console.error('認証API呼び出しエラー:', error);
                
                // セッションストレージをクリア（認証失敗時）
                Object.values(CONFIG.STORAGE_KEYS).forEach(key => {
                    sessionStorage.removeItem(key);
                });
                
                throw error;
            }
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
         * GPS位置情報を検証
         * @param {string} userId - ユーザーID
         * @param {string} spotId - スポットID（スタンプID）
         * @param {number} lat - 緯度
         * @param {number} lon - 経度
         * @param {number} accuracy - 精度（メートル、オプション）
         * @returns {Promise} GPS検証結果
         */
        async verifyGPS(userId, spotId, lat, lon, accuracy = null) {
            const body = {
                userId: userId,
                spotId: spotId,
                lat: lat,
                lon: lon
            };
            
            // accuracyが指定されている場合は追加
            if (accuracy !== null && accuracy !== undefined) {
                body.accuracy = accuracy;
            }
            
            return await apiCall(CONFIG.API_ENDPOINTS.GPS_VERIFY, {
                method: 'POST',
                body: JSON.stringify(body)
            });
        },
        
        /**
         * ランキングを取得
         * @param {string} endpoint - ランキングエンドポイント（/ranking/weekly または /ranking/monthly）
         * @param {string} period - 期間（オプション）
         * @returns {Promise} ランキングデータ
         */
        async getRankings(endpoint, period = null) {
            let url = endpoint;
            if (period) {
                url += `?period=${encodeURIComponent(period)}`;
            }
            return await apiCall(url, {
                method: 'GET'
            });
        },
        
        /**
         * ユーザー比較
         * @param {string} userId - ユーザーID
         * @param {string} friendId - 友達のユーザーID
         * @returns {Promise} 比較結果
         */
        async compareUsers(userId, friendId) {
            const endpoint = `/ranking/compare?user_id=${encodeURIComponent(userId)}&friend_id=${encodeURIComponent(friendId)}`;
            return await apiCall(endpoint, {
                method: 'GET'
            });
        },
        
        /**
         * 友達関係を追加
         * @param {string} userId - ユーザーID
         * @param {string} friendId - 友達のユーザーID
         * @returns {Promise} 追加結果
         */
        async addFriend(userId, friendId) {
            return await apiCall('/friends/add', {
                method: 'POST',
                body: JSON.stringify({
                    user_id: userId,
                    friend_id: friendId
                })
            });
        },
        
        /**
         * 友達リストを取得
         * @param {string} userId - ユーザーID
         * @returns {Promise} 友達リスト
         */
        async getFriends(userId) {
            const endpoint = `/friends/list?user_id=${encodeURIComponent(userId)}`;
            return await apiCall(endpoint, {
                method: 'GET'
            });
        }
    };
    
    // グローバルスコープにエクスポート
    window.api = api;
    console.log('✅ apiオブジェクトをwindowにエクスポートしました');
    console.log('api.getRankings:', typeof api.getRankings === 'function' ? '利用可能' : '未定義');
} catch (error) {
    console.error('❌ apiオブジェクトの作成に失敗:', error);
    // エラーが発生しても、空のapiオブジェクトを作成してエクスポート
    window.api = {
        getRankings: function() {
            return Promise.reject(new Error('apiオブジェクトの初期化に失敗しました'));
        }
    };
}

