---
_slug: 30-Areas-swimming-GAP-ANALYSIS
_vault_path: 30-Areas/swimming/GAP-ANALYSIS.md
title: Swimming Vault — Gap Analysis
created: '2026-05-23'
updated: '2026-06-15'
type: swimming
tags: []
status: budding
---

# Swimming Vault — Gap Analysis

> 審查：Hestia（外部視角）
> 基準：Vortex Project（上游）+ ARCHITECTURE.md（vault 自身規範）
> 日期：2026-05-23

---

## 總論

Vault 現有内容：16 個檔案，分布在 3 個區塊（RAW / technique / 根目錄）。
Vortex 上游：41 個檔案，分布在 6 個層（Instructional / Technica / Bridge / Research/感知科學 / Research/物理現象 / Observations）。

Vault 已整合 Vortex Instructional 的物理層（Section 1–5 完成）。但 Vortex 最核心的創新——**感知層（L0–L6 水感框架）**——完全未進入 vault。這不只是缺口，是方向問題。

---

## 第一層：ARCHITECTURE 規範違規

### G1：缺少 `insights/` 目錄（嚴重）

**規範依據**：ARCHITECTURE.md 明文建立 `swimming/insights/`（第76–81行），用於存放月度消化產物，頻率每週由 Hearth cron job 執行（`swimming-weekly-digest` skill）。

**現況**：
```
$ ls /root/obsidian-vault/swimming/insights/
→ 目錄不存在
```

**後果**：ARCHITECTURE 定義了兩個輸出層（technique/ 和 insights/），但只有一個實際運作。RAW → 技術動作 這條徑路存在，但 RAW → 洞察 這條徑路不存在。

**影響**：每週教練論壇監控、PubMed 文獻消化，都沒有結構化的月度產出沉積點。知識進入 vault 後是靜態的，不會随時間累積出綜合洞察。

---

### G2：`swimming-weekly-digest` skill 不存在（嚴重）

**規範依據**：ARCHITECTURE.md：「每週六由 Hearth cron job 消化一次（`swimming-weekly-digest` skill）」。

**現況**：技能清單中無此技能。無 cron job 執行每週文獻消化。

**影響**：vault 的 RAW 層會持續增長，但沒有轉換為洞察的機制。長時間下來 vault 會變成文獻倉庫而非知識庫。

---

## 第二層：Vortex 上游 → Vault 的內容缺口

### G3：感知層（Technica/）— 完全未整合

**上游**：Vortex Technica/ 6 個檔案
```
技術指標_L級對應框架.md  — 跨泳式 L 級技術指標總表
水感指南.md              — L0–L6 理論基礎（Part 1–6）
自由式水感框架.md        — 自由式 L0–L6
仰式水感框架.md          — 仰式 L0–L6
蛙式水感框架.md          — 蛙式 L0–L6
蝶式水感框架.md          — 蝶式 L0–L6
```

**現況**：vault 中無任何對應檔案。

**為什麼這是核心缺口**：

Vortex 的核心命題是「技術形式是感知系統的輸出，不是輸入」。

Vault 目前的架構是：
```
RAW（文獻）
  ↓
四式技術動作.md（技術動作本體）  ← 終點
  ↑                             
 這個方向是「由外而內」
```

Vortex 的方向是：
```
水感建立（L0–L6）
  ↓ 感知帶動動作
技術動作（自然的結果）
```

Vault 只拿了 Vortex 的「骨幹」（物理層動作描述），完全没拿「靈魂」（感知發展框架）。這代表 vault 的底層邏輯和 Vortex 是不相容的——如果把 vault 當作教練工具用，邏輯會打架。

**缺口規模**：6 個檔案，建議以一個整合檔案 `swimming/感知框架.md` 呈現，而非逐一複製。

---

### G4：感知橋接層（Bridge/）— 完全未整合

**上游**：Vortex Bridge/ 6 個檔案
```
自由式感知橋接.md   — 8 感知時刻 + SL/SR 區分 + 疲勞崩潰 + 三型識別
仰式感知橋接.md    — 9 感知時刻 + 三指標系統 + 旋轉方向感知
蛙式感知橋接.md    — 11 感知時刻 + 渦流整合 + 滑行管理
蝶式感知橋接.md    — 9 感知時刻 + 波動連鎖 + 兩踢不對稱
出發轉身感知橋接.md — 8 感知時刻 + 三型快速識別 + 指導語速查
水下蝶腳感知橋接.md — 7 感知時刻 + 三型識別 + 疲勞崩潰 + 指導語速查
```

**現況**：vault 中無任何對應檔案。

**橋接層的功能**：把物理層（Instructional）和感知層（Technica）串起來——每一個技術點，泳者「應該感覺到什麼」和「感覺錯了是什麼樣子」。這是教練在 poolside 最需要的东西。

**缺口規模**：6 個檔案，是從技術骨幹通往實際教學的必經之路。

---

### G5：教學誤區深探（Instructional/誤區）— 未整合

**上游**：Vortex Instructional/ 10 個誤區深探檔案
```
自由式教學誤區深探.md   — 10 條（回臂×5 + 入水×4 + 水下×1）
仰式教學誤區深探.md     — 4 大類（保持平躺 / S形 / 深抓 / 向下踢）
蛙式教學誤區深探.md     — 12 條（蛙腳×4 + 手部×2 + 換氣×3 + 時機×3）
蝶式教學誤區深探.md     — 14 條（划手×3 + 回臂×2 + 蝶腿×4 + 蝶腰×2 + 換氣×3）
出發與轉身教學誤區深探.md — 9 條（出發×4 + 轉身×4 + 觀念×1）
水下蝶腳教學誤區深探.md  — 13 條 + UDK vs 蝶式對照
```

**現況**：vault `四式技術動作.md` 有物理層動作描述，但沒有「教練在說什麼是錯的」這層。誤區深探不是動作描述，是教學語言的對錯分辨——這是教練最直接的參考資源。

**缺口規模**：6 個實質檔案（出發轉身誤區 + 四式各有1個）。

---

### G6：觀察層（Observations/）— 完全未整合

**上游**：Vortex Observations/ 3 個檔案
```
L0漂浮三態診斷.md     — 姿態三態 + 三種神經模式
小划手板實驗.md       — L1–L2 感知自組織課堂觀察
指令層次設計.md        — 身體運動語言 vs 流體意圖語言
```

**現況**：vault 中無任何對應。

**功能**：這些是「現場教學記錄」——教學案例、教練觀察、訓練設計工具。不是文獻，是實務沉澱。

**缺口規模**：3 個檔案，但實際價值高（可直接用於 practice plan）。

---

### G7：研究層（Research/）— 局部，未整合

**上游感知科學**（9 個檔案）：
- 因果倒置假設.md（核心理論）
- 機械感受器.md
- feedforward機制.md
- 感知學習.md
- 動態系統理論.md
- 內臟感知與迷走神經.md
- 感知量化SQ框架.md
- 神經學對照組三點座標.md
- 隱性_顯性學習.md

**上游物理現象**（5 個檔案）：
- 渦流回收.md（🟢 完整文獻）
- 推進力理論演變.md
- 自然頻率.md（🔵 + 🟢）
- 彈性蓄能.md（v4 完成）
- 教學競技.md

**現況**：
- vault RAW 有 5 個 research summary（SUMMARY.md）→ 對應 Vortex Research 的部分主題
- 但 Vortex 這 14 個檔案（感知科學 9 + 物理現象 5）沒有進入 vault
- RAW 存放的是文獻原文，研究層存放的是**假說與理論整合**——這是不同層次的東西

**缺口規模**：14 個檔案。建議优先整合「渦流回收」（已有完整文獻）和「因果倒置假設」（核心理論）。

---

## 第三層：vault 架構的結構性問題

### G8：vault 的底層邏輯與 Vortex 不相容

**問題**：

Vortex 的因果鏈：
```
感知建立 → 技術動作自然出現（輸出）→ 速度
```

Vault 目前的邏輯：
```
技術動作（物理層）→ 文獻驗證
↑
這個方向是「由外而內」
```

Vault 把「技術動作」當作起點和終點，水感是附帶指標。但 Vortex 的出發點是感知——技術動作是感知的輸出，不是輸入。

**這不是文件缺失的問題，是框架方向的問題。**

如果 vault 要成為教練可用的知識庫，這個邏輯需要一個明確的定位：
- 若定位是「技術動作參考手冊」→ 現有架構夠用，但名稱不應叫「游泳研究」
- 若定位是「水感教學系統」→ 需要感知層整合，邏輯需要翻轉

---

### G9：缺少「教練工具」層

Vortex 的分層設計，最終是為了讓教練在 poolside 能用：

```
物理層（Instructional）    → 教練理解「為什麼」
感知層（Technica）         → 教練知道「感覺什麼」
橋接層（Bridge）           → 教練說什麼「語言」
誤區深探（Instructional/誤區）→ 教練避免「說錯」
觀察層（Observations）      → 教練記錄「看見什麼」
```

Vault 目前只有物理層。**沒有橋接層和誤區層，教練即使讀了 vault，也沒有足夠的語言工具在 poolside 使用。**

---

### G10：`swimming/RAW/` 的標題格式不一致

RAW 有兩種標題格式：
```
YYYY-MM-DD-forum-reddit-r-swimming.md      ← 年月日前綴（論壇digest）
PMID-41021363-lumbar-spine-injuries-swimmers.md  ← PMID前綴（文獻）
```

而 ARCHITECTURE.md 規定的命名規範：
- PubMed：`PMID-{pmid}-{short-title}.md` ✅ 符合
- Forum：`YYYY-MM-DD-forum-{source}.md` ✅ 符合

但子目錄內的 research summary 命名不統一：
```
analogy-implicit-learning/SUMMARY.md
mechanoreceptor-forearm/SUMMARY.md
swimming-mechanoreceptor-adaptation/SUMMARY.md  ← 主題含dash
tactile-transfer/SUMMARY.md
vagus-diaphragm-swimming/SUMMARY.md            ← 主題含dash
```

ARCHITECTURE.md 規定子目錄內的 research summary 為 `SUMMARY.md`（統一），这点有遵守。

**但有一個問題**：forum digest 和文獻沒有被計入 swim-specific topics。詳見 G11。

---

### G11：RAW 主題覆蓋嚴重不均

| Vortex 主題 | vault RAW 狀態 |
|---|---|
| 渦流回收 | 🔴 無對應文獻 |
| 推進力理論 | 🔴 無 |
| 自然頻率/划頻優化 | 🔴 無 |
| 彈性蓄能 | 🔴 無 |
| 機械感受器（基礎） | ✅ `swimming-mechanoreceptor-adaptation/SUMMARY.md` |
| 觸覺遷移 | ✅ `tactile-transfer/SUMMARY.md` |
| 迷走神經/橫膈膜 | ✅ `vagus-diaphragm-swimming/SUMMARY.md` |
| 隱性學習/類比指令 | ✅ `analogy-implicit-learning/SUMMARY.md` |
| 前臂感受器密度 | ✅ `mechanoreceptor-forearm/SUMMARY.md` |
| 腰椎受傷 | ✅ `PMID-41021363` / `PMID-42127379` |
| 生物成熟度 | ✅ `PMID-42028723` |
| 教練倦怠 | ✅ `PMID-burnout-Chinese-swimmers-2026` |
| 水下動作監測 | ✅ `PMID-swimming-motion-TENG-42111162` |
| Jerk cost | ✅ `PMID-41734092` |
| 核心訓練 | ✅ `PMID-42135915` |

**核心物理現象完全空白**：渦流回收、推進力理論、自然頻率、彈性蓄能——這些是 Vortex 的物理層骨幹，但 vault 沒有對應的文獻支撐。這導致 vault 的技術動作章節有物理描述，但缺乏文獻淵源。

---

## 第四層：技術債

### G12：無 cron job 維護 RAW → insights 的轉換

ARCHITECTURE.md 規定 `swimming-weekly-digest` skill 每週執行，但此 skill 不存在。vault 的生長是断断续续的，不會随時間自動累积洞察。

### G13：論壇摘要的 HTML 残留

forum digest 檔案（如 `2026-05-23-forum-reddit-r-swimming.md`）含有未清除的 HTML 標籤残留（`!-- SC_OFF --`、`</p>`、`<a href=`）。這些干擾閱讀，也代表 forum 監控的抓取/清理流程不够乾淨。

---

## 優先級與行動建議

### P0 — 立即修復（ARCHITECTURE 破壞）

| 行動 | 影響 |
|---|---|
| 建立 `swimming/insights/` 目錄 | ARCHITECTURE 合規 |
| 建立 `swimming-weekly-digest` skill + cron job | 讓 vault 有時間軸的知識累積 |

### P1 — 核心缺口（框架完整性）

| 行動 | 影響 |
|---|---|
| 整合感知層（Technica/）→ `swimming/感知框架.md` | 補完 Vortex 核心——解決 G8 的邏輯不相容 |
| 整合 Bridge/（感知橋接） | 讓技術骨幹可轉換為 poolside 教練語言 |
| 整合教學誤區深探（6式） | 直接支撑教練實務 |

### P2 — 實用性補充（教練工具層）

| 行動 | 影響 |
|---|---|
| 整合 Observations/ | 教學案例現場記錄，直接可用於 practice plan |
| 補渦流回收文獻至 RAW | 物理層的文獻基礎，目前完全空白 |
| 補推進力理論文獻至 RAW | 同上 |

### P3 — 技術優化

| 行動 | 影響 |
|---|---|
| 修復 forum HTML 残留 | 提升 RAW 閱讀品質 |
| 補齊仰泳/蛙泳文獻至 RAW（仰泳：旋轉幅度/疲勞；蛙泳：渦流/CFD/收腿） | 技術章節的文獻支撐 |

---

## 總結：Vault 的核心問題

**不是數量問題，是深度問題。**

Vault 的物理層整合做得很好（Section 1–5 完成），但：
1. 丢了 Vortex 的核心（感知層、橋接層）
2. 没有時間軸的知識累積機制（insights/ + cron）
3. 物理層的文獻支撐嚴重不足（渦流、推進力、自然頻率全空白）

**建議方向**：先把 P0（insights/ + cron）做起來，讓 vault 活起來。然後選一個方向深入——P1（感知+橋接）or P2（誤區+觀察）——但不要同時做，先集中火力。

---

*Gap Analysis 完成*
*Hestia — 2026-05-23*