// ランキング画面のロジック

// グローバル変数
let elements;
let currentPeriod = 'weekly';
let currentRankings = [];
let currentType = 'friends'; // 'friends' only

// すべてのスクリプトが読み込まれるまで待つ
function waitForScripts() {
    return new Promise((resolve, reject) => {
        // CONFIGとapiの両方が必要
        const checkScripts = () => {
            const configReady = typeof CONFIG !== 'undefined' && CONFIG && CONFIG.API_BASE_URL;
            const apiReady = window.api && typeof window.api === 'object' && typeof window.api.getRankings === 'function';
            
            if (configReady && apiReady) {
                console.log('✅ すべてのスクリプトが読み込まれました');
                console.log('CONFIG.API_BASE_URL:', CONFIG.API_BASE_URL);
                console.log('api.getRankings:', typeof window.api.getRankings);
                resolve();
                return true;
            }
            return false;
        };

        // 即座にチェック（スクリプトが既に読み込まれている場合）
        if (checkScripts()) {
            return;
        }

        // 定期的にチェック（10ms間隔、より頻繁にチェック）
        let checkCount = 0;
        const maxChecks = 500; // 5秒（10ms × 500）
        const checkInterval = setInterval(() => {
            checkCount++;
            
            if (checkScripts()) {
                clearInterval(checkInterval);
                return;
            }

            // デバッグログ（50回ごと = 0.5秒ごと）
            if (checkCount % 50 === 0) {
                console.log(`⏳ スクリプト読み込み待機中... (${(checkCount * 10) / 1000}秒)`);
                console.log('  CONFIG:', typeof CONFIG !== 'undefined' && CONFIG ? '✅ 読み込み済み' : '❌ 未読み込み');
                console.log('  CONFIG.API_BASE_URL:', typeof CONFIG !== 'undefined' && CONFIG ? (CONFIG.API_BASE_URL || '未設定') : 'N/A');
                console.log('  window.api:', window.api ? '✅ 読み込み済み' : '❌ 未読み込み');
                if (window.api) {
                    console.log('  api.getRankings:', typeof window.api.getRankings === 'function' ? '✅ 利用可能' : '❌ 未定義');
                    console.log('  apiオブジェクトのキー:', Object.keys(window.api));
                }
            }

            // タイムアウト
            if (checkCount >= maxChecks) {
                clearInterval(checkInterval);
                console.error('❌ スクリプト読み込みタイムアウト（5秒）');
                console.error('CONFIG状態:', typeof CONFIG);
                if (typeof CONFIG !== 'undefined') {
                    console.error('CONFIG内容:', CONFIG);
                }
                console.error('window.api状態:', typeof window.api);
                if (window.api) {
                    console.error('apiオブジェクトのキー:', Object.keys(window.api));
                    console.error('api.getRankings:', typeof window.api.getRankings);
                }
                
                // エラーとして扱う
                reject(new Error('スクリプトの読み込みに失敗しました'));
            }
        }, 10); // 10ms間隔でチェック（より頻繁に）
    });
}

// DOM読み込み完了後に初期化
function initializeRanking() {
    elements = {
        rankingsContainer: document.getElementById('rankingsContainer'),
        shareButton: document.getElementById('shareButton'),
        inviteButton: document.getElementById('inviteButton'),
        tabs: document.querySelectorAll('.tab')
    };

    // スクリプトの読み込みを待つ
    waitForScripts()
        .then(() => {
            // 再度確認（念のため）
            if (typeof CONFIG === 'undefined' || !CONFIG || !CONFIG.API_BASE_URL) {
                throw new Error('CONFIGが読み込まれていません');
            }

            if (!window.api || typeof window.api !== 'object' || typeof window.api.getRankings !== 'function') {
                throw new Error('api.getRankings is not available');
            }

            console.log('✅ APIモジュール読み込み確認完了');
            initializeAfterScriptsLoaded();
        })
        .catch((error) => {
            console.error('❌ スクリプト読み込みエラー:', error);
            showError(`スクリプトの読み込みに失敗しました: ${error.message}\n\nページを再読み込みしてください。`);
        });
}

// スクリプト読み込み後の初期化処理
function initializeAfterScriptsLoaded() {

    // タブ切り替えのイベントリスナーを設定
    elements.tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            elements.tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentType = tab.dataset.type || 'friends'; // デフォルトを'friends'に変更
            currentPeriod = tab.dataset.period || 'weekly';
            loadRankings(currentPeriod, currentType);
        });
    });

    // 友達招待ボタンのイベントリスナー
    if (elements.inviteButton) {
        elements.inviteButton.addEventListener('click', async () => {
            await inviteFriend();
        });
    }

    // LIFF初期化
    liff.init({ liffId: CONFIG.LIFF_ID })
        .then(() => {
            console.log('✅ LIFF初期化成功');
            console.log('LINEアプリ内:', liff.isInClient());
            console.log('shareTargetPicker利用可能:', liff.isApiAvailable('shareTargetPicker'));
            
            // シェアボタンの有効/無効を設定
            setupShareButton();
            
                if (liff.isLoggedIn()) {
                    loadRankings(currentPeriod, currentType);
                } else {
                    // 未ログインの場合はログイン画面にリダイレクト
                    liff.login();
                }
        })
        .catch(error => {
            console.error('❌ LIFF初期化エラー:', error);
            showError('アプリの初期化に失敗しました。ページを再読み込みしてください。');
        });
}

// すべてのリソース（スクリプトを含む）が読み込まれるまで待つ
function startInitialization() {
    // window.onloadが既に発火している場合
    if (document.readyState === 'complete') {
        console.log('ページ読み込み完了 - 初期化を開始');
        initializeRanking();
    } else {
        // window.onloadを待つ（すべてのスクリプトが読み込まれた後）
        window.addEventListener('load', () => {
            console.log('window.onload発火 - 初期化を開始');
            initializeRanking();
        });
    }
}

// 初期化を開始
startInitialization();

// シェアボタンの設定
function setupShareButton() {
    if (!elements || !elements.shareButton) {
        console.error('Share button element not found');
        return;
    }

    // 既存のイベントリスナーを削除（重複防止）
    const newButton = elements.shareButton.cloneNode(true);
    elements.shareButton.parentNode.replaceChild(newButton, elements.shareButton);
    elements.shareButton = newButton;

    // シェア機能の実装
    elements.shareButton.addEventListener('click', async () => {
        await handleShare();
    });
}

// シェア処理
async function handleShare() {
    try {
        // LIFF SDKの確認
        if (typeof liff === 'undefined') {
            console.error('LIFF SDK is not loaded');
            fallbackShare();
            return;
        }

        // LINEアプリ内かどうかを確認
        const isInClient = liff.isInClient();
        console.log('LINEアプリ内:', isInClient);

        // shareTargetPickerが利用可能か確認
        const isShareAvailable = liff.isApiAvailable('shareTargetPicker');
        console.log('shareTargetPicker利用可能:', isShareAvailable);

        if (isShareAvailable) {
            // shareTargetPickerを使用
            const shareUrl = `${window.location.origin}/ranking.html`;
            let shareText;
            
            if (currentRankings.length > 0) {
                const periodText = currentPeriod === 'weekly' ? '週間' : '月間';
                const topUser = currentRankings[0];
                shareText = `🏆 スタンプラリーランキング（${periodText}）\n\n` +
                           `1位: ${topUser.display_name || 'Unknown'} (${topUser.stamp_count || 0}個)\n\n` +
                           `あなたもスタンプを集めてランキングに参加しよう！\n\n` +
                           `${shareUrl}`;
            } else {
                shareText = `🏆 スタンプラリーランキングを見てみて！\n\n` +
                           `スタンプを集めてランキングに参加しよう！\n\n` +
                           `${shareUrl}`;
            }

            console.log('シェアテキスト:', shareText);

            try {
                const result = await liff.shareTargetPicker([
                    {
                        type: 'text',
                        text: shareText
                    }
                ]);
                console.log('シェア成功:', result);
                
                // 成功メッセージ（オプション）
                if (result && result.status === 'success') {
                    // シェア成功時の処理（必要に応じて）
                }
            } catch (shareError) {
                console.error('shareTargetPickerエラー:', shareError);
                
                // エラーの種類に応じて処理
                if (shareError.code === 'CANCEL') {
                    // ユーザーがキャンセルした場合
                    console.log('シェアがキャンセルされました');
                } else {
                    // その他のエラー
                    console.error('シェアエラー詳細:', shareError);
                    alert(`シェアに失敗しました: ${shareError.message || '不明なエラー'}`);
                    // フォールバックに切り替え
                    fallbackShare();
                }
            }
        } else {
            // shareTargetPickerが利用できない場合
            console.log('shareTargetPickerが利用できません。フォールバックを使用します。');
            fallbackShare();
        }
    } catch (error) {
        console.error('シェア処理エラー:', error);
        alert(`シェアに失敗しました: ${error.message || '不明なエラー'}`);
        fallbackShare();
    }
}

// フォールバックシェア（URLコピー）
async function fallbackShare(customUrl = null) {
    const shareUrl = customUrl || `${window.location.origin}/ranking.html`;
    
    try {
        // クリップボードAPIを試す
        if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(shareUrl);
            alert('ランキングのURLをクリップボードにコピーしました！\n\n' + shareUrl);
        } else {
            // クリップボードAPIが使えない場合
            const textArea = document.createElement('textarea');
            textArea.value = shareUrl;
            textArea.style.position = 'fixed';
            textArea.style.opacity = '0';
            document.body.appendChild(textArea);
            textArea.select();
            
            try {
                document.execCommand('copy');
                document.body.removeChild(textArea);
                alert('ランキングのURLをクリップボードにコピーしました！\n\n' + shareUrl);
            } catch (e) {
                document.body.removeChild(textArea);
                // 最終手段: promptで表示
                prompt('以下のURLをコピーしてください:', shareUrl);
            }
        }
    } catch (e) {
        console.error('クリップボードコピーエラー:', e);
        prompt('以下のURLをコピーしてください:', shareUrl);
    }
}

// ランキング読み込み
async function loadRankings(period, type = 'friends') {
    try {
        if (!elements || !elements.rankingsContainer) {
            console.error('Elements not initialized');
            return;
        }

        elements.rankingsContainer.innerHTML = `
            <div class="loading">
                <div class="loading-spinner"></div>
                <p>読み込み中...</p>
            </div>
        `;
        
        // すべてのランキングは友達ランキングを使用
        const userId = sessionStorage.getItem(CONFIG.STORAGE_KEYS.USER_ID);
        if (!userId) {
            throw new Error('ログインが必要です');
        }
        
        const endpoint = period === 'weekly' 
            ? `/ranking/friends/weekly?user_id=${encodeURIComponent(userId)}` 
            : `/ranking/friends/monthly?user_id=${encodeURIComponent(userId)}`;
        
        // apiオブジェクトの存在確認
        if (!window.api || typeof window.api.getRankings !== 'function') {
            throw new Error('APIモジュールが読み込まれていません');
        }
        
        const response = await window.api.getRankings(endpoint);
        
        // デバッグログ
        console.log('📊 ランキングAPIレスポンス:', response);
        console.log('📊 response.ok:', response.ok);
        console.log('📊 response.rankings:', response.rankings);
        console.log('📊 rankings.length:', response.rankings ? response.rankings.length : 0);
        
        if (response.ok && response.rankings) {
            currentRankings = response.rankings;
            console.log('✅ ランキングデータを取得しました。件数:', response.rankings.length);
            displayRankings(response.rankings);
        } else {
            console.error('❌ ランキング取得失敗:', response);
            throw new Error(response.message || 'ランキングの取得に失敗しました');
        }
    } catch (error) {
        console.error('ランキング取得失敗:', error);
        showError(error.message || 'ランキングの取得に失敗しました');
    }
}

// 友達を招待する機能
async function inviteFriend() {
    try {
        const userId = sessionStorage.getItem(CONFIG.STORAGE_KEYS.USER_ID);
        if (!userId) {
            alert('ログインが必要です。');
            // ログインを促す
            if (typeof liff !== 'undefined' && liff.isLoggedIn()) {
                // 既にログインしている場合は、認証情報を再取得
                const idToken = liff.getIDToken();
                if (idToken) {
                    try {
                        await window.api.auth(idToken);
                        // 再試行
                        const newUserId = sessionStorage.getItem(CONFIG.STORAGE_KEYS.USER_ID);
                        if (newUserId) {
                            await inviteFriendWithUserId(newUserId);
                        }
                    } catch (error) {
                        console.error('認証エラー:', error);
                        alert('認証に失敗しました。ページを再読み込みしてください。');
                    }
                }
            } else if (typeof liff !== 'undefined') {
                liff.login();
            } else {
                alert('ログインが必要です。LINEアプリからアクセスしてください。');
            }
            return;
        }

        await inviteFriendWithUserId(userId);
    } catch (error) {
        console.error('友達招待エラー:', error);
        alert('友達招待に失敗しました。');
    }
}

// ユーザーIDを使って友達を招待
async function inviteFriendWithUserId(userId) {
    try {
        // 招待リンクを生成
        const inviteUrl = `${window.location.origin}/index.html?invite=${encodeURIComponent(userId)}`;
        
        // 招待URLをクリップボードにコピー
        await copyToClipboard(inviteUrl);
        
        // 成功メッセージを表示
        alert('✅ 招待リンクをクリップボードにコピーしました！\n\n' + 
              '友達にシェアしてください。\n\n' + 
              inviteUrl);
        
        console.log('招待リンクをコピーしました:', inviteUrl);
    } catch (error) {
        console.error('友達招待エラー:', error);
        alert('招待リンクのコピーに失敗しました。\n\n' + 
              '以下のURLを手動でコピーしてください:\n\n' + 
              `${window.location.origin}/index.html?invite=${encodeURIComponent(userId)}`);
    }
}

// クリップボードにコピーする関数
async function copyToClipboard(text) {
    try {
        // クリップボードAPIを試す（モダンブラウザ）
        if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(text);
            return;
        }
        
        // フォールバック: 古いブラウザ用
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.top = '0';
        textArea.style.left = '0';
        textArea.style.width = '2em';
        textArea.style.height = '2em';
        textArea.style.padding = '0';
        textArea.style.border = 'none';
        textArea.style.outline = 'none';
        textArea.style.boxShadow = 'none';
        textArea.style.background = 'transparent';
        textArea.style.opacity = '0';
        
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            const successful = document.execCommand('copy');
            document.body.removeChild(textArea);
            
            if (!successful) {
                throw new Error('execCommand failed');
            }
        } catch (e) {
            document.body.removeChild(textArea);
            throw e;
        }
    } catch (error) {
        console.error('クリップボードコピーエラー:', error);
        throw error;
    }
}

// ランキング表示
function displayRankings(rankings) {
    if (!elements || !elements.rankingsContainer) {
        console.error('Elements not initialized');
        return;
    }

    if (!rankings || rankings.length === 0) {
        elements.rankingsContainer.innerHTML = `
            <div class="empty-state">
                <p>ランキングデータがありません</p>
                <p class="text-muted">スタンプを集めてランキングに参加しましょう！</p>
            </div>
        `;
        return;
    }
    
    let html = '<ol class="ranking-list">';
    rankings.forEach((entry, index) => {
        const rank = entry.rank || (index + 1);
        const medal = rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : '';
        const isSelf = entry.is_self || false;
        const selfClass = isSelf ? 'self' : '';
        
        html += `
            <li class="ranking-item ${rank <= 3 ? 'top-three' : ''} ${selfClass}">
                <span class="rank">${medal} ${rank}位</span>
                <span class="name">${escapeHtml(entry.display_name || 'Unknown')}${isSelf ? ' (あなた)' : ''}</span>
                <span class="count">${entry.stamp_count || 0}個</span>
            </li>
        `;
    });
    html += '</ol>';
    
    elements.rankingsContainer.innerHTML = html;
}

// エラー表示
function showError(message) {
    if (!elements || !elements.rankingsContainer) {
        console.error('Elements not initialized');
        alert(message);
        return;
    }

    elements.rankingsContainer.innerHTML = `
        <div class="error">
            <div class="error-icon">⚠️</div>
            <p>${escapeHtml(message)}</p>
            <button onclick="location.reload()" class="btn btn-primary">再読み込み</button>
        </div>
    `;
}

// HTMLエスケープ
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

