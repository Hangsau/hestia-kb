---
_slug: 30-Areas-learnings-2026-05-28-Psyche-Cron-Filesystem-View-Mismatch
_vault_path: 30-Areas/learnings/2026-05-28-Psyche-Cron-Filesystem-View-Mismatch.md
tags:
- psyche
- cron
- financial-research
- architecture
- pitfall
source: psyche/sessions/20260527_090844
created: '2026-05-28'
title: Psyche Cron 環境問題：Filesystem 視角不一致
updated: '2026-06-15'
type: learning
status: budding
---

# Psyche Cron 環境問題：Filesystem 視角不一致

## 問題

每日市場掃描 cron job (`f582732354ea`) 執行時，工作目錄可能與用戶 terminal 不同，導致：
- `git push` 成功（無錯誤）
- 但寫入位置並非預期目錄（`/tmp/financial-expertise/`）
- Cron agent session 看不到用戶当前 terminal 的實際目錄狀態

## 觀察而來的事實

- Cron agent 每次執行是**獨立 session**，filesystem 視角與用戶不同
- Git 操作不會失敗，但寫入位置可能錯
- 解決方案：設定 `workdir: /tmp/financial-expertise` 或讓 cron 直接跑 script 而非 LLM agent

## 相關工作階段

- `20260527_090844_67b0d6f3.jsonl` — 每日市場掃描，cron job 架構問題
- `20260527_095104_94c168.jsonl` — 美國債券分析輸出
- `20260526_222007_6cf928.jsonl` — 框架驗證，市場數據格式標準化

## 狀態

- [ ] 待修復：Cron workdir 問題