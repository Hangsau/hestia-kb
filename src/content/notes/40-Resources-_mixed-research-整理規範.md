---
_slug: 40-Resources-_mixed-research-整理規範
_vault_path: 40-Resources/_mixed/research/整理規範.md
title: 研究資料整理規範
created: '2026-05-23'
updated: '2026-06-15'
type: research
tags: []
status: budding
---

# 研究資料整理規範

## 資料夾結構

```
research/
├── agent/              # Agent 框架與整合知識
│   ├── agent-knowledge-map.md     # 閱讀導覽（入口）
│   ├── agent-core-concepts.md    # 核心洞察整合層
│   └── framework/                # 框架文件（hermes-agent-framework, openclaw-vs-hermes 等）
├── reports/            # 深度研究報告（年份排序）
├── insights/          # 每日 consolidated insights（月份子目錄）
│   ├── 2026-05/
│   └── 2026-04/
├── spikes/            # 一次性探索文件（驗證概念用，不進入整合層）
└── swimming/          # 游泳技術文獻
    ├── RAW/           # 英文原文（PubMed abstract、forum 摘要）— 不翻譯
    ├── references/   # 搜尋紀錄、補充資料
    ├── threads/      # 論壇討論串
    └── 四式技術動作.md   # 唯一中文整合層（教練實務應用 + 文獻對照表）
```

## 分類原則

| 類型 | 放哪裡 | 例子 |
|---|---|---|
| 整合入口（地圖 + 核心結論） | `agent/` | `agent-knowledge-map.md`, `agent-core-concepts.md` |
| 深度研究報告（有結構的長文） | `reports/` | `研究報告-*.md` |
| 每日產出的 consolidated insight | `insights/YYYY-MM/` | `2026-05-23-1500-hermes-consolidated-insight.md` |
| 驗證性一次性文件（試錯誤區、概念驗證） | `spikes/` | `spike-001-*.md`, `hermes-pipe-mode-spike.md` |
| 框架文件（介紹、功能說明） | `agent/framework/` | `hermes-agent-framework.md` |
| 原始英文文獻 | `swimming/RAW/` | `pmid-*.md`, `forum-*.md` |
| 技術整合（中文、含結論與應用） | `swimming/四式技術動作.md` | — |

## 命名慣例

- **Consolidated insights**: `YYYY-MM-DD-HHMM-*-consolidated-insight.md`
- **研究報告**: `YYYY-MM-DD-研究報告-{主題}.md`
- **游泳 RAW**: `YYYY-MM-DD-pmid-{PMID}.md` 或 `YYYY-MM-DD-forum-{source}.md`
- **整合文件**: 中文，說明性標題（如 `四式技術動作.md`）

## 游泳文獻特殊規則

- `RAW/` 內放英文原文，不翻譯
- `四式技術動作.md` 是**唯一中文整合層**，教練實務應用、層次對照表寫在這裡
- 仰泳、蛙泳若無文獻則留空白，並主動檢索補充，不得長期殘缺

## 新增檔案時

1. 依上表判斷放哪個子目錄
2. 符合命名慣例
3. 若是游泳相關：進 `swimming/RAW/` 的檔案，同時在 `四式技術動作.md` 的對應位置加上 cross-reference
4. 若是 agent 重大發現：同步更新 `agent-core-concepts.md` 的相應領域（M1–M5）
