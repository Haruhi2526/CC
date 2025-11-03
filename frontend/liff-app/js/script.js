"use strict";

// 各スポットの spotId を定義（AWS側と合わせる）
const SPOT_IDS = {
    yil: "YIL-001",
    statue: "STATUE-001"
};
let selectedSpot = null;

const showListKeyframes = {
    opacity: [0, 1],
};
const hideListKeyframes = {
    opacity: [1, 0],
};
const options = {
    duration: 400,
    easing: 'ease',
    fill: 'forwards',
};

let isAnimating = false;
const myPageButton = document.getElementById("myPageButton");
const locationModal = document.getElementById("locationModal");
const closeButton = document.getElementById("closeButton");
const mask = document.getElementById("mask");
const locationName = document.getElementById("locationName")

// yil modal
document.getElementById("yil").addEventListener("click", async () => {
    locationModal.style.visibility = "visible";
    mask.style.visibility = "visible";
    locationModal.animate(showListKeyframes, options);
    mask.animate(showListKeyframes, options);
    locationName.textContent = "YIL Entrance";
    document.getElementById("location-img").src = "assets/images/yil.png";
    selectedSpot = "yil";
});

document.getElementById("statue").addEventListener("click", async () => {
    locationModal.style.visibility = "visible";
    mask.style.visibility = "visible";
    locationModal.animate(showListKeyframes, options);
    mask.animate(showListKeyframes, options);
    locationName.textContent = "Mr.Fujiwara Statue";
    document.getElementById("location-img").src = "assets/images/statue.png";
    selectedSpot = "statue";
});

closeButton.addEventListener("click", () => {
    if (isAnimating) return; // すでにアニメーション中なら処理しない
    isAnimating = true;
    mask.animate(hideListKeyframes, options);
    mask.style.pointerEvents = "none";
    locationModal.animate(hideListKeyframes, options).onfinish = () => { // アニメーション完了後にクリック許可
        mask.style.pointerEvents = "auto";
        isAnimating = false;
        locationModal.style.visibility = "hidden";
        mask.style.visibility = "hidden";
        document.getElementById('out').textContent = ""; // リセット
    };
});

// mask
mask.addEventListener("click", () => {
    closeButton.dispatchEvent(new PointerEvent("click"));
});

document.getElementById('checkinButton').onclick = async () => {
    if (!selectedSpot) {
        alert("スポットを選択してください。");
        return;
    }
    if (!navigator.geolocation) {
        alert("このブラウザでは位置情報が利用できません。");
        return;
    }

    document.getElementById('out').textContent = "位置情報取得中…";

    // 端末の現在地を取得（ブラウザの Geolocation API）
    navigator.geolocation.getCurrentPosition(async (pos) => {
        try {
        // 緯度・経度（小数, 単位は度）と精度[m]を取り出す
        const { latitude, longitude, accuracy } = pos.coords;
        console.log(`lat=${latitude}, lon=${longitude}, accuracy=${accuracy}m`);
        
        const spotIdToSend = SPOT_IDS[selectedSpot];

            // ユーザーIDを取得（セッションストレージから）
            const userId = sessionStorage.getItem(CONFIG.STORAGE_KEYS.USER_ID) || 'user123';

            // バックエンドAPIを使用してGPS検証
            const result = await window.api.verifyGPS(
                userId,
                spotIdToSend,
                latitude,
                longitude,
                accuracy
            );

            // レスポンスの処理
            if (result && result.ok !== false) {
                const inside = !!result.within;

        // 画面出力
        document.getElementById('out').textContent =
        (inside ? "範囲内 ✅" : "範囲外 ❌") +
                    `\nname: ${result.name || ''}` +
                    `\nlat: ${latitude.toFixed(6)}` +
                    `\nlon: ${longitude.toFixed(6)}` +
                    `\ndistanceM: ${result.distanceM || 0}m` +
                    `\nradiusM: ${result.radiusM || 100}m`;
                
                // 範囲内の場合はスタンプ授与を試みる（オプション）
                if (inside && userId !== 'user123') {
                    try {
                        await window.api.awardStamp(userId, spotIdToSend, 'GPS');
                        console.log('スタンプ授与成功');
                    } catch (awardError) {
                        console.error('スタンプ授与エラー:', awardError);
                        // エラーは無視（既に取得済みなどの可能性がある）
                    }
                }
            } else {
                // エラーレスポンスの場合
                const errorMessage = result?.message || 'GPS検証に失敗しました';
                document.getElementById('out').textContent = `エラー: ${errorMessage}`;
                console.error('GPS検証エラー:', result);
            }
        } catch (error) {
            // エラーハンドリング
            console.error('GPS検証エラー:', error);
            alert('位置情報検証エラー: ' + (error.message || error));
            document.getElementById('out').textContent = 'エラー: ' + (error.message || '位置情報検証に失敗しました');
        }
    }, (err) => {
        // 位置情報取得に失敗したときの処理
        alert('位置情報エラー: ' + err.message);
        document.getElementById('out').textContent = '位置情報取得エラー: ' + err.message;
    }, {
        // オプション：高精度・タイムアウト・キャッシュ無効
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
    });
};