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
        // 既存のイベントリスナーを削除
        elements.loginButton.onclick = null;
        elements.loginButton.addEventListener('click', () => {
            console.log('ログインボタンクリック');
            
            if (typeof liff === 'undefined') {
                showError('LIFF SDKが読み込まれていません', null, true);
                return;
            }
            
            // ローディングを表示
            if (elements.loading) {
                elements.loading.style.display = 'block';
            }
            
            console.log('LINEログインを開始...');
            try {
                // LINEログインを実行（この呼び出しでリダイレクトが発生する）
                liff.login();
                // 注意: liff.login()の後は実行されない（リダイレクトされるため）
            } catch (error) {
                console.error('LINEログインエラー:', error);
                hideLoading();
                showError('ログインに失敗しました: ' + (error.message || error), error, true);
            }
        });
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
        
        // LIFF SDKが初期化されているか確認
        if (typeof liff === 'undefined') {
            throw new Error('LIFF SDKが初期化されていません');
        }
        
        // ログイン状態の確認
        if (!liff.isLoggedIn()) {
            console.log('ログインしていないため、ログインボタンを表示');
            showLoginButton();
            return;
        }
        
        // ローディングを表示（認証処理中）
        if (elements.loading) {
            elements.loading.style.display = 'block';
        }
        
        // ログインセクションを非表示
        if (elements.loginSection) {
            elements.loginSection.style.display = 'none';
        }
        
        // エラー表示を非表示
        if (elements.error) {
            elements.error.style.display = 'none';
        }
        
        // IDトークンを取得
        const idToken = liff.getIDToken();
        if (!idToken) {
            throw new Error('IDトークンを取得できませんでした。LINEアプリ内からアクセスしてください。');
        }
        
        console.log('IDトークン取得成功');
        console.log('認証API呼び出し開始');
        
        // 認証APIを呼び出し
        const responseData = await api.auth(idToken);
        
        // レスポンスの検証
        if (!responseData || !responseData.ok) {
            const errorMessage = responseData?.message || '認証に失敗しました';
            throw new Error(errorMessage);
        }
        
        // 必須フィールドの確認
        if (!responseData.user_id || !responseData.access_token) {
            throw new Error('認証レスポンスに必須フィールドが含まれていません');
        }
        
        console.log('認証成功:', {
            user_id: responseData.user_id,
            display_name: responseData.display_name
        });
        
        // ローディングを非表示
        hideLoading();
        
        // ユーザー情報を表示
        displayUserInfo(responseData);
        
        // スタンプ一覧を取得
        try {
            await loadStamps(responseData.user_id);
        } catch (stampError) {
            console.warn('スタンプ一覧の取得に失敗しましたが、処理を継続します:', stampError);
            // スタンプ取得の失敗は致命的ではないので、エラー表示せず継続
        }
        
        // メインコンテンツを表示
        if (elements.mainContent) {
            elements.mainContent.style.display = 'block';
        }
        
        // ログアウトボタンのイベントリスナーを設定
        if (elements.logoutButton) {
            // 既存のイベントリスナーを削除
            elements.logoutButton.onclick = null;
            elements.logoutButton.addEventListener('click', () => {
                if (confirm('ログアウトしますか？')) {
                    // セッションストレージをクリア
                    Object.values(CONFIG.STORAGE_KEYS).forEach(key => {
                        sessionStorage.removeItem(key);
                    });
                    
                    // LIFFログアウト
                    liff.logout();
                    
                    // ページをリロード
                    location.reload();
                }
            });
        }
        
        console.log('handleLoggedIn 完了');
    } catch (error) {
        console.error('handleLoggedIn エラー:', error);
        const errorMessage = error.message || 'ログイン処理に失敗しました';
        showError(errorMessage, error, true);
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
    if (!userId) {
        console.warn('ユーザーIDが指定されていません');
        displayEmptyStamps();
        return;
    }
    
    try {
        console.log('スタンプ一覧取得開始, userId:', userId);
        const responseData = await api.getStamps(userId);
        
        console.log('スタンプ一覧レスポンス受信:', {
            ok: responseData?.ok,
            stamps_count: responseData?.stamps?.length || 0
        });
        
        // レスポンスの検証と処理
        if (responseData && responseData.ok && Array.isArray(responseData.stamps)) {
            if (responseData.stamps.length > 0) {
                displayStamps(responseData.stamps);
            } else {
                displayEmptyStamps();
            }
        } else {
            console.warn('スタンプ一覧の形式が不正です:', responseData);
            displayEmptyStamps();
        }
    } catch (error) {
        console.error('スタンプ一覧の取得に失敗しました:', error);
        // エラーでもアプリは続行（スタンプがない状態で表示）
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
    
    const stampImages = {
        "BLD14-RM213": "assets/images/stamps/bld14213.png",
        "YIL-001": "assets/images/stamps/yil.png",
        "STATUE-001": "assets/images/stamps/statue.png",
        "test": "assets/images/stamps/test.png"
    };

    // 取得済みスタンプIDを配列に
    const obtainedIds = stamps.map(s => s.stamp_id);

    Object.entries(stampImages).forEach(([stampId, imgSrc]) => {
        const stampElement = document.createElement('div');
        stampElement.className = 'stamp-item';

        // スタンプ画像を表示
        const img = document.createElement('img');
        img.src = imgSrc;
        img.alt = stampId;
        img.classList.add('stamp'); // script.jsと同じclassにすると統一される
        const obtainedStamp = stamps.find(s => s.stamp_id === stampId);
        if (obtainedStamp) {
            // 取得済み
            img.classList.add('obtained');
            img.addEventListener('click', (e) => {
                showStampInfo(e.currentTarget, obtainedStamp);
            });
        } else {
            // 未取得 → 半透明に
            img.classList.add('not-obtained');
        }
        stampElement.appendChild(img);

        elements.stampsContainer.appendChild(stampElement);
    });

    // バックエンドから取得したデータを使って進捗更新
    updateProgress(stamps);
}

function showStampInfo(targetImg, stamp) {
    // 既存の吹き出しがあれば削除
    const existing = targetImg.parentElement.querySelector('.stamp-info');
    if (existing) existing.remove();

    // 吹き出し要素を作成
    const infoBox = document.createElement('div');
    infoBox.className = 'stamp-info';
    infoBox.innerHTML = `
        <strong>${stamp.name || stamp.stamp_id}</strong><br>
        <small>${formatDate(stamp.collected_at)}</small>
    `;

    // 親要素に追加（画像の上に表示）
    targetImg.parentElement.style.position = 'relative';
    targetImg.parentElement.appendChild(infoBox);

    // 3秒後に自動でフェードアウトして削除
    setTimeout(() => {
        infoBox.classList.add('fade-out');
        setTimeout(() => infoBox.remove(), 400); // フェード終了後に削除
    }, 2000); // 2秒表示
}

/**
 * スタンプが空の場合の表示
 */
function displayEmptyStamps() {
    if (elements.stampsContainer) {
        elements.stampsContainer.innerHTML = '<p class="empty-message">スタンプがありません</p>';
    }
    // 空の場合も進捗リセット
    updateProgress([]);
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
 * スタンプ進捗を更新
 * @param {Array} stamps - 取得済みスタンプ配列
 */
function updateProgress(stamps = []) {
    const totalSpots = Object.keys(stampImages).length; // 全スポット数
    const obtained = stamps.length;
    const ratio = totalSpots > 0 ? obtained / totalSpots : 0;
    const percent = Math.round(ratio * 100);

    const textEl = document.getElementById('progressText');
    const fillEl = document.getElementById('progressFill');

    if (textEl) textEl.textContent = `${percent}%（${obtained}/${totalSpots}）`;
    if (fillEl) fillEl.style.width = `${percent}%`;
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
        
        // LIFF初期化の前にローディングを表示
        if (elements.loading) {
            elements.loading.style.display = 'block';
        }
        
        liff.init({ liffId: CONFIG.LIFF_ID })
            .then(() => {
                console.log('LIFF初期化成功');
                console.log('ログイン状態:', liff.isLoggedIn());
                console.log('LINEアプリ内:', liff.isInClient());
                
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
                hideLoading();
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
