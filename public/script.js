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
