---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-19-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-19-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-19'
confidence: high
title: Agent Enforcer 的三種執行模式
updated: '2026-06-15'
type: research
status: budding
---

# Agent Enforcer 的三種執行模式

**消化筆記**: docker-agent-yaml-schema-policy-enforcement, docker-credential-governance-injection-proxy, jido-circuit-finder, portcullis-secret-detection-engine, zerostack-doom-loop-source-analysis, agent-orchestration-zenflow-opik

（6 篇筆記從不同角度探索 agent 安全治理，歸納出 enforcement 的三種執行哲學，而非統一的 policy rule 框架。）

## Cross-Cutting Theme 1: Enforcement 不等於 Prohibition — 三種執行模式

**支援筆記**: docker-agent-yaml-schema-policy-enforcement, docker-credential-governance-injection-proxy, jido-circuit-finder, portcullis-secret-detection-engine

單看各篇，這些筆記各自記錄了不同 enforcement 技術。但擺在一起，浮現一個結構性的分類：**enforcement 的「位置」決定了它的能力邊界，不是「強度」。**

| 模式 | Docker 代表 | Jido 代表 | 核心邏輯 |
|------|------------|----------|---------|
| **Policy Rule**（禁止/允許） | `permissions.yaml`（deny/allow/ask）| — | 「你不能這樣做」，enforcement 在決策前 |
| **Mediation**（指令轉譯） | — | `pure agent + directive` model | 「你要做的事我轉成安全版本再執行」 |
| **Injection**（代理注入） | HTTP proxy injection（credential） | — | 「你根本看不到那個 secret」 |
| **Detection + Response**（偵測反應） | portcullis（secret redaction） | — | 「你已經做到了，我來修補」 |

Policy Rule 是最常見的框架（也是 `guardian_policy.yaml` 草案採用的），但單靠它是不足的。Credential 的 injection proxy 揭示了為什麼：`deny: "web:api.github.com"` 無法阻止 agent 看到寫在 log 裡的 GitHub token。Prohibition 做不到 injection 能做到的事。

Jido 的 directive model 補上了第二層：不是「不准做」，是「你說的翻譯成安全版本再做」。Agent 仍然有主動性，但執行路徑經過 mediated。

**可行動下一步**: 將 `guardian_policy.yaml` 草案從純 YAML policy rule 擴展為三層 enforcement 宣告文件：
```yaml
enforcement:
  rules:        # Policy Rule layer — deny/allow/ask
  directives:   # Mediation layer — Talos transforms dangerous calls  
  injection:    # Injection layer — sentinel values for sensitive data
```

## Cross-Cutting Theme 2: 雙層閘道模式 — 便宜預篩 gate 昂貴核心

**支援筆記**: portcullis-secret-detection-engine, zerostack-doom-loop-source-analysis, agent-orchestration-zenflow-opik

portcullis 的 Aho-Corasick + regex 雙層、Zerostack 的 sliding window + threshold detection——看起來是不同的領域（secret detection vs loop detection），但結構完全相同：

```
預篩層（O(n), 低成本）→ 符合條件才啟動核心（O(n²) 或更高）
```

Opik 的 trace → evaluate → optimize 流程也有這個模式：便宜的 trace 先做，昂貴的 evaluation 只在需要時觸發。

這個模式的共同設計原則：
1. 預篩層使用資料結構優化（Aho-Corasick 的 transition table、sliding window 的 ring buffer）
2. 預篩層有明確的 negative path（Aho-Corasick 無匹配 = 0 allocs；window 未觸發 threshold = no response）
3. 核心層的 threshold 是經驗值，不是理論最優

對 Hermes 的具體應用：

| 位置 | 預篩層 | 核心層 |
|------|--------|--------|
| `secret-leak-prevention` skill | Aho-Corasick keyword scan（0 allocs on clean） | regex 完整比對 |
| heartbeat doomer detection | sliding window tracking | full session replay analysis |
| skill loading | 參數 hash 比對 | 全量 skill code parse |
| WUPHF pipeline | query complexity estimate | full LLM evaluation |

**可行動下一步**: 在 `guardian_policy.yaml` 中為 `secret-leak-prevention` 加上雙層模式宣告：
```yaml
secret_detection:
  prefilter: aho_corasick   # keyword bitset, near-zero on clean input
  core: regex               # only on prefilter hit
  idempotent_marker: "[REDACTED]"
```

## 備註：為何跳過「明顯重複」

這些筆記之間有幾個看似相關但實際是內部重複的主題，未納入 cross-cutting 分析：
- Zenflow 和 Jido 的 multi-agent pattern——都有「pure agent + mediation」，但 Zenflow 是 build-time workflow、Jido 是 runtime architecture，維度不同而非 cross-cutting
- Docker credential 和 filesystem 都用了 allow/deny——這只是同一實作（YAML schema）在不同資源類型的應用，不是新的 pattern