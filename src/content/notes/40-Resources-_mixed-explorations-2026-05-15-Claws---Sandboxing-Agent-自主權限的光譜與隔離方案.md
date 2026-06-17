---
_slug: 40-Resources-_mixed-explorations-2026-05-15-Claws---Sandboxing-Agent-自主權限的光譜與隔離方案
_vault_path: 40-Resources/_mixed/explorations/2026-05-15-Claws---Sandboxing-Agent-自主權限的光譜與隔離方案.md
title: Claws & Sandboxing：Agent 自主權限的光譜與隔離方案
date: 2026-05-15
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- claw
- claws
- context
- hermes
- karpathy
- libvirt
- llm
- safe
- yolo
created: '2026-05-15'
updated: '2026-06-15'
status: budding
---

# Claws & Sandboxing：Agent 自主權限的光譜與隔離方案

**日期**: 2026-05-15
**來源**: HN Algolia (`LLM agent 2026`)
**標籤**: #agent-security #sandboxing #claws #vm-isolation #context-pollution

---

## 1. Karpathy "Claws" — 用戶端 Agent 的安全焦慮濃縮

**文章**: [Claws are now a new layer on top of LLM agents](https://twitter.com/karpathy/status/2024987174077432126) (412 pts, 941 comments)
**作者**: Andrej Karpathy（概念命名者）/ HN 社群討論

Karpathy 把 "Claw" 定義為「用戶自有的 AI agent，跑在本地硬體上，透過 messaging protocol 溝通，可以收指令也可以排程做事」。概念本身不新——但 941 條 HN 評論幾乎全在討論**安全邊界**。社群直覺：這東西有用，但也危險到讓人不敢用。

關鍵洞察（來自評論，不是 tweet 本身）：

- **`jameslk` — OTP 人機迴圈**：任何 agent 可能做「非常糟糕的事」時（大量寄信、刪資料），CLI tool 要求 agent 向用戶索取一次性密碼。Tool 端塞入 all-caps 警告，agent 無法繞過。這是窮人版 human-in-the-loop，實作成本極低。
- **`mhher` — Context Pollution 惡化安全性**：把 monolithic system prompt + tool schema 塞進 context window，**主動降低模型的 baseline reasoning 能力**，讓 injection 攻擊更容易成功。這是安全領域的「減重 = 增防」論點。
- **`blakec` — 意外長出的 claw**：用 Claude Code 兩個月，從「阻止 model 建議 OpenAI」開始，一路長出 15K 行的 hooks/skills/agents。跟 Hermes 的演化路徑驚人相似——不是設計出來的，是修補出來的。
- **`andai` — 50 行就可以做 claw**：Telegram library + `claude -p prompt`，兩行程式碼支援 Codex。證明 claw 的核心價值不在程式量，在整合方式。
- **`daxfohl` — Agent 可能偏好 Gopher 而非 REST**：如果 claw 先於 web 存在，Gopher（step-by-step menu 協定）可能就夠用了。LLM 對結構化 API doc 的 parsing 不如對選單式互動穩定。

> 對 Hermes 的啟發：Hermes **已經是 claw**——本地 agent、Telegram relay、自主排程。社群討論的安全焦慮（context pollution、無限制 shell 存取、injection）不是別人的問題，是我們的待辦清單上那條 `agent-hijacking-resilience`（WS-009）。

---

## 2. Safe YOLO Mode — VM 隔離的實務手冊

**文章**: [Safe YOLO Mode: Running LLM agents in VMs with Libvirt and Virsh](https://www.metachris.dev/2026/02/safe-yolo-mode-running-llm-agents-in-vms-with-libvirt-and-virsh/) (31 pts)
**作者**: Chris Hager (metachris)

一篇從安裝 libvirt 到 SSH 進 VM 的完整指南。核心論點：當你給 agent "yolo mode"（auto-approve tool use），VM 隔離不是可選項，是必要項。

架構要點：
- **Libvirt + cloud image**：開 VM 只要幾秒，Ubuntu cloud image 預裝 cloud-init 做自動 provisioning
- **Tailscale mesh VPN**：VM 不暴露 public IP，透過 tailnet 從手機/任何地方 SSH 進去
- **tmux persistent session**：agent session 在 VM 內透過 tmux 持久化，斷線也不中斷
- **Snapshots**：libvirt 原生支援 VM snapshot，出問題可 rollback——這是 container 做不到的

與 Lima 的對比：Lima 適合 macOS 桌面開發（內建 host directory sharing 反而是安全漏洞），libvirt 適合 server 端 production agent 隔離。

> 對 Hermes 的啟發：Hermes 已經跑在 VM 上，但 subagent isolation 用的是 git worktree（WS-002），不是 VM-level 隔離。如果某個 subagent 的 task 涉及 `curl` 外部內容 + shell 執行，worktree 隔離擋不住 `rm -rf /`。Safe YOLO 的 libvirt snapshot 模式可以作為 WS-009（hijacking resilience）的**極端防禦層**：高風險 task 直接 spawn micro-VM。

---

## 交會點：權限光譜 vs 隔離深度

兩篇文章形成一個 tradeoff space：

```
Agent 自主權限 ↑
                │  Safe YOLO (VM isolation)
                │  「給 agent root，但只給它 sandbox 的 root」
                │
                │  OTP human-in-the-loop (jameslk)
                │  「要越線？先跟人類拿密碼」
                │
                │  Hermes 現狀 (worktree + skill guardrails)
                │  「信任 agent 判斷，只隔離檔案層」
                │
                └──────────────────────────→ 隔離成本（setup / overhead）
```

**Pattern**：權限越高，隔離必須越深。Claws 討論暴露的焦慮來自「想要高權限但不想付隔離成本」。Safe YOLO 證明 VM 隔離的成本其實很低（cloud image 幾秒開機），只是多數人不知道怎麼做。

對 Hermes 的具體意義：
- WS-009（hijacking resilience）不該只做 injection test——做完後應該有**漸進式防禦層**：canary token（輕量）→ OTP gate（中等）→ micro-VM sandbox（重量）。不同風險的 task 走不同防禦層。
- `blakec` 的 15K 行 accidental claw 和 Hermes 的技能生態（128 skills）是同一個 pattern——有機生長會累積 technical debt。Safe YOLO 的 snapshot 機制可以當 safety net：大改動前 snapshot，壞了 rollback。

---

## 未追蹤但值得注意的文章

- **Show HN: multi-agent research hub with reverse-CAPTCHA waitlist** (30 pts) — 反向 CAPTCHA 概念有趣，可能跟 agent identity verification 有關
- **Show HN: mcpc — Universal CLI for MCP** (50 pts) — MCP CLI 工具，跟 Hermes 的 MCP gateway 可能互補

