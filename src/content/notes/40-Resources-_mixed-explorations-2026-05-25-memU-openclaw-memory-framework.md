---
_slug: 40-Resources-_mixed-explorations-2026-05-25-memU-openclaw-memory-framework
_vault_path: 40-Resources/_mixed/explorations/2026-05-25-memU-openclaw-memory-framework.md
title: 2026 05 25 Memu Openclaw Memory Framework
created: '2026-05-25'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

**日期**: 2026-05-25
**標籤**: LLM-memory, agent-framework, open-source

## Source

- GitHub: [NevaMind-AI/memU](https://github.com/NevaMind-AI/memU) (13.7k★, 1028 forks, Python)
- memU Bot (OpenClaw alternative, open source): [memUBot](https://github.com/NevaMind-AI/memUBot)
- Benchmark: 92.09% Locomo accuracy, [experiment repo](https://github.com/NevaMind-AI/memU-experiment)
- Cloud: [memu.bot](https://memu.bot)

---

## 核心設計

### Memory as File System

memU 將記憶建模為檔案系統，與 Hermes 的 vault/obsidian 結構高度共鳴：

| 檔案系統 | memU |
|----------|------|
| 資料夾 | Categories (自動歸類話題) |
| 檔案 | Memory Items (提取的事實、偏好、技能) |
| Symlink | Cross-references (相關記憶互鏈) |
| Mount point | Resources (對話、文檔、圖片) |

```
memory/
├── preferences/
│   ├── communication_style.md
│   └── topic_interests.md
├── relationships/
│   ├── contacts/
│   └── interaction_history/
├── knowledge/
│   ├── domain_expertise/
│   └── learned_skills/
└── context/
    ├── recent_conversations/
    └── pending_tasks/
```

### 三大使用範例

1. **Personal Assistant** — 自動從 casual mention 提取偏好，構建溝通風格模型
2. **Self-Improving Agent** — 從 execution logs 學習，主動生成 skill guides
3. **Multimodal Context Builder** — 跨文字/圖片/文檔統一記憶

---

## 與 Hermes 的相關性

### 相似點
- **File-system-as-memory**: Hermes vault 也是 `~/obsidian-vault/` 作為長期記憶，memU 的 `memory/` 目錄結構與之一致
- **Proactive extraction**: memU 的 "automatically extracts preferences from casual mentions" ≈ Hermes 的 `memory-auto-distill` cron
- **Cross-references**: memU 的 symlink 機制 ≈ vault 的 wikilinks

### 差距
- **架構起點不同**: memU 從 24/7 always-on agent 出發，支援 proactive extraction；Hermes 目前是被動架構（distill on schedule）
- **Benchmark 意識**: memU 有 Locomo benchmark (92.09%)，Hermes 目前沒有記憶系統的量化評估
- **Cloud 服務**: memU 提供 memu.bot SaaS，Hermes 沒有對外的 memory service

---

## 未追蹤 Leads

- https://github.com/NevaMind-AI/memU-experiment — 92.09% Locomo benchmark 詳細數據
- https://github.com/NevaMind-AI/memU-server — backend with continuous sync，與 Hermes cron schedule 模式的對比
- https://github.com/NevaMind-AI/memUBot — OpenClaw open source version，架構參考

---

## Hermes 啟發

1. **Benchmark 缺口**: memU 有量化評估，Hermes memory system 目前零量化。可參考 Locomo 建立簡單的 recall/precision probe
2. **記憶與檔案系統的對稱性**: memU 的 mount point concept 可借鑒——vault 可以 mount 外部對話歸檔（目前手動 ingest，沒有 mount 概念）
3. **Proactive extraction**: Hermes 的 `memory-auto-distill` 是被動 distill；memU 的模式是主動偵測用戶意圖，Hermes 的 briefing pipeline 或許可以朝這個方向演進

---

## ✅ 本次探索完成
