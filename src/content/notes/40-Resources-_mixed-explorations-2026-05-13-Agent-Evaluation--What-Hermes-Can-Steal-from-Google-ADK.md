---
_slug: 40-Resources-_mixed-explorations-2026-05-13-Agent-Evaluation--What-Hermes-Can-Steal-from-Google-ADK
_vault_path: 40-Resources/_mixed/explorations/2026-05-13-Agent-Evaluation--What-Hermes-Can-Steal-from-Google-ADK.md
_parse_error: "mapping values are not allowed here\n  in \"<unicode string>\", line\
  \ 2, column 24:\n    title: Agent Evaluation: What Hermes Can Steal from Goo ...\
  \ \n                           ^"
_raw_fm: '

  title: Agent Evaluation: What Hermes Can Steal from Google ADK

  date: 2026-05-13

  type: explorations

  tags: [explorations, auto-ingested]

  fingerprint: [adk, agent, disk, eval, expected, google, heartbeat, hermes, mem,
  stuck]

  created: 2026-05-13

  updated: 2026-06-15

  status: active

  '
title: 'Agent Evaluation: What Hermes Can Steal from Google ADK'
type: resource
status: seedling
created: '2026-06-15'
updated: '2026-06-15'
---

# Agent Evaluation: What Hermes Can Steal from Google ADK

**Date**: 2026-05-13  
**Source**: [google/adk-python](https://github.com/google/adk-python) (19.6K ⭐, Apache 2.0)  
**Theme**: 研究日主題 — Multi-Agent Systems（順便撈到的好東西）  
**Confidence**: medium（只讀 README + llms.txt，沒 deploy）

## The Gap

Hermes 的 heartbeat v2 監控的是**系統健康**：disk、mem、stuck processes、provider errors。但它完全不碰**agent 品質**。

Google ADK 有一個很乾淨的 evaluation 介面：

```bash
adk eval \
    samples_for_testing/hello_world \
    samples_for_testing/hello_world/hello_world_eval_set_001.evalset.json
```

eval set 是一個 JSON，定義 input/expected output 配對。框架自動跑 agent、比對結果、給分。

## Why This Matters

目前 Hermes 的核心品質 loop 是：
1. 用戶發現問題 → 回報
2. 除錯 → patch skill / script
3. 靠 heartbeat 確保系統別掛

但沒有**自動化的 agent correctness 驗證**。舉例：
- `heartbeat_v2.py` 改了 scoring 公式 → 沒人知道 REST 決策是否還是對的
- `managed-agents-framework` 的 swarm runner 被改路徑 → `ma run` 壞了，沒自動發現（上次 cron 就撞到這個）
- Skill 更新後，沒 regression test

## ADK 的 eval 能移植到 Hermes 嗎？

ADK eval 的核心元件：
1. **EvalSet JSON** — 定義 test cases（input, expected_tool_calls, expected_response）
2. **EvalRunner** — 跑 agent，收集結果
3. **Metrics** — tool call accuracy, response match, latency

Hermes 的對應思路：

```yaml
# ~/.hermes/eval_sets/heartbeat_scoring.yaml
- name: "REST when idle"
  context: {disk: 12, mem: 45, stuck: 0, pending: 7}
  expected_action: REST
- name: "WORK when stuck sessions"
  context: {disk: 30, mem: 60, stuck: 3, pending: 5}
  expected_action: WORK
- name: "REPORT when disk high"
  context: {disk: 88, mem: 50, stuck: 0, pending: 0}
  expected_action: REPORT
```

但實際上有難度 — Hermes 的 agent 行為是**非確定性**的（不同 LLM provider 會給不同結果），沒辦法簡單做 string match。

## 務實的下一步

與其追求 formal eval framework，更務實的路可能是：

1. **Deterministic unit tests for non-LLM components** — heartbeat_v2.py 的 scoring、snapshot parsing、health check functions。這些是純 Python 函數，可以直接用 pytest。
2. **Smoke tests for skills** — load skill → check syntax + frontmatter → verify skill_view() works
3. **Cron job health integration** — 在 heartbeat 中加入「上次 cron job 是否有成功輸出」檢查（目前 heartbeat 只看 process 是否 alive，不看 output 是否 valid）
4. **Golden test set for critical paths** — 挑 5-10 個高頻操作（如 `hermes config` 的各種 subcommand），確保 CLI 不會 regression

## 值得追蹤

- ADK 的 [EvalSet schema](https://github.com/google/adk-docs/blob/main/docs/evaluate/index.md) 有 formal spec，可以直接參考格式
- ADK 的 testing 指南（`get-started/testing.md`）有 agent unit test 的 pattern
- `llms-full.txt` 裡可能有 eval runner 的完整實作細節（但檔案很大）

