---
_slug: 30-Areas-swimming-00-游泳知識庫-index
_vault_path: 30-Areas/swimming/00-游泳知識庫-index.md
title: 游泳知識庫 INDEX
created: '2026-06-01'
updated: '2026-06-15'
type: swimming
tags: []
status: budding
---

# 游泳知識庫 INDEX

> 建檔：2026-06-01
> 用途：整體導覽 + 內容地圖

---

## 核心理念

**技術動作是感知系統的輸出。** 當水感建立，動作自然趨近正確。

本知識庫只談**物理層事實**（力學、能耗、生理限制）+ **教練圈共識**，感知框架（L0-L6 水感發育地圖）尚未納入——這是最大缺口。

**證據標記系統：**
- 🟢 文獻可驗證（文字可直接對應 abstract）
- 🟠 教練圈共識（教練社群觀測歸納，無直接文獻）
- 🔵 物理推導（連動鏈分析，非實證結論）

---

## 架構總覽

```
swimming/
├── 00-游泳知識庫-index.md          ← 你在這裡（索引/入口）
├── SWIMMING-游泳技術手冊.md         ❌ 已廢除（內容已整合至四式技術動作.md）
├── insights/
│   └── 游泳知識庫總覽.md            ✅ 改造完成（物理層補充 + 快速索引）
├── technique/
│   ├── 四式技術動作.md              📖 主要知識庫（最完整）
│   ├── 教學誤區-自由式.md            📚 自由式23條誤區（來源：Vortex）
│   └── [其他技術專檔]               📚 各泳式補充
├── RAW/
│   ├── [PMID-XXXXX-原始文獻].md     📖 88篇原始文獻（abstract）
│   ├── vortex-recovery.md           🔬 渦流回收理論
│   ├── propulsion-theory-evolution.md 🔬 推進力理論演變
│   ├── natural-frequency-swimming.md 🔬 自然頻率
│   └── elastic-energy-storage.md   🔬 彈性蓄能
└── digests/
    └── [PMID-動物游泳-digest].md    📚 50篇生物游泳對比文獻
```

---

## 閱讀路徑建議

### 🚀 快速了解（30分鐘）
→ `insights/游泳知識庫總覽.md`

### 📖 完整學習（2-4小時）
→ `technique/四式技術動作.md`

### 🔬 深入某個物理現象
| 主題 | 來源 |
|------|------|
| 渦流推進機制 | `RAW/vortex-recovery.md` |
| 推進力理論演變 | `RAW/propulsion-theory-evolution.md` |
| 自然頻率與划頻 | `RAW/natural-frequency-swimming.md` |
| 彈性蓄能 | `RAW/elastic-energy-storage.md` |

### 📚 文獻依據（88篇）
→ `RAW/[PMID-XXXXX].md`

---

## 主要知識內容（2026-06-01 整理）

### 四式技術

| 泳式 | 核心重點 | 疲勞崩潰序列 |
|------|---------|------------|
| 自由式 | SR×SL 公式 · EVF 物理 · 旋轉槓桿 · 踢水減阻 | 前鋸肌→EVF崩潰→划距下降 |
| 仰式 | 旋轉是功能需求（49°+）· 出發/轉身佔1/3 | 髖旋轉→踢水退化→直線划水 |
| 蛙式 | 渦流噴射推進· insweep峰值· 速度谷值管理 | insweep消失→滑行縮短→收腿路徑偏移 |
| 蝶式 | 波動能量傳遞鏈·兩踢時序不對稱 | 第二踢→空中Recovery→波動鏈斷裂 |

### 出發與轉身（佔短距離1/3）
- 起跳：窄腳位優於寬站 · 角度 27°（菁英）vs 40°（非菁英）
- 水下滑行：深度 −0.92m 最優 · 水下收腿阻力更小
- WCT：太短反而更差 · 最優 Tuck Index = 0.7

### 呼吸做功（被低估的疲勞源）
- 75 L/min 通氣量時，呼吸做功比自行車高 +56 J/min
- 屏氣冲泉更快（呼吸税真實存在），但需監控

### 損傷預防
- 游泳肩：發生率 35–91% · 疲勞鏈追蹤
- 下背疼痛：椎間盤壓力 + 核心穩定性
- 青少年：Jerk cost 可區分表現 · 生物年齡比時序年齡重要

---

## 已知缺口

1. **最大缺口：感知框架** — L0-L6 水感發育地圖（Vortex上層）尚未進入vault
2. **文獻缺口**：「swimming feel for water proprioception」+「implicit learning swimming」

---

## 更新日誌

| 日期 | 動作 |
|------|------|
| 2026-05-31 | 初建，消化80篇文獻 |
| 2026-06-01 | 整合判斷：廢除重複手冊，改造總覽為物理層補充，完善地圖 |
