"use strict";

const ENDPOINT = "https://is77v2y5ff.execute-api.us-east-1.amazonaws.com/gps/check";
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

document.getElementById('checkinButton').onclick = () => {
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
        // 緯度・経度（小数, 単位は度）と精度[m]を取り出す
        const { latitude, longitude, accuracy } = pos.coords;
        console.log(`lat=${latitude}, lon=${longitude}, accuracy=${accuracy}m`);
        
        const spotIdToSend = SPOT_IDS[selectedSpot];

        // 位置情報をサーバに送って判定（最寄りのみ判定: mode不要）
        const res = await fetch(ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            // サーバ側が必要とする JSON 形式：userId / lat / lon / accuracy
            body: JSON.stringify({
                userId: 'user123',    // ユーザー識別子（今は仮でOK。あとでLINEのuserIdなどに置換）
                spotId: spotIdToSend, // チェックするスポットID
                lat: latitude,
                lon: longitude,
                accuracy              // 端末の推定誤差[m]。サーバは max(radiusM, accuracy) で判定済み
            })
        });

        // レスポンス JSON を取得（例：{spotId, name, distanceM, within, ...}）
        const json = await res.json();

        // 「どこかのスタンプに入ってるか？」= 最寄りの within が true かを見る
        const inside = !!json.within;

        // 画面出力
        document.getElementById('out').textContent =
        (inside ? "範囲内 ✅" : "範囲外 ❌") +
        `\nname: ${json.name}` +
        `\nlat: ${latitude}` +
        `\nlon: ${longitude}` +
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