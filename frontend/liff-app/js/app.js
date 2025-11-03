// LIFFアプリケーション メインファイル

// DOM要素の参照
const elements = {
    loading: document.getElementById('loading'),
    error: document.getElementById('error'),
    errorMessage: document.getElementById('errorMessage'),
    errorRetry: document.getElementById('errorRetry'),
    loginSection: document.getElementById('loginSection'),
    loginButton: document.getElementById('loginButton'),
    mainContent: document.getElementById('mainContent'),
    logoutButton: document.getElementById('logoutButton'),
    userInfo: document.getElementById('userInfo'),
    stampsContainer: document.getElementById('stampsContainer')
};

/**
 * ローディング表示を隠す
 */
function hideLoading() {
    console.log('hideLoading 呼び出し');
    if (elements.loading) {
        elements.loading.style.display = 'none';
        console.log('ローディングを非表示にしました');
    } else {
        console.error('loading要素が見つかりません');
    }
}

/**
 * エラーを表示
 * @param {string} message - エラーメッセージ
 * @param {Error} error - エラーオブジェクト（オプション）
 * @param {boolean} showRetry - 再試行ボタンを表示するか
 */
function showError(message, error = null, showRetry = false) {
    console.error('showError 呼び出し:', message, error);
    hideLoading();
    
    if (elements.error) {
        elements.error.style.display = 'block';
        if (elements.errorMessage) {
            let errorText = message;
            if (error && error.message) {
                errorText += `\n詳細: ${error.message}`;
            }
            elements.errorMessage.textContent = errorText;
        }
        if (elements.errorRetry) {
            elements.errorRetry.style.display = showRetry ? 'block' : 'none';
            if (showRetry) {
                elements.errorRetry.onclick = () => {
                    location.reload();
                };
            }
        }
    } else {
        console.error('error要素が見つかりません');
    }
    
    // 他のセクションを隠す
    if (elements.loginSection) {
        elements.loginSection.style.display = 'none';
    }
    if (elements.mainContent) {
        elements.mainContent.style.display = 'none';
    }
    
    console.error('Error:', message, error);
}

/**
 * ログインボタンを表示
 */
function showLoginButton() {
    console.log('showLoginButton 呼び出し');
    hideLoading();
    
    if (elements.loginSection) {
        elements.loginSection.style.display = 'block';
        console.log('ログインセクションを表示');
    } else {
        console.error('loginSection要素が見つかりません');
    }
    
    // ログインボタンのイベントリスナー
    if (elements.loginButton) {
        elements.loginButton.onclick = () => {
            console.log('ログインボタンクリック');
            if (typeof liff !== 'undefined') {
                liff.login();
            } else {
                showError('LIFF SDKが読み込まれていません', null, true);
            }
        };
    } else {
        console.error('loginButton要素が見つかりません');
    }
}

/**
 * ログイン済みの処理
 */
async function handleLoggedIn() {
    try {
        console.log('handleLoggedIn 開始');
        hideLoading();
        
        // IDトークンを取得
        const idToken = liff.getIDToken();
        console.log('IDトークン取得:', idToken ? '成功' : '失敗');
        
        if (!idToken) {
            throw new Error('IDトークンを取得できませんでした');
        }
        
        console.log('認証API呼び出し開始');
        console.log('IDトークン:', idToken ? idToken.substring(0, 20) + '...' : 'なし');
        // 認証APIを呼び出し
        const authResponse = await api.auth(idToken);
        console.log('認証APIレスポンス:', authResponse);
        console.log('認証APIレスポンス（詳細）:', JSON.stringify(authResponse, null, 2));
        
        // API Gateway経由の場合、レスポンス構造が異なる可能性がある
        // bodyが文字列の場合もあるので、パースを試みる
        let responseData = authResponse;
        if (typeof authResponse === 'string') {
            try {
                responseData = JSON.parse(authResponse);
            } catch (e) {
                console.error('レスポンスのパースに失敗:', e);
            }
        }
        
        // bodyプロパティが存在する場合（API Gateway形式）
        if (responseData.body && typeof responseData.body === 'string') {
            try {
                responseData = JSON.parse(responseData.body);
            } catch (e) {
                console.error('bodyのパースに失敗:', e);
            }
        }
        
        console.log('処理後のレスポンスデータ:', responseData);
        
        // エラーレスポンスの場合（statusCodeが400や500など）
        if (authResponse.statusCode && authResponse.statusCode >= 400) {
            const errorMessage = responseData.message || `APIエラー (${authResponse.statusCode})`;
            throw new Error(errorMessage);
        }
        
        if (!responseData.ok) {
            throw new Error(responseData.message || '認証に失敗しました');
        }
        
        // ユーザー情報を表示
        displayUserInfo(responseData);
        
        // スタンプ一覧を取得
        await loadStamps(responseData.user_id);
        
        // メインコンテンツを表示
        if (elements.mainContent) {
            elements.mainContent.style.display = 'block';
        }
        
        // ログアウトボタンのイベントリスナー
        if (elements.logoutButton) {
            elements.logoutButton.onclick = () => {
                if (confirm('ログアウトしますか？')) {
                    liff.logout();
                    location.reload();
                }
            };
        }
        
        console.log('handleLoggedIn 完了');
    } catch (error) {
        console.error('handleLoggedIn エラー:', error);
        showError('ログイン処理に失敗しました', error, true);
    }
}

/**
 * ユーザー情報を表示
 * @param {object} authResponse - 認証レスポンス
 */
function displayUserInfo(authResponse) {
    if (elements.userInfo) {
        const userName = authResponse.display_name || 'ユーザー';
        const userId = authResponse.user_id || '';
        elements.userInfo.textContent = `${userName}さん（${userId}）`;
    }
}

/**
 * スタンプ一覧を読み込み
 * @param {string} userId - ユーザーID
 */
async function loadStamps(userId) {
    try {
        console.log('スタンプ一覧取得開始, userId:', userId);
        const stampsResponse = await api.getStamps(userId);
        console.log('スタンプ一覧レスポンス:', stampsResponse);
        
        // API Gateway経由の場合、レスポンス構造が異なる可能性がある
        let responseData = stampsResponse;
        if (typeof stampsResponse === 'string') {
            try {
                responseData = JSON.parse(stampsResponse);
            } catch (e) {
                console.error('レスポンスのパースに失敗:', e);
            }
        }
        
        // bodyプロパティが存在する場合（API Gateway形式）
        if (responseData && typeof responseData.body === 'string') {
            try {
                responseData = JSON.parse(responseData.body);
            } catch (e) {
                console.error('bodyのパースに失敗:', e);
            }
        }
        
        console.log('処理後のスタンプレスポンスデータ:', responseData);
        
        if (responseData && responseData.ok && responseData.stamps && responseData.stamps.length > 0) {
            displayStamps(responseData.stamps);
        } else {
            displayEmptyStamps();
        }
    } catch (error) {
        console.error('スタンプ一覧の取得に失敗しました:', error);
        console.error('エラー詳細:', error.message, error);
        // エラーでもアプリは続行
        displayEmptyStamps();
    }
}

/**
 * スタンプを表示
 * @param {Array} stamps - スタンプ配列
 */
function displayStamps(stamps) {
    if (!elements.stampsContainer) {
        return;
    }
    
    elements.stampsContainer.innerHTML = '';
    
    stamps.forEach(stamp => {
        const stampElement = document.createElement('div');
        stampElement.className = 'stamp-item';
        stampElement.innerHTML = `
            <h3>${stamp.name || stamp.stamp_id}</h3>
            <p>${stamp.description || ''}</p>
            <small>取得日時: ${formatDate(stamp.collected_at)}</small>
        `;
        elements.stampsContainer.appendChild(stampElement);
    });
}

/**
 * スタンプが空の場合の表示
 */
function displayEmptyStamps() {
    if (elements.stampsContainer) {
        elements.stampsContainer.innerHTML = '<p class="empty-message">スタンプがありません</p>';
    }
}

/**
 * Unixタイムスタンプを日付文字列に変換
 * @param {number} timestamp - Unixタイムスタンプ
 * @returns {string} 日付文字列
 */
function formatDate(timestamp) {
    if (!timestamp) {
        return '不明';
    }
    const date = new Date(timestamp * 1000);
    return date.toLocaleString('ja-JP');
}

/**
 * LIFF SDKの読み込みを待つ
 * @param {number} retries - リトライ回数
 * @param {number} delay - 待機時間（ミリ秒）
 */
function waitForLIFFSDK(retries = 20, delay = 100) {
    return new Promise((resolve, reject) => {
        let attempts = 0;
        
        const checkSDK = () => {
            attempts++;
            
            if (typeof liff !== 'undefined') {
                console.log('LIFF SDK読み込み確認: 成功');
                resolve();
            } else if (attempts >= retries) {
                console.error('LIFF SDK読み込み確認: タイムアウト');
                reject(new Error('LIFF SDKの読み込みがタイムアウトしました'));
            } else {
                console.log(`LIFF SDK読み込み確認: 待機中 (${attempts}/${retries})`);
                setTimeout(checkSDK, delay);
            }
        };
        
        checkSDK();
    });
}

/**
 * LIFF初期化処理
 */
async function initializeLIFF() {
    try {
        // LIFF SDKの読み込みを待つ
        await waitForLIFFSDK();
        
        // CONFIGが読み込まれているか確認
        if (typeof CONFIG === 'undefined') {
            console.error('CONFIGが定義されていません');
            showError('設定ファイルが読み込まれていません', null, true);
            return;
        }
        
        console.log('LIFF初期化を開始...', CONFIG.LIFF_ID);
        
        liff.init({ liffId: CONFIG.LIFF_ID })
            .then(() => {
                console.log('LIFF初期化成功');
                console.log('ログイン状態:', liff.isLoggedIn());
                
                // 初期化成功
                if (!liff.isLoggedIn()) {
                    // ログインしていない場合
                    console.log('未ログイン - ログインボタンを表示');
                    showLoginButton();
                } else {
                    // ログイン済みの場合
                    console.log('ログイン済み - 認証処理を開始');
                    handleLoggedIn();
                }
            })
            .catch((err) => {
                // 初期化エラー
                console.error('LIFF初期化エラー:', err);
                showError('LIFF初期化に失敗しました: ' + (err.message || err), err, true);
            });
            
    } catch (error) {
        console.error('LIFF SDK読み込みエラー:', error);
        showError('LIFF SDKが読み込まれていません。LINEアプリからアクセスしてください。', error, true);
    }
}

// DOMContentLoadedイベントで初期化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('DOMContentLoaded - LIFF初期化を開始');
        initializeLIFF();
    });
} else {
    // DOMが既に読み込まれている場合
    console.log('DOM already loaded - LIFF初期化を開始');
    initializeLIFF();
}
