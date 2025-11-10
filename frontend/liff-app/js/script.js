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
const photoInput = document.getElementById("photoInput");
const uploadButton = document.getElementById("uploadButton");

// ファイル選択時にアップロードボタンを有効化する関数
function setupFileInputListener() {
    const currentPhotoInput = document.getElementById("photoInput");
    const currentUploadButton = document.getElementById("uploadButton");
    
    if (currentPhotoInput && currentUploadButton) {
        // 既存のイベントリスナーを削除（重複を防ぐ）
        const newPhotoInput = currentPhotoInput.cloneNode(true);
        currentPhotoInput.parentNode.replaceChild(newPhotoInput, currentPhotoInput);
        
        newPhotoInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            const btn = document.getElementById("uploadButton");
            
            if (file && btn) {
                // ファイルが選択されたら、ボタンが有効な場合のみ有効化
                // （チェックイン後に有効化されている場合のみ）
                if (btn.classList.contains('abled')) {
                    btn.disabled = false;
                    console.log('ファイルが選択されました。アップロードボタンを有効化しました。');
                } else {
                    console.log('ファイルが選択されましたが、チェックインが必要です。');
                }
            } else if (btn) {
                btn.disabled = true;
            }
        });
    }
}

// 初期設定
if (photoInput && uploadButton) {
    setupFileInputListener();
}
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
        const outElement = document.getElementById('out');
        if (outElement) {
            outElement.textContent = "";
        }
        const currentPhotoInput = document.getElementById("photoInput");
        if (currentPhotoInput) {
            currentPhotoInput.value = "";
        }
        const currentUploadButton = document.getElementById("uploadButton");
        if (currentUploadButton) {
            currentUploadButton.classList.remove('abled');
            currentUploadButton.disabled = true;
        }
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
                
                // 範囲内ならUploadボタンを有効化（スタンプは画像認識成功時に付与）
                if (inside) {
                    // 現在のボタン要素を取得（DOMから直接取得）
                    const currentUploadButton = document.getElementById("uploadButton");
                    const currentPhotoInput = document.getElementById("photoInput");
                    
                    if (currentUploadButton) {
                        // ボタンを操作可能に
                        currentUploadButton.classList.add('abled');
                        // ファイルが選択されている場合のみ有効化
                        const hasFile = currentPhotoInput && currentPhotoInput.files && currentPhotoInput.files[0];
                        currentUploadButton.disabled = !hasFile;
                        
                        console.log('チェックイン成功。アップロードボタンの状態:', {
                            hasFile: hasFile,
                            disabled: currentUploadButton.disabled,
                            hasAbledClass: currentUploadButton.classList.contains('abled')
                        });
                    }

                    // ファイル選択イベントリスナーを再設定
                    setupFileInputListener();

                    // アップロードボタンのイベントリスナーを設定
                    if (currentUploadButton) {
                        // 既存のイベントリスナーを削除（重複を防ぐ）
                        // 新しいボタンを作成して置き換え
                        const newUploadButton = currentUploadButton.cloneNode(true);
                        currentUploadButton.parentNode.replaceChild(newUploadButton, currentUploadButton);
                        
                        // 新しいボタン要素を取得
                        const btn = document.getElementById("uploadButton");
                        
                        // ボタンの状態を再設定
                        btn.classList.add('abled');
                        const hasFile = currentPhotoInput && currentPhotoInput.files && currentPhotoInput.files[0];
                        btn.disabled = !hasFile;
                        
                        // selectedSpotを保存（クロージャーで保持）
                        const currentSelectedSpot = selectedSpot;
                        
                        btn.addEventListener('click', async () => {
                            const currentInput = document.getElementById("photoInput");
                            const currentBtn = document.getElementById("uploadButton");
                            const file = currentInput ? currentInput.files[0] : null;
                            
                            if (!file) {
                                alert('画像ファイルを選択してください。');
                                return;
                            }
                            
                            // ユーザーIDを取得
                            const userId = sessionStorage.getItem(CONFIG.STORAGE_KEYS.USER_ID);
                            if (!userId) {
                                alert('ログインが必要です。');
                                return;
                            }
                            
                            // スポットIDを取得
                            if (!currentSelectedSpot) {
                                alert('スポットが選択されていません。');
                                return;
                            }
                            
                            const spotIdToSend = SPOT_IDS[currentSelectedSpot];
                            if (!spotIdToSend) {
                                alert('無効なスポットです。');
                                return;
                            }
                            
                            try {
                                // アップロードボタンを無効化
                                if (currentBtn) {
                                    const originalText = currentBtn.textContent;
                                    currentBtn.setAttribute('data-original-text', originalText);
                                    currentBtn.disabled = true;
                                    currentBtn.textContent = 'アップロード中...';
                                }
                                
                                console.log('Presigned URLを取得中...', { userId, fileName: file.name, spotId: spotIdToSend });
                                
                                // Presigned URLを取得
                                const uploadUrlResponse = await window.api.getS3UploadUrl(userId, file.name);
                                
                                console.log('Presigned URL取得結果:', uploadUrlResponse);
                                
                                if (!uploadUrlResponse || !uploadUrlResponse.ok) {
                                    throw new Error('Presigned URLの取得に失敗しました');
                                }
                                
                                console.log('S3にアップロード中...');
                                
                                // S3にアップロード
                                await window.api.uploadToS3(
                                    uploadUrlResponse.upload_url,
                                    uploadUrlResponse.fields,
                                    file
                                );
                                
                                console.log('S3アップロード成功');
                                
                                // アップロード成功
                                const outElement = document.getElementById('out');
                                if (outElement) {
                                    outElement.textContent = 
                                        '画像をアップロードしました！\n画像認識処理中...\n（数秒後にスタンプが付与される場合があります）';
                                }
                                
                                // スタンプ一覧を更新して、スタンプが付与されたか確認
                                // 画像認識処理には数秒かかるため、複数回チェック
                                let checkCount = 0;
                                const maxChecks = 10; // 最大10回（約20秒間）
                                const checkInterval = 2000; // 2秒間隔
                                
                                const checkStampAwarded = async () => {
                                    try {
                                        // 現在のスタンプ一覧を取得
                                        const currentStamps = await window.api.getStamps(userId);
                                        const stampIds = currentStamps.stamps ? currentStamps.stamps.map(s => s.stamp_id) : [];
                                        
                                        // このスポットのスタンプが付与されたか確認
                                        const stampAwarded = stampIds.includes(spotIdToSend);
                                        
                                        if (stampAwarded) {
                                            // スタンプが付与された
                                            console.log('スタンプが付与されました:', spotIdToSend);
                                            obtainedModalShow(); // スタンプ獲得モーダル表示
                                            
                                            if (outElement) {
                                                outElement.textContent = 
                                                    '画像認識成功！\nスタンプを獲得しました！';
                                            }
                                            
                                            // スタンプ一覧を更新
                                            if (typeof loadStamps === 'function') {
                                                await loadStamps(userId);
                                            } else if (window.loadStamps) {
                                                await window.loadStamps(userId);
                                            }
                                        } else if (checkCount < maxChecks) {
                                            // まだスタンプが付与されていない場合、再度チェック
                                            checkCount++;
                                            console.log(`スタンプ付与を確認中... (${checkCount}/${maxChecks})`);
                                            setTimeout(checkStampAwarded, checkInterval);
                                        } else {
                                            // タイムアウト
                                            console.log('スタンプ付与の確認がタイムアウトしました');
                                            if (outElement) {
                                                outElement.textContent = 
                                                    '画像をアップロードしました。\n画像認識結果を確認中...\n（スタンプが付与されない場合は、画像が正しく認識されていない可能性があります）';
                                            }
                                            
                                            // スタンプ一覧を更新（念のため）
                                            if (typeof loadStamps === 'function') {
                                                await loadStamps(userId);
                                            } else if (window.loadStamps) {
                                                await window.loadStamps(userId);
                                            }
                                        }
                                    } catch (refreshError) {
                                        console.error("スタンプ確認エラー:", refreshError);
                                        // エラーが発生しても、スタンプ一覧を更新
                                        try {
                                            if (typeof loadStamps === 'function') {
                                                await loadStamps(userId);
                                            } else if (window.loadStamps) {
                                                await window.loadStamps(userId);
                                            }
                                        } catch (e) {
                                            console.error("スタンプ再取得エラー:", e);
                                        }
                                    }
                                };
                                
                                // 最初のチェックを開始（3秒後）
                                setTimeout(checkStampAwarded, 3000);
                                
                            } catch (error) {
                                console.error('画像アップロードエラー:', error);
                                alert('画像アップロードに失敗しました: ' + (error.message || error));
                                const outElement = document.getElementById('out');
                                if (outElement) {
                                    outElement.textContent = 
                                        'エラー: ' + (error.message || '画像アップロードに失敗しました');
                                }
                            } finally {
                                // ボタンを再有効化
                                const currentBtn = document.getElementById("uploadButton");
                                if (currentBtn) {
                                    currentBtn.disabled = false;
                                    const originalText = currentBtn.getAttribute('data-original-text') || 'Upload';
                                    currentBtn.textContent = originalText;
                                }
                            }
                        });
                    }
                } else {
                    // 範囲外の場合、Uploadボタンを無効化
                    const currentUploadButton = document.getElementById("uploadButton");
                    if (currentUploadButton) {
                        currentUploadButton.classList.remove('abled');
                        currentUploadButton.disabled = true;
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