---
_slug: 40-Resources-_mixed-explorations-2026-05-17-portcullis---Docker-的-Secret-Detection-Engine-原始碼分析
_vault_path: 40-Resources/_mixed/explorations/2026-05-17-portcullis---Docker-的-Secret-Detection-Engine-原始碼分析.md
title: portcullis — Docker 的 Secret Detection Engine 原始碼分析
date: 2026-05-17
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- docker
- keyword
- marker
- pattern
- portcullis
- regex
- rule
- secret
- talos
created: '2026-05-17'
updated: '2026-06-15'
status: budding
---

# portcullis — Docker 的 Secret Detection Engine 原始碼分析

**延續自**: [[2026-05-17-docker-agent-internals-hooks-defer-redact]], [[2026-05-17-docker-agent-yaml-schema-policy-enforcement]]

## 來源

- **Repo**: [docker/portcullis](https://github.com/docker/portcullis) (Apache-2.0, 1232972544)
- **定位**: Docker Agent pipeline 的 secret redaction library（獨立的 Go library，非 MCP Gateway 內嵌）
- **核心檔案**: `portcullis.go` (~120 lines), `rules.go` (~600+ lines), `aho.go` (~120 lines)
- **Provenance**: 規則源自 MIT-licensed `docker/mcp-gateway/pkg/secretsscan` → `aquasecurity/trivy/pkg/fanal/secret`，再擴展 AI/payment/infra tokens

---

## Per-Source Insights

### 1. 兩層過濾架構（Aho-Corasick + Regex）

這是 portcullis 最關鍵的設計決策：**不直接跑 regex**，而是先做一次便宜的 keyword 掃描。

```
Input → Aho-Corasick scan → kwMask (keyword bitset)
       → 每個 rule 檢查 kwMask & rule.kwBits
       → 只有匹配的 rule 才執行 regex
```

**Clean input 路徑效能**：
- Aho-Corasick 單次線性掃描，ascii case-folding 內建在 transition table 中（不需 to-lower pass）
- 若沒有任何 keyword 匹配 → 零 regex 執行 → `0 B/op, 0 allocs/op`
- kwMask 是 `[4]uint64`，overlap check 是單一 `&` 指令（branch-free）

**對 Talos 的意義**：`secret-leak-prevention` skill 目前是純 regex 線性掃描。加上 keyword pre-filter 層可以把常見 case（檔案中沒有 secret）的成本降到接近零。Python 有 `pyahocorasick` 可用。

### 2. kwMask — 固定大小 bitset

```go
type kwMask [4]uint64  // cap 256 keywords, currently ~225 in use

func (m *kwMask) overlaps(other kwMask) bool {
    return m[0]&other[0]|m[1]&other[1]|m[2]&other[2]|m[3]&other[3] != 0
}
```

設計意圖：
- 不 heap-allocate（array，非 slice）
- 256 keyword cap 是刻意限制——強制 rule 作者只用高特異性 keyword
- Overflow 會觸發 `panic`（編譯期可偵測）
- 每個 rule 有自己的 `kwBits` mask，scan 結果是 `found` mask，重疊檢查 = 單一 AND

### 3. `[REDACTED]` — Idempotent Marker

portcullis 的 redact 輸出用 `[REDACTED]` 取代敏感值。關鍵設計：**這個 marker 字串本身不匹配任何 rule 的 keyword**，因此 re-redaction 是 no-op。

```
原始: Authorization: Bearer sk-ant-api03-xxx...AA
第一次: Authorization: Bearer [REDACTED]
第二次: Authorization: Bearer [REDACTED]   ← no-op，不會變成 [[REDACTED]]
```

這對 Talos 很重要：目前的 `secret-leak-prevention` 如果同一份輸出被掃兩次，可能重複標記。應該採用同樣的 idempotent marker 設計。

### 4. `redactSpan()` — 保留 Context 標籤

```go
// 保留 named subgroup 外的文字
// 輸入: AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
// 輸出: AWS_SECRET_ACCESS_KEY=[REDACTED]
```

Regex rule 用 named subgroup (`(?P<secret>...)`) 標記要 redact 的部分，`redactSpan()` 只替換 subgroup 內容，保留周圍的 context 標籤。這讓 redacted 輸出仍然可讀（知道是哪個 provider 的 key），但值已被移除。

### 5. `contextual()` Helper — Gitleaks 風格錨定

```go
// (?i)[\w.-]{0,50}?(?:vendor_keyword)...body...
contextual("aws", `(?i)aws(.{0,20})?(?-i)['\"](?P<secret>...`)
```

設計：
- 在 secret pattern 前插入 vendor 關鍵字（`aws`, `stripe`, `github`）
- 允許 0-50 chars 的間距（覆蓋 `_SECRET_ACCESS_KEY=` 之類的 label）
- case-insensitive vendor match
- 大幅降低 false positive（不會把 random base64 字串誤判為 AWS key）

這是 gitleaks 的核心技巧，portcullis 將其標準化為 helper function。

### 6. LLM Provider Pattern 覆蓋

portcullis 為 AI provider 設計了高特異性 pattern：

| Provider | Pattern | 特異性來源 |
|----------|---------|-----------|
| OpenAI | `sk-[...]T3BlbkFJ[...]` | `T3BlbkFJ` = base64("OpenAI")，內嵌在 key body |
| Anthropic | `sk-ant-(api\|sid\|admin)\d{2}-[...]AA` | 固定 prefix + 108 char body + base64 padding |
| Google | `AIza[...]{35}` | 固定 prefix + 35 char body |
| Replicate | `r8_[...]{37}` | 固定 prefix |
| HuggingFace | `hf_[...]` | 固定 prefix |
| Notion | `ntn_[...]{46}` | 固定 prefix |

OpenAI pattern 最值得注意：利用 key body 內部固定出現的 `T3BlbkFJ`（base64 "OpenAI"）做為二次錨定，讓 regex 幾乎不可能 false positive。

### 7. 移除 Word Boundary Anchor

portcullis 刻意**不使用** `\b` anchor：

```go
// 註解: "Removing the word-boundary anchor lets the rule catch
// secrets embedded inside larger tokens (BEFOREghp_...AFTER)"
```

這是有意的設計取捨：寧可多一些 false positive（可事後 audit），也不要漏掉被 concatenation 或奇怪字元包圍的 secret。Talos 目前有些 pattern 用 `\b`——應評估是否跟進。

---

## 跨文章 Synthesis

### Docker Agent 生態系的 Defense-in-Depth

三篇筆記形成一個完整的安全鏈：

1. **policy enforcement**（`docker-agent-yaml-schema-policy-enforcement`）— Docker Agent 的 YAML schema 定義了 agent 能做什麼的**事前約束**
2. **hooks/defer/redact**（`docker-agent-internals-hooks-defer-redact`）— 執行期的生命週期 hook，在 tool output 回傳 LLM 前攔截
3. **portcullis**（本篇）— 攔截層的具體實作：用兩層過濾做到零 overhead secret detection

這三層對應的 Talos governance pipeline blueprint 已經在 `references/talos-governance-pipeline-blueprint.md` 中有骨架。portcullis 的分析補上了**執行層的具體演算法選擇**（Aho-Corasick + idempotent marker + context preservation）。

### 從 Regex-Only 升級到 Two-Layer 的邊際成本

Talos 目前 `secret-leak-prevention` skill 是純 regex。portcullis 顯示的升級路徑：

| 項目 | 現狀 (Talos) | 目標 (portcullis-style) | 成本 |
|------|-------------|------------------------|------|
| Pre-filter | 無 | Aho-Corasick keyword scan | 加 `pyahocorasick` dep；rule 需定義 keywords |
| Idempotency | 無保證 | `[REDACTED]` marker 不匹配任何 keyword | 改 marker 字串 + keyword 審計 |
| Context preservation | 全行 redact | `redactSpan()` 只替換 named subgroup | regex rule 重寫（加 `(?P<secret>...)`） |
| False positive 控制 | `\b` anchor | `contextual()` vendor-anchored templates | rule 重寫；需收集 vendor 關鍵字 |

實際遷移可以漸進：先加 Aho-Corasick pre-filter（不改 rule），再逐步升級 rule 格式。

### Governance Pipeline 的 Secret Detection 層定位

在 Talos governance pipeline（`references/talos-governance-pipeline-blueprint.md`）中，secret detection 屬於 **Pre-LLM Output Sanitization** 層（對應 Docker Agent 的 `defer redact` hook）。portcullis 證明這一層可以做到：
- 零 overhead（clean input 0 allocs）
- 不能繞過（所有 tool output 必經此層）
- Idempotent（re-redaction safe）

---

## Hermes 啟發

1. **`secret-leak-prevention` skill 升級方向明確**：Aho-Corasick pre-filter + idempotent marker + context preservation。不需要從零設計，可以直接參考 portcullis 的 architecture。

2. **256 keyword cap 是好的約束**：強制 rule 作者只用高特異性 keyword。Talos 目前的 pattern 有些 prefix 太短（如 `sk-`）——應該學 portcullis 用 `T3BlbkFJ` 這種 body-internal marker 提高特異性。

3. **Python 可行性**：`pyahocorasick` 是成熟庫（C extension，效能接近 Go 版本）。`kwMask` bitset 用 Python `int` 的 bitwise ops 可以做到同樣的 branch-free overlap check。

4. **規則來源的可持續性**：portcullis 的規則從 Trivy 繼承，Trivy 從 gitleaks 繼承。Talos 可以直接 consuming portcullis 的 rules.go 做為 upstream pattern source（Apache-2.0 license 允許），減少自行維護成本。

5. **`[REDACTED]` marker 設計可立即採用**：不需要等整個 pre-filter 架構完成。先改 marker、審計現有 keyword 確保 idempotent，是零風險的改進。

---

## 未追蹤 Leads

- https://github.com/docker/portcullis — 追蹤未來新增的 provider pattern（目前仍在 active development）
- https://github.com/docker/mcp-gateway/tree/main/pkg/secretsscan — portcullis 的 upstream source，可能有 portcullis 尚未 port 的 pattern
- `pyahocorasick` Python 套件 — 評估 API 相容性與效能
- gitleaks `config/gitleaks.toml` — portcullis 的規則來源之一，可 cross-reference 找 portcullis 遺漏的 pattern

## ✅ 本次探索完成

