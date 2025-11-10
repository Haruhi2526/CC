"use strict";

// 各スポットの spotId を定義（AWS側と合わせる）
const SPOT_IDS = {
    yil: "YIL-001",
    statue: "STATUE-001",
    BLD14213: "BLD14-RM213",
    MONU075: "MONU-075",
    SEV001: "SEV-001"
};

// 各スポットのスタンプ画像を定義
const stampImages = {
    "STATUE-001": "assets/images/stamps/statue.png",
    "YIL-001": "assets/images/stamps/yil.png",
    "BLD14-RM213": "assets/images/stamps/bld14213.png",
    "MONU-075": "assets/images/stamps/object34.png",
    "SEV-001": "assets/images/stamps/seven-eleven.png"
};

// 各スポットの説明を定義
const explanations = {
    "STATUE-001": "藤原銀次郎先生の銅像である。17歳より慶應義塾に学び、1939年に資材を投じて藤原工業大学を設立。1944年に同大を慶應義塾に寄付し、慶應義塾大学工学部(現理工学部)となった。",
    "YIL-001": "イノベーションの拠点として、人が集い、議論し、学び、挑戦する場所を提供するために、2025年に開設された。36棟前の奥行5mの細長い敷地にあり、うなぎ（eel）の寝床のような空間への親しみも込めて、「YIL（イール）」という愛称で呼ばれている。",
    "BLD14-RM213": "14棟にあるディスカッションルームの一つであり、主にグループワークやミーティングに使用される。クラウドコンピューティング実験(本実験)は、主にこの教室で開催された。",
    "MONU-075": "慶應義塾大学理工学部の創立75周年を記念して34棟に設置されたモニュメントである。理工学部の歴史と伝統を象徴し、未来への展望を示すものとして、学生や教職員に親しまれている。",
    "SEV-001": "矢上キャンパス内にあるセブンイレブンであり、毎日多くの学生が利用している。食料品、飲料、日用品など、様々な商品を取り揃えており、学生生活をサポートしている。",
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
const locationName = document.getElementById("locationName");
const locationImg = document.getElementById("location-img");
const loadingPic = document.getElementById("loadingPic");
const obtainedModal = document.getElementById('obtainedModal');
const mask2 = document.getElementById('mask2');
const out = document.getElementById('out');

// スタンプ画像をUIに追加する共通関数
function appendStampImage(spotId, nameIfAny) {
    const stampSrc = stampImages[spotId];
    if (!stampSrc) {
        console.warn('スタンプ画像が見つかりません:', spotId);
        return;
    }
    const container = document.getElementById('stampsContainer');
    if (!container) return;
    const emptyMsg = container.querySelector('.empty-message');
    if (emptyMsg) emptyMsg.remove();
    if (!container.querySelector(`img[data-spot="${spotId}"]`)) {
        const img = document.createElement('img');
        img.src = stampSrc;
        img.alt = nameIfAny || spotId;
        img.dataset.spot = spotId;
        img.classList.add('stamp');
        container.appendChild(img);
    }
}

// yil modal
document.getElementById("yil").addEventListener("click", async () => {
    locationModal.style.visibility = "visible";
    mask.style.visibility = "visible";
    locationModal.animate(showListKeyframes, options);
    mask.animate(showListKeyframes, options);
    locationName.textContent = "YIL Entrance";
    loadingPic.style.display = "";
    locationImg.style.display = "none";
    locationImg.src = "assets/images/yil.png";
    out.textContent = explanations["YIL-001"];
    locationImg.onload = () => { // success
        loadingPic.style.display = "none";
        locationImg.style.display = "block";
    };
    selectedSpot = "yil";
});

// statue
document.getElementById("statue").addEventListener("click", async () => {
    locationModal.style.visibility = "visible";
    mask.style.visibility = "visible";
    locationModal.animate(showListKeyframes, options);
    mask.animate(showListKeyframes, options);
    locationName.textContent = "Mr.Fujiwara Statue";
    loadingPic.style.display = "";
    locationImg.style.display = "none";
    locationImg.src = "assets/images/statue.png";
    out.textContent = explanations["STATUE-001"];
    locationImg.onload = () => { // success
        loadingPic.style.display = "none";
        locationImg.style.display = "block";
    };
    selectedSpot = "statue";
});

// 14-213
document.getElementById("BLD14-213").addEventListener("click", async () => {
    locationModal.style.visibility = "visible";
    mask.style.visibility = "visible";
    locationModal.animate(showListKeyframes, options);
    mask.animate(showListKeyframes, options);
    locationName.textContent = "14-213 Classroom";
    loadingPic.style.display = "";
    locationImg.style.display = "none";
    locationImg.src = "assets/images/BLD14213.png";
    out.textContent = explanations["BLD14-RM213"];
    locationImg.onload = () => { // success
        loadingPic.style.display = "none";
        locationImg.style.display = "block";
    };
    selectedSpot = "BLD14213";
});

// object34
document.getElementById("object34").addEventListener("click", async () => {
    locationModal.style.visibility = "visible";
    mask.style.visibility = "visible";
    locationModal.animate(showListKeyframes, options);
    mask.animate(showListKeyframes, options);
    locationName.textContent = "75th Monument";
    loadingPic.style.display = "";
    locationImg.style.display = "none";
    locationImg.src = "assets/images/object34.png";
    out.textContent = explanations["MONU-075"];
    locationImg.onload = () => { // success
        loadingPic.style.display = "none";
        locationImg.style.display = "block";
    };
    selectedSpot = "MONU075";
});

// seven-eleven
document.getElementById("sevenEleven").addEventListener("click", async () => {
    locationModal.style.visibility = "visible";
    mask.style.visibility = "visible";
    locationModal.animate(showListKeyframes, options);
    mask.animate(showListKeyframes, options);
    locationName.textContent = "7-Eleven in Yagami";
    loadingPic.style.display = "";
    locationImg.style.display = "none";
    locationImg.src = "assets/images/seven-eleven.png";
    out.textContent = explanations["SEV-001"];
    locationImg.onload = () => { // success
        loadingPic.style.display = "none";
        locationImg.style.display = "block";
    };
    selectedSpot = "SEV001";
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
        // リセット
        document.getElementById('out').textContent = ""; 
        document.getElementById("photoInput").value = "";
        uploadButton.classList.remove('abled');
        uploadButton.disabled = true;
    };
});

// mask
mask.addEventListener("click", () => {
    closeButton.dispatchEvent(new PointerEvent("click"));
});

function obtainedModalShow() {
    // 表示（フェードイン）
    obtainedModal.style.display = 'block';
    mask2.style.display = 'block';
    requestAnimationFrame(() => {
        obtainedModal.style.opacity = '1';
        mask2.style.opacity = '1';
    });

    // 3秒後にフェードアウトして非表示にする
    setTimeout(() => {
        obtainedModal.style.opacity = '0';
        mask2.style.opacity = '0';
        setTimeout(() => {
            obtainedModal.style.display = 'none';
            mask2.style.display = 'none';
        }, 500); // フェードアウト時間と合わせる
    }, 3000);
}

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
                    `\nName: ${result.name || ''}` +
                    `\nLat: ${latitude.toFixed(6)}` +
                    `\nLon: ${longitude.toFixed(6)}` +
                    `\nDistance: ${result.distanceM || 0}m`;
                
                // 範囲内ならUIにスタンプを表示（ユーザーIDに関わらず）
                if (inside) {
                    obtainedModalShow(); // スタンプ獲得モーダル表示
                    // ボタンを操作可能に
                    uploadButton.classList.add('abled');
                    uploadButton.disabled = false;

                    uploadButton.onclick = async () => {
                        const file = photoInput.files[0];
                        if (!file) {
                            alert('画像ファイルを選択してください。');
                            return;
                        }
                        // 画像アップロード処理追加
                    }
                    // 現在のスタンプ取得状況を取得
                    const userId = sessionStorage.getItem(CONFIG.STORAGE_KEYS.USER_ID);
                    let userStamps = [];

                    try {
                        userStamps = await window.api.getUserStamps(userId);
                    } catch (err) {
                        console.error("スタンプ取得エラー:", err);
                    }

                    // すでに取得済みなら追加処理しない
                    const alreadyObtained = userStamps.some(s => s.stamp_id === spotIdToSend);
                    if (alreadyObtained) {
                        console.log(`スタンプ「${spotIdToSend}」はすでに取得済みです`);
                    } else {
                        // バックエンドにスタンプ授与
                        try {
                            await window.api.awardStamp(userId, spotIdToSend, 'GPS');
                            console.log('スタンプ授与成功');
                        } catch (awardError) {
                            console.error('スタンプ授与エラー:', awardError);
                        }

                        // 再度スタンプ一覧を取得し、UIを再描画
                        try {
                            await loadStamps(userId);
                        } catch (refreshError) {
                            console.error("スタンプ再取得エラー:", refreshError);
                        }
                    }
                }

                // 認証済みユーザーのみバックエンドでスタンプ授与を試みる
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