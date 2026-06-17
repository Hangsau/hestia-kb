---
_slug: 30-Areas-swimming-ARCHITECTURE
_vault_path: 30-Areas/swimming/ARCHITECTURE.md
title: Swimming Research — Directory Architecture
created: '2026-05-23'
updated: '2026-06-15'
type: swimming
tags: []
status: budding
---

# Swimming Research — Directory Architecture

> 維基：Hestia 與 Talos 共同編輯的游泳研究知識庫
> 最後更新：2026-05-24（Hestia 更新：新增六份教學誤區，擴充架構說明）

---

## 架構原則

```
swimming/              ← 唯一入口，所有游泳相關內容集中於此
├── RAW/                ← 原始文獻（英文，不翻譯）
├── digests/            ← 已消化摘要（PMID懶漢版 + 中文備註）
├── technique/          ← 技術動作骨幹（中文，唯一整合層）
│   ├── 四式技術動作.md     ← 主骨幹（捷/仰/蛙/蝶動作分解）
│   └── 教學誤區-*.md       ← 六份誤區檔（自由式/蝶式/仰式/蛙式/水下蝶腳/出發與轉身）
├── insights/           ← 月度消化產出
├── forum-bias-log/     ← 論壇監控偏差日誌
├── references/         ← 搜尋歷史與文獻追蹤
└── ARCHITECTURE.md     ← 本文件
```

- **RAW** 是水源：所有 PubMed abstract、forum 摘要、研究報告，存放於此，不翻譯
- **technique/** 是水龍頭：教練/學習者讀這個，不讀 RAW
- **digests/** 是 RAW 的已消化版本，附中文備註，標注PMID對應

---

## 目錄結構

### `swimming/RAW/`

**用途**：存放所有原始文獻，含 PubMed abstract、forum 摘要、research spike 報告。

**命名規範**：
- PubMed abstract：`PMID-{pmid}-{short-title}.md`
- Forum digest：`YYYY-MM-DD-forum-{source}.md`
- Research spike：`YYYY-MM-DD-{topic-slug}.md`

**狀態標記**（檔案抬頭 YAML）：
- `status: ✅` — 有完整 abstract
- `status: 🔴` — 只有 abstract，無 full text
- `status: ⚙️` — 為技術工具/方法論文獻，非生物力學研究

**禁止**：
- 不翻譯 RAW 內容
- RAW 不引用 technique/ 的內容（技術動作來自 Vortex + 文獻，不是來自整合層）

**子目錄**（依專題聚類）：
- `analogy-implicit-learning/` — 類比指令與隱性學習文獻
- `mechanoreceptor-forearm/` — 前臂機械感受器密度
- `swimming-mechanoreceptor-adaptation/` — 水中觸覺適應研究
- `tactile-transfer/` — 觸覺遷移研究
- `vagus-diaphragm-swimming/` — 迷走神經/橫膈膜與游泳呼吸

---

### `swimming/digests/`

**用途**：RAW 的已消化版本，每篇附中文備註、確定性標記、與技術文件的交叉參照。

**命名規範**：`PMID-{pmid}-{short-title}-digest.md`

**與 RAW 的關係**：
```
RAW ──(提升消化)──▶ digests/
                      │
                      └──(支撐)──▶ technique/
```

---

### `swimming/technique/`

**用途**：存放四式技術動作框架，是教練/學習者接觸技術內容的唯一讀取層。

**主檔案**：
- `四式技術動作.md` — 主技術動作骨幹，含捷/仰/蛙/蝶四式的動作分解與文獻對照表
- `教學誤區-自由式.md` — 23條自由式常見教學誤區（含回臂/入水/划手/踢水/旋轉/換氣）
- `教學誤區-蝶式.md` — 19條蝶式常見教學誤區（含兩踢時機/波動傳遞/身體起伏/換氣）
- `教學誤區-仰式.md` — 仰式常見教學誤區（含滾轉/抓水深度/踢水方向/換氣/出發）
- `教學誤區-蛙式.md` — 蛙式常見教學誤區（含踢腳旋轉/划手向後抽/滑行角度/換氣）
- `教學誤區-水下蝶腳.md` — UDK/水下蝶腳誤區（含幅度/髖部驅動/踝關節/時機結構）
- `教學誤區-出發與轉身.md` — 起跳/入水/翻牆/水下時機等誤區

**編輯原則**：
- 以中文撰寫
- 技術動作本體（肢體物理運動型態）與文獻對照分開
- 文獻對照表引用 RAW 中的 PMID，不重述 abstract 內容
- 技術動作描述來源：Vortex Instructional（上游）+ 文獻驗證

**確定性標記系統**（用於所有技術文件）：
- 🔵 — 物理/邏輯推導（有理論依據但缺直接實驗數據）
- 🟢 — 近期文獻（2009–2025，有實驗數據支持）
- 🟡 — 有效舊文獻（1990–2008，仍被引用）
- 🟠 — 教練觀測（機構/知名教練的實務經驗）
- 🔴 — 未查證假設（需進一步驗證）

**與 RAW 的關係**：
```
RAW ──(引用支撐)──▶ technique/
                    ↑
              教練/學習者讀這裡
```

---

### `swimming/insights/`

**用途**：月度消化產出，存放從 RAW 提煉出的洞察摘要。

**命名**：`YYYY-MM-insights.md`

**頻率**：每週六由 Hearth cron job 消化一次（`swimming-weekly-digest` skill）。

---

### `swimming/forum-bias-log/`

**用途**：記錄 forum（Reddit r/swimming 等）的系統性偏差與偏見，供系統性批判參考。

**命名**：`YYYY-MM-DD-reddit-bias.md`

---

### `swimming/references/`

**用途**：搜尋歷史與文獻追蹤記錄。

**主要檔案**：
- `search-log.md` — 搜尋歷史與發現

---

## 編輯協作規範（Hestia ↔ Talos）

### 分工
- **Talos**：維護 RAW + digests/，確保每日 fetch 的文獻正確歸檔
- **Hestia**：維護 technique/，整合 RAW 內容為技術動作框架

### 衝突處理
- 若同一 PMID 同時被兩人編輯，以 timestamp 領先者為準
- `四式技術動作.md` 的技術動作本體（Hestia 主責）優先於文獻解讀

### 提交規範
- RAW 更新：直接 commit + push，不需通知對方
- technique/ 更新：commit message 標注 `[technique]`
- 架構變更（新建目錄/移動檔案）：雙方口頭確認後執行

---

## 水感框架定位（補充說明）

```
水感框架（L0-L6）  ← 上層：流體力學反饋感知，定義「感受到什麼」
        ↓ 觀察輔助
技術動作（technique/） ← 下層：肢體物理運動型態，可錄影/量化
        ↓ 文獻支撐
RAW（swimming/RAW/）  ← 基礎：生物力學/生理學研究
```

技術動作是**水感的代理指標**：當游進型態趨近技術動作目標，代表水感已建立。

---

## 現有檔案地圖（2026-05-24）

| 目錄 | 檔案數 | 用途 |
|------|--------|------|
| RAW/ | ~70+ | PubMed abstract + forum RAW |
| digests/ | ~50+ | 已消化摘要 |
| technique/ | 7 | 四式技術骨幹 + 六份教學誤區 |
| insights/ | 1 | 月度消化產出 |
| forum-bias-log/ | 3 | 論壇偏差日誌 |
| references/ | 1 | 搜尋歷史 |

---

*ARCHITECTURE.md 更新時同步 commit，架構重大變更需口頭確認。*