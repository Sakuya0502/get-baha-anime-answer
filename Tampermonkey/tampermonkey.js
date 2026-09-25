// ==UserScript==
// @name         獲取動漫通答案
// @namespace    http://tampermonkey.net/
// @version      0.0.1
// @description  在動畫瘋頂部選單加入動漫通答案按鈕
// @author       Sakuya0502
// @license      MIT
// @match        *://ani.gamer.com.tw/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=gamer.com.tw
// @grant        GM_addStyle
// @noframes
// ==/UserScript==

(function() {
    'use strict';

    if (window.self !== window.top) return;

    GM_addStyle(`
        #baha-ans-nav-btn {
            background: #F00078
        }
        #baha-ans-nav-btn:hover {
            background: #FF359A
        }
        #baha-ans-modal {
            position: fixed;
            z-index: 999999;
            width: 320px;
            background: #232529;
            color: #ffffff;
            border: 1px solid #3c4048;
            border-radius: 10px;
            box-shadow: 0 14px 35px rgba(0, 0, 0, 0.65);
            padding: 16px;
            box-sizing: border-box;
            display: none;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            user-select: none;
        }
        .ans-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #3c4048;
            padding-bottom: 8px;
            margin-bottom: 12px;
            font-size: 15px;
            font-weight: bold;
            color: #00d2ff;
            cursor: move;
        }
        .ans-close-btn {
            cursor: pointer;
            font-size: 16px;
            color: #999;
            border: none;
            background: transparent;
            line-height: 1;
            padding: 2px 6px;
        }
        .ans-close-btn:hover {
            color: #fff;
        }
        .ans-body {
            font-size: 14px;
            line-height: 1.6;
            user-select: text;
        }
        .ans-num {
            color: #aaa;
            margin-bottom: 4px;
        }
        .ans-highlight {
            font-size: 18px;
            font-weight: bold;
            color: #ffca28;
            word-break: break-all;
        }
    `);

    const modal = document.createElement("div");
    modal.id = "baha-ans-modal";
    modal.innerHTML = `
        <div class="ans-header" id="baha-ans-header">
            <span>🎯 今日動漫通答案</span>
            <button class="ans-close-btn" id="baha-ans-close">✕</button>
        </div>
        <div class="ans-body" id="baha-ans-content">
            <span style="color: #aaa;">載入答案中...</span>
        </div>
    `;
    document.body.appendChild(modal);
    const header = document.getElementById("baha-ans-header");
    const closeBtn = document.getElementById("baha-ans-close");
    closeBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        modal.style.display = "none";
    });

    function centerModal() {
        modal.style.display = "block";
        const modalWidth = modal.offsetWidth || 320;
        const modalHeight = modal.offsetHeight || 160;
        const left = Math.max(0, (window.innerWidth - modalWidth) / 2);
        const top = Math.max(0, (window.innerHeight - modalHeight) / 2);
        modal.style.left = `${left}px`;
        modal.style.top = `${top}px`;
    }
    let isDragging = false;
    let startX = 0, startY = 0;
    let initialLeft = 0, initialTop = 0;

    header.addEventListener("mousedown", (e) => {
        if (e.target === closeBtn) return;

        isDragging = true;
        startX = e.clientX;
        startY = e.clientY;
        initialLeft = modal.offsetLeft;
        initialTop = modal.offsetTop;
        document.addEventListener("mousemove", onMouseMove);
        document.addEventListener("mouseup", onMouseUp);
        e.preventDefault();
    });

    function onMouseMove(e) {
        if (!isDragging) return;
        const dx = e.clientX - startX;
        const dy = e.clientY - startY;
        let newLeft = initialLeft + dx;
        let newTop = initialTop + dy;
        const maxLeft = window.innerWidth - modal.offsetWidth;
        const maxTop = window.innerHeight - modal.offsetHeight;
        newLeft = Math.max(0, Math.min(newLeft, maxLeft));
        newTop = Math.max(0, Math.min(newTop, maxTop));
        modal.style.left = `${newLeft}px`;
        modal.style.top = `${newTop}px`;
    }

    function onMouseUp() {
        isDragging = false;
        document.removeEventListener("mousemove", onMouseMove);
        document.removeEventListener("mouseup", onMouseUp);
    }

    let currentAnsKey = "";

    async function fetchAndUpdateUI(isBackground = false) {
        const contentBox = document.getElementById("baha-ans-content");
        
        if (!currentAnsKey && !isBackground) {
            contentBox.innerHTML = `<span style="color: #aaa;">載入答案中...</span>`;
        }
      
        const json_url = `https://raw.githubusercontent.com/Sakuya0502/get-baha-anime-answer/main/answer.json?t=${Date.now()}`;

        try {
            const response = await fetch(json_url, { cache: "no-store" });
            if (!response.ok) throw new Error(`HTTP 錯誤: ${response.status}`);
            const data = await response.json();
            const ansObj = data.answer;
            if (!ansObj || Object.keys(ansObj).length === 0) return;
            const [ansNum, ansText] = Object.entries(ansObj)[0];
            const newKey = `${ansNum}-${ansText}`;
            if (newKey !== currentAnsKey) {
                currentAnsKey = newKey;
                contentBox.innerHTML = `
                    <div class="ans-num">選項號碼：<strong>${ansNum}</strong></div>
                    <div class="ans-highlight ans-updated-flash">${ansText}</div>
                `;
                console.log(`答案已熱更新 -> [${ansNum}] ${ansText}`);
            }
        } catch (err) {
            if (!currentAnsKey) {
                contentBox.innerHTML = `<span style="color: #ff6b6b;">答案獲取失敗</span>`;
            }
        }
    }
    setInterval(() => {
        fetchAndUpdateUI(true);
    }, 30 * 1000);

    function add_btn() {
        if (document.getElementById("baha-ans-nav-btn")) return;
        const timer = setInterval(() => {
            const top_bar = document.querySelector(".mainmenu > .container-player > ul") || document.querySelector(".mainmenu ul");
            if (top_bar) {
                clearInterval(timer);
                const setBTN = document.createElement("li");
                setBTN.id = "baha-ans-nav-btn";
                const setBTName = document.createElement("a");
                setBTName.href = "javascript:void(0);";
                setBTName.innerHTML = "動漫通答案";
                setBTN.appendChild(setBTName);
                top_bar.appendChild(setBTN);
                setBTN.addEventListener("click", (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    const isVisible = modal.style.display === "block";
                    if (isVisible) {
                        modal.style.display = "none";
                    } else {
                        centerModal();
                        fetchAndUpdateUI(false);
                    }
                });
            }
        }, 300);
    }

    add_btn();
})();
