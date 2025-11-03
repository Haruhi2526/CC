"use strict";

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
const myPageModal = document.getElementById("myPageModal");
const locationModal = document.getElementById("locationModal");
const closeButton = document.getElementById("closeButton");
const closeMyPageButton = document.getElementById("closeMyPageButton");
const mask = document.getElementById("mask");
const maskM = document.getElementById("maskM");
const locationName = document.getElementById("locationName")

// MyPage
myPageButton.addEventListener("click", async () => {
    myPageModal.style.visibility = "visible";
    maskM.style.visibility = "visible";
    myPageModal.animate(showListKeyframes, options);
    maskM.animate(showListKeyframes, options);
});

closeMyPageButton.addEventListener("click", () => {
    if (isAnimating) return; // すでにアニメーション中なら処理しない
    isAnimating = true;
    maskM.animate(hideListKeyframes, options);
    maskM.style.pointerEvents = "none";
    myPageModal.animate(hideListKeyframes, options).onfinish = () => { // アニメーション完了後にクリック許可
        maskM.style.pointerEvents = "auto";
        isAnimating = false;
        myPageModal.style.visibility = "hidden";
        maskM.style.visibility = "hidden";
    };
});

// mask
maskM.addEventListener("click", () => {
    closeMyPageButton.dispatchEvent(new PointerEvent("click"));
});

// yil modal
document.getElementById("yil").addEventListener("click", async () => {
    locationModal.style.visibility = "visible";
    mask.style.visibility = "visible";
    locationModal.animate(showListKeyframes, options);
    mask.animate(showListKeyframes, options);
    locationName.textContent = "YIL Entrance";
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
    };
});

// mask
mask.addEventListener("click", () => {
    closeButton.dispatchEvent(new PointerEvent("click"));
});

const ENDPOINT = "https://is77v2y5ff.execute-api.us-east-1.amazonaws.com/gps/check";

document.getElementById('checkinButton').onclick = () => {
  // 端末の現在地を取得（ブラウザの Geolocation API）
    navigator.geolocation.getCurrentPosition(async (pos) => {
        // 緯度・経度（小数, 単位は度）と精度[m]を取り出す
        const { latitude, longitude, accuracy } = pos.coords;

        // 位置情報をサーバに送って判定（最寄りのみ判定: mode不要）
        const res = await fetch(ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            // サーバ側が必要とする JSON 形式：userId / lat / lon / accuracy
            body: JSON.stringify({
                userId: 'user123',   // ← ユーザー識別子（今は仮でOK。あとでLINEのuserIdなどに置換）
                lat: latitude,
                lon: longitude,
                accuracy             // 端末の推定誤差[m]。サーバは max(radiusM, accuracy) で判定済み
            })
        });

        // レスポンス JSON を取得（例：{spotId, name, distanceM, within, ...}）
        const json = await res.json();

        // 「どこかのスタンプに入ってるか？」= 最寄りの within が true かを見る
        const inside = !!json.within;

        // 画面に出す（見やすいように主要フィールドだけ）
        document.getElementById('out').textContent =
        (inside ? "範囲内 ✅" : "範囲外 ❌") +
        `\nspotId: ${json.spotId}` +
        `\nname: ${json.name}` +
        `\ndistanceM: ${json.distanceM}`;

    }, (err) => {
        // 位置情報取得に失敗したときの処理
        alert('位置情報エラー: ' + err.message);
    }, {
        // オプション：高精度・タイムアウト・キャッシュ無効
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
    });
};
