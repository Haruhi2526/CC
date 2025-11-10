// ランキング画面のロジック

const elements = {
    rankingsContainer: document.getElementById('rankingsContainer'),
    shareButton: document.getElementById('shareButton'),
    tabs: document.querySelectorAll('.tab')
};

let currentPeriod = 'weekly';
let currentRankings = [];

// LIFF初期化
liff.init({ liffId: CONFIG.LIFF_ID })
    .then(() => {
        if (liff.isLoggedIn()) {
            loadRankings(currentPeriod);
        } else {
            // 未ログインの場合はログイン画面にリダイレクト
            liff.login();
        }
    })
    .catch(error => {
        console.error('LIFF初期化エラー:', error);
        showError('アプリの初期化に失敗しました。ページを再読み込みしてください。');
    });

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
        elements.rankingsContainer.innerHTML = `
            <div class="loading">
                <div class="loading-spinner"></div>
                <p>読み込み中...</p>
            </div>
        `;
        
        const endpoint = period === 'weekly' 
            ? '/ranking/weekly' 
            : '/ranking/monthly';
        
        const response = await api.getRankings(endpoint);
        
        if (response.ok && response.rankings) {
            currentRankings = response.rankings;
            displayRankings(response.rankings);
        } else {
            throw new Error(response.message || 'ランキングの取得に失敗しました');
        }
    } catch (error) {
        console.error('ランキング取得失敗:', error);
        showError(error.message || 'ランキングの取得に失敗しました');
    }
}

// ランキング表示
function displayRankings(rankings) {
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
        
        html += `
            <li class="ranking-item ${rank <= 3 ? 'top-three' : ''}">
                <span class="rank">${medal} ${rank}位</span>
                <span class="name">${escapeHtml(entry.display_name || 'Unknown')}</span>
                <span class="count">${entry.stamp_count || 0}個</span>
            </li>
        `;
    });
    html += '</ol>';
    
    elements.rankingsContainer.innerHTML = html;
}

// エラー表示
function showError(message) {
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

// シェア機能
elements.shareButton.addEventListener('click', async () => {
    try {
        if (typeof liff !== 'undefined' && liff.isApiAvailable('shareTargetPicker')) {
            const shareUrl = `${window.location.origin}/ranking.html`;
            const shareText = currentRankings.length > 0
                ? `🏆 スタンプラリーランキング（${currentPeriod === 'weekly' ? '週間' : '月間'}）\n\n` +
                  `1位: ${currentRankings[0]?.display_name || 'Unknown'} (${currentRankings[0]?.stamp_count || 0}個)\n` +
                  `あなたもスタンプを集めてランキングに参加しよう！\n\n${shareUrl}`
                : `スタンプラリーランキングを見てみて！\n${shareUrl}`;
            
            await liff.shareTargetPicker([
                {
                    type: 'text',
                    text: shareText
                }
            ]);
        } else {
            // フォールバック: URLをクリップボードにコピー
            const shareUrl = `${window.location.origin}/ranking.html`;
            try {
                await navigator.clipboard.writeText(shareUrl);
                alert('URLをクリップボードにコピーしました');
            } catch (e) {
                // クリップボードAPIが使えない場合
                prompt('以下のURLをコピーしてください:', shareUrl);
            }
        }
    } catch (error) {
        console.error('シェアエラー:', error);
        alert('シェアに失敗しました');
    }
});

