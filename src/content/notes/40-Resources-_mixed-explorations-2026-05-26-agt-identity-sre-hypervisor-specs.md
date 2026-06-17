---
_slug: 40-Resources-_mixed-explorations-2026-05-26-agt-identity-sre-hypervisor-specs
_vault_path: 40-Resources/_mixed/explorations/2026-05-26-agt-identity-sre-hypervisor-specs.md
title: AGT Identity + SRE + Hypervisor Specs — WS-035 Policy Engine SPIKE
created: '2026-05-26'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

**延續自**: [[2026-05-26-mcp-security-gateway-spec-deep-dive]]

# AGT Identity + SRE + Hypervisor Specs — WS-035 Policy Engine SPIKE

## 探索目標

驗證 WS-035 提案的三個 untracked leads，全數來自 microsoft/agent-governance-toolkit GitHub repo。
所有 URL 均活得（Phase 1 validation ✅）。

---

## Source 1: AGENTMESH-IDENTITY-TRUST-1.0.md（729 lines）

### 核心架構

**身份模型**：每個 agent 有一個 `did:mesh:<hex-id>`（128-bit），綁定 Ed25519 金鑰對與人類 sponsor email。沒有「孤兒 agent」——所有 identity 都追溯到一個驗證過的人。

**關鍵欄位**：
```
AgentIdentity {
  did: AgentDID                    # did:mesh:<hex>
  public_key: Ed25519              # base64 encoded
  sponsor_email: string             # 責任追溯
  status: active | suspended | revoked
  capabilities: list[string]
  parent_did: string?               # delegation chain
  delegation_depth: int
  max_initial_trust_score: int?     # Sybil resistance ceiling
}
```

**Trust Score Model**：0-1000 整數，五維 reward dimensions，自動 decay + 網路傳播。
- 初始分數是預設值，只有行為信號能移動它
- KL divergence 檢測「regime change」（行為突變）

**Trust Tiers**：verified_partner > trusted > standard > probationary > untrusted

**IATP（Inter-Agent Trust Protocol）**：Ed25519 challenge-response 握手，互相認證。支援 RFC 9334 新鮮性。

**Scope Chain（ delegation）**：
- 只能縮小，不能擴大（monotonic capability narrowing）
- 每次 delegation 設定 `trust_ceiling`（child 可達到的最大 trust score）
- hash chain integrity

**Human Sponsor Binding**：每個 agent 必須綁定一個 human sponsor。
- `sponsor_verified` flag：是否經過獨立驗證（email confirmation、SSO、org directory）
- 子 agent 繼承 parent 的 `sponsor_email`，確保 accountability chain 不斷

**Key Rotation**：用 Ed25519，rotation 需要舊 key 簽名的 `RotationProof`。

**Fail Closed**：任何 identity 或 trust 驗證失敗 → **deny**，不回退到 permissive default。

### Hermes 啟發

**WS-028 Autonomy Tracker 對應**：
- `did:mesh` 機制類似 Hermes 的 `agent_id` + `owner` 雙重標識
- Trust score decay 對應 autonomy_level 的「streak 衰減」概念
- `regime_change`（KL divergence）對應 `_DoomLoopTracker` 的「指紋漂移」檢測
- **差距**：Hermes 沒有實體的 identity document + cryptographic binding，只有 session-level 的 `owner` 欄位

**Policy Engine 整合**（WS-035）：
- `trust scores feed policy conditions`：AGT 的 `GovernancePolicy.allowed_tools[]` 可用 trust tier 決定
- `policy violations generate negative trust signals`：被抓到的 policy violation 降低 trust score，形成 feedback loop
- `Deny immutability invariant`（Policy Engine spec）= this identity spec 的 `Fail closed`

**Exploration Tool Scoping 對應**（`exploration-tool-scoping-gradient.md`）：
- `capabilities[]` 清單對應「可用的 tool sets」
- `trust ceiling` 對應「最大 scope 等級」
- Ring 3 (Sandbox) 的 `filesystem_writable: false, subprocess_allowed: false, max_concurrent_tools: 2` = 純 read-only exploration agent

**帳號責任鏈**：
- Hermes cron job 的 `owner` 欄位（hestia/talos）= AGT 的 `sponsor_email`
- 差別：Hermes 沒有 `sponsor_verified` 機制，cron job owner 只是字串，無密鑰驗證

---

## Source 2: AGENT-SRE-GOVERNANCE-1.0.md（1173 lines）

### 核心架構

**SLO Model**：
```
SLO {
  name: string
  indicators: SLI[]
  error_budget: ErrorBudget
  alert_manager: AlertManager?
  exhaustion_action: ALERT | FREEZE_DEPLOYMENTS | CIRCUIT_BREAK | THROTTLE
}
```

**SLI types**（`collect()` interface）：
- `TaskSuccessRate`：任務成功率
- `ResponseLatency`：響應延遲（percentile，NOT mean）
- `CalibrationDelta`：預測信心 vs 實際成功率之差（running aggregate of |mean_predicted_confidence - mean_actual_success_rate|）
- `ToolCallAccuracy`：tool call 準確率
- `DelegationChainDepth`：delegation 鏈深度

**Error Budget**：
```
burn_rate = actual_error_rate / allowed_error_rate
```
- burn_rate > 1.0 = 高於預期的錯誤消耗速度
- burn_rate >= 2.0 → WARNING alert
- burn_rate >= 10.0 → CRITICAL alert

**Circuit Breaker**：
```
CLOSED → OPEN: failure_count >= failure_threshold (default 5)
OPEN → CLOSED: manual only (force_close() / reset())
```
- HALF_OPEN state 有 wire-through 但**實際不使用**（Public Preview 限制）
- `is_available` 只有在 `state == CLOSED` 時 return True

**Chaos Engineering**：
- `Blast Radius`：控制在 [0.0, 1.0] 範圍內
- Fault types：latency, errors, timeouts, adversarial attacks
- 只在 staging 環境執行

**Golden Traces**：捕獲並標記為「預期正確」的執行 trace，用於迴歸測試。SHA-256 content hash 做 deduplication。

**Artifact Signing**：Ed25519 簽名 build artifacts + SBOMs。`SignatureBundle = {signature, public_key, artifact_hash, timestamp}`。

**Incident Detection**：自動從 reliability signals 創建 incident，SREWitness required for Ring 0。

**OTEL Integration**：標準化的 metrics + traces + spans，適用於所有 agent operations。

### Hermes 啟發

**Heartbeat SLO 映射**：
- `heartbeat_cron_ok_rate` = TaskSuccessRate（cron job 是否按時完成）
- `gateway_uptime` = 可用性 SLI
- `evolve_error_rate` = 從 `heartbeat_severity.json` 計算的真實錯誤率
- `cost_per_task` = Cost Anomaly SLI

**Circuit Breaker → `_DoomLoopTracker` 整合**（WS-035 實作路徑）：
- AGT circuit breaker：`failure_count >= 5` → OPEN → 隔離 agent
- Hermes `_DoomLoopTracker`：同一指紋連續 N 次 → escalation
- **整合點**：`_DoomLoopTracker` 觸發時，不只是發 Telegram，還應該「打開 circuit breaker」——即標記該 agent/fingerprint 為 suspended，直到手動 `force_close()`
- AGT 的 `force_close()` 需要人類介入（類似 Hermes 的「Human-in-the-Loop」OTP gate）

**Burn Rate Alert → Hermes Alerting**：
- Hermes 的 `[warning×N]` / `[critical×N]` 計數就是 burn rate 的近似
- WS-035 可正式建立 SLO：例如 `heartbeat_evolve_error_rate_SLO: 0.05`（每月不超過 5% critical events）
- Error budget exhaustion → `CIRCUIT_BREAK` 等於「停止 heartbeat 直到人工介入」

**CalibrationDelta SLI 對 Hermes Learning**：
- 預測信心（`followup_quality=2.0` 預測這次 cycle 會有實質產出）vs 實際（EVOLVE scoring）
- Hermes 的 `learnings_type_fix` 導致 `followup_quality` 永遠 = 1.0，修復後才能正確校準

**Artifact Signing → Hermes script integrity**：
- WS-034 的 `ToolFingerprint` + HMAC sidecar（WS-031）= Hermes 的 artifact signing
- SHA-256 hash chain = append-only audit log for script modifications

---

## Source 3: AGENT-HYPERVISOR-EXECUTION-CONTROL-1.0.md（724 lines）

### 核心架構

**Execution Rings**（4 層）：
| Ring | 值 | 名稱 | 描述 | Trust 門檻 |
|------|----|------|------|-----------|
| 0 | 0 | Root | 超visor配置。系統專用。需 SRE Witness。 | N/A |
| 1 | 1 | Privileged | 不可逆操作；full resource access | > 0.95 + consensus |
| 2 | 2 | Standard | 可逆操作；scoped resource access | > 0.60 |
| 3 | 3 | Sandbox | 唯讀操作；minimal access | default |

**Ring 0 永遠不可通過標準 API 取得**。需要 out-of-band SRE Witness attestation。

**Action Classification**：
```
if is_admin:          → Ring 0
elif reversibility == NONE and not is_read_only: → Ring 1
elif is_read_only:    → Ring 3
else:                 → Ring 2
```

**Resource Constraints per Ring**：
| Ring | Network | FS | Subprocess | Max Tools |
|------|---------|-----|------------|-----------|
| 0 | Yes | full | Yes | 32 |
| 1 | Yes | full | Yes | 16 |
| 2 | Yes (allowlist) | scoped | Yes | 8 |
| 3 | **No** | **none** | **No** | **2** |

**Privilege Elevation**：
- `elevate(target_ring, ttl_seconds, attestation?)`
- Ring 1 需 `>= 0.85` trust + sponsor attestation
- Ring 2 需 `>= 0.50` trust
- Default TTL: 300s (5 min)，Max: 3600s (1h)
- 過期自動 revoke

**Session Model**：
- `Session { id, consistency_mode, participants[], audit_trail }`
- Consistency modes：`TERMINATED | ISOLATED | CONSISTENT | LINEARIZABLE`
- 參與者需要 `present` 才能執行操作

**Kill Switch**：
- `kill(agent_id, reason, handoff?)`
- `handoff`: step 交接（compensation），避免中斷造成不一致
- 需要 SRE Witness for Ring 0

**Quarantine**：臨時隔離惡意 agent，與外界隔離但不立即終止。

**Hash Chain Audit**：
- 所有 session 操作形成 SHA-256 hash chain
- `previous_hash` 確保 tamper-evident
- 任何中間節點被修改 → chain break 檢測

**Saga Orchestration**：多步分佈式事務，支援 compensation（undo）操作。

**Risk Weight Model**：每個 action 有 `risk_weight`，影響 error budget burn rate。

### Hermes 啟發

**Hermes Tool Scoping → Execution Rings**：
- `max_concurrent_tools: 2` + `network_allowed: false` + `filesystem_scope: none` = Ring 3 Sandbox = **純讀取探索 agent**
- `network_allowed: true (allowlist)` + `filesystem_scope: scoped` = Ring 2 Standard = **正常 cron job**
- `filesystem_writable: true` + `max_concurrent_tools: 8` = Ring 1 = **有破壞力的 agent**（如 `auto-git-push`）
- Ring 0 = **系統級操作**（修改 cron job 定義、刪除 workspace）

**Exploration Tool Scoping Gradient 實作**（`exploration-tool-scoping-gradient.md`）：
```
4-tool 白名單（Ring 3 Sandbox）：
  - terminal (read-only): search_files, read_file, session_search
  - web: web_search, curl
  - file: ls, stat
  - 禁止: write_file, terminal exec, delete
```

**Action Descriptor 應用於 Hermes**：
- `reversibility: NONE`：刪除檔案、`git push --force`
- `reversibility: FULL`：write_file（有 git revert 可恢復）
- `is_read_only: true`：search_files, read_file, curl, session_search
- 不可逆 + 非唯讀 → 需要高一層 Ring

**Privilege Elevation 對應 OTP Gate**（WS-031/OTP）：
- WS-031 的 `otp_gate.py`：generate OTP → user approves → elevated action
- AGT 的 Ring 1 elevation：需要 `>= 0.85 trust` + `sponsor attestation`
- **對映**：AGT sponsor attestation = Hermes OTP approval
- OTP 的 5-min expiry = AGT 的 `DEFAULT_TTL: 300s`
- **差距**：Hermes 沒有「trust score」概念，所有 session 同等信任。只有 OTP 才暫時提升

**Session Isolation 對應 Hermes cron session**：
- 每個 cron job 是獨立的 session
- `filesystem_scope: session` = 每個 cron job 只能寫自己的 `workdir`
- Hermes 的 `workdir` 欄位就是 session-scoped filesystem

**Kill Switch → Hermes gateway restart**：
- Hermes 的 `kill -SIGUSR1 $(cat gateway.pid)` = AGT 的 `kill(agent_id, handoff=false)`
- 差異：AGT 有 `handoff` 機制（step 交接），Hermes 只是重啟，沒有 compensation

**Hash Chain Audit → heartbeat_action_log.jsonl**：
- `append-only`：heartbeat_action_log.jsonl 只有 `>>` append，沒有 in-place edit
- SHA-256 hash chain：`record_action_log` 每次寫入含前一条 hash（如果有用 hash chain）
- 目前 `heartbeat_action_log.jsonl` 沒有 hash chain——可以作為 WS-035 的一個小 enhancement

---

## 跨 Spec 綜合：AGT 與 Hermes 架構對應圖

```
AGT Specification Stack          Hermes 現有設施          缺口
─────────────────────────────────────────────────────────────────────
Identity & Trust                 agent_id + owner          sponsor_verified
  └─ Trust Score (0-1000)         autonomy_level (0-4)      decay, regime_change
  └─ IATP (mutual auth)           OTP gate (unidirectional)  mutual auth
  └─ Scope Chain                  delegation (TBD)           無 delegation

Policy Engine                    ToolFingerprint +          整合以上 identity
  └─ GovernancePolicy             MCPResponseScanner          trust → policy
  └─ allowed_tools[]              enabled_toolsets           scope gradient

Hypervisor                       cron job execution          ring model
  └─ Execution Rings              workdir isolation          ring enforcement
  └─ Resource Constraints         max concurrent tools       per-tool limits
  └─ Privilege Elevation          OTP gate                   trust-gated elevation
  └─ Kill Switch                  SIGUSR1 gateway restart    step handoff

SRE Governance                   heartbeat EVOLVE           SLO formalization
  └─ SLO + Error Budget          severity escalation         burn rate tracking
  └─ Circuit Breaker              _DoomLoopTracker           integration
  └─ Burn Rate Alerts             [warning]/[critical]       SLO-based alerting
  └─ Chaos Engineering           (none)                     staging fault injection
  └─ Golden Traces                (none)                     regression test
  └─ Artifact Signing            HMAC sidecar (WS-031)       full Ed25519 signing
```

---

## 未追蹤 Leads

- （無——本次三個 spec 均已覆蓋，Phase 1 終結）

## ✅ 本次探索完成
