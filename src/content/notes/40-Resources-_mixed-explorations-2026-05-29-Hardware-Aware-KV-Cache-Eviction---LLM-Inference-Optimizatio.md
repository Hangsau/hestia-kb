---
_slug: 40-Resources-_mixed-explorations-2026-05-29-Hardware-Aware-KV-Cache-Eviction---LLM-Inference-Optimizatio
_vault_path: 40-Resources/_mixed/explorations/2026-05-29-Hardware-Aware-KV-Cache-Eviction---LLM-Inference-Optimizatio.md
title: Hardware-Aware KV Cache Eviction — LLM Inference Optimization
date: 2026-05-29
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- aware
- cache
- eviction
- hardware
- hit
- llm
- memory
- prefix
- priority
- scheduling
created: '2026-05-29'
updated: '2026-06-15'
status: budding
---

# Hardware-Aware KV Cache Eviction — LLM Inference Optimization

**Date**: 2026-05-29
**Topic**: Hardware-aware KV cache eviction strategies for LLM inference
**Sources**: 4 (HillInfer arXiv 2602.18750, NVIDIA TRT-LLM blog, Stabilarity Hub cache-aware scheduling, HotPrefix SIGMOD 2026)

---

## Per-Source Insights

### 1. HillInfer — Hierarchical KV Eviction via SmartSSD (arXiv 2602.18750)

**What it is**: CSD-assisted (Computational Storage Device) KV eviction framework for memory-constrained AIPCs. Offloads *only lightweight token importance evaluation* to a SmartSSD FPGA, avoiding the FPGA resource exhaustion problem of prior approaches that tried to offload full exact attention computation.

**Core architecture — three components**:
- **HKM (Hierarchical KV Cache Manager)**: Physically partitions hot KV (CPU DRAM) and cold KV (SmartSSD). Uses two insights: (a) *temporal locality* — newly generated tokens have extremely high probability of being critical for immediately following steps, so recent α·N tokens are pinned in Hot Pool; (b) *hit-rate stability* — some historical tokens act as persistent "attention sinks" with consistently high importance. Maintains a globally synchronized KV Cache Hit-Rate Table. Bidirectional promotion/demotion after each decoding step keeps Hot Pool populated with highest-utility data.
- **APP (Adaptive Prefetch-based Pipeline)**: Balances evaluation workload between multi-core CPU and SmartSSD FPGA. Derives optimal capacity ratio β between hot/cold pools via analytical latency model: `TCPU = Mc/fc + αMc/Bc ≈ Ms/fs + αMs/Bs = TSmartSSD`. Prevents straggler effect where faster processor stalls waiting for slower one.
- **CEC (CSD-based Evaluation Configuration)**: Strips Softmax exponentiation and scaling division — uses raw inner product `Q·K^T` for importance ranking (monotonic relationship sufficient for ranking). Asymmetric precision: INT8/INT4 for FPGA evaluation phase, original FP16 KV tensors only retrieved after top-K indices identified.

**Key numbers**: 8.56× speedup over SOTA baselines. 76.25%–88.32% latency reduction. α (importance retention ratio) = 10–20%.

**Memory hierarchy insight**: On AIPC (RTX 4090 24GB VRAM + 64GB host DRAM), Qwen-7B with 4K context and batch=8 consumes ~30GB — exceeds GPU VRAM alone. KV cache grows linearly with context length, number of layers, and hidden dimension. KV eviction is mandatory for long-context on memory-constrained devices.

**I/O thrashing problem**: Token importance is query-dependent (fluctuates across decoding steps). Naive eviction causes ping-pong data movement between host DRAM and SSD on every step. HKM's solution: partition + bidirectional pools, not just "evict to SSD."

---

### 2. NVIDIA TRT-LLM — Priority-Based KV Cache Eviction

**What it is**: Production-grade priority-based eviction API in TensorRT-LLM Executor. Users specify retention config per request:

```
struct TokenRangeRetentionConfig {
  start: int
  end: optional<int>   # null = extend to end of sequence
  priority: int        # 0-100, higher = more retained
  duration: optional<int>  # how long priority applies
}
```

**Key production insight**: Priority-based eviction increasing cache hit rate by ~20% in NVIDIA benchmarks. Even without explicit priorities, the implementation "biases toward blocks further from the root" — a small but measurable improvement.

**Duration semantics**: `duration=30s` means priority applies for 30 seconds after last *reuse* (not after eviction). So a cache block can be demoted after 30s of non-access, not just non-use.

**Two use cases**:
1. System prompts: `[0, 500)` tokens → priority=100, duration=∞ (never evict unless necessary)
2. Cache-sensitive routing: KV cache event API exposes `KVCacheEvent {CreatedData, StoredData, RemovedData, UpdatedData}` for multi-instance routing decisions. An instance with cached prefixes for an incoming request may be preferred over a less-loaded instance without cached state.

**KV cache event API enables**: eventually consistent cache state tracking across multiple executor instances. Useful for KV-aware load balancing (prefer instance that already has relevant KV state over one that's less loaded but has cold cache).

---

### 3. Stabilarity Hub — Cache-Aware Request Scheduling

**What it is**: Academic research synthesis on cache-aware scheduling vs. cache-agnostic baselines. Compiles data from SGLang, Mooncake, LMCache across three research questions.

**RQ1 — Hit rates by scheduling strategy**:
| Strategy | Cache Hit Rate |
|---|---|
| Random | 12% |
| Round-robin | 15.8% |
| Least-load | 22% |
| Prefix-aware (SGLang RadixAttention) | 58.4% |
| KV-aware cluster routing (Mooncake) | 71.2% |
| KV-aware + prefix-tree batching | **82.6%** |

Round-robin to KV-aware = **5.2× improvement** in hit rate. At 82.6% hit rate, ~5.6× less prefill computation.

**RQ2 — Batch size vs. cache pressure**:
Optimal batch size *decreases by 2–4×* under high cache pressure:
- Low pressure (2K context): optimal batch = 128 (1120 tok/s)
- Medium pressure (8K context): optimal batch = 32 (620 tok/s)  
- High pressure (32K context): optimal batch = 16 (310 tok/s)

Static batch size configurations in production leave significant performance on the table.

**RQ3 — Eviction policy and memory stability**:
| Eviction Policy | Memory Utilization StdDev |
|---|---|
| LRU | 12.4% |
| TTL-based | 9.8% |
| Prefix-tree-aware | **6.2%** |

LRU evicts recently-used-but-still-valuable entries during load spikes → recompute shortly after → high variance. Prefix-tree-aware eviction avoids evicting internal nodes that serve as prefix for multiple active requests.

**Eviction policy and P99 latency**: Prefix-tree-aware reduces P99 latency spikes during eviction by 35% vs. LRU.

**Prefix reuse by workload type**:
- RAG: 68% compute savings (shared document chunks)
- Code completion: 52%
- Agentic: 45% (shared conversation history across tool calls)
- Chatbot: 35%
- Batch summarization: 22%

**Combined with disaggregated prefill-decode**: 1.4–2.3× (disaggregation) × 1.4× (cache-aware scheduling) = **2–3.2× total TTFT improvement** over baseline monolithic serving.

---

### 4. HotPrefix — Hotness-Aware KV Cache Scheduling (SIGMOD 2026)

**What it is**: SIGMOD 2026 paper on hotness-aware scheduling for prefix sharing in LLM inference. vLLM reserves fixed physical memory blocks for shared prefixes. HotPrefix extends this with hotness awareness.

**Core contribution**: Unlike vLLM's static block allocation for prefix sharing, HotPrefix dynamically adjusts based on prefix access frequency (hotness). Hot prefixes get more cache blocks; cold prefixes get fewer or none.

**SIGMOD 2026 paper**: PDF available at `cs.nju.edu.cn/tianchen/lunwen/2026/sigmod26-liyuhang.pdf`. Full technical content not yet extracted — PDF was partially retrieved but full text processing deferred. Core claim from abstract: dynamic hotness-aware block allocation improves upon vLLM's fixed-size prefix sharing.

---

## Cross-Article Synthesis

### The hardware-aware eviction spectrum

There are three distinct layers of "hardware awareness" in KV cache eviction, roughly ordered by hardware sophistication required:

**Layer 1 — Software priority (TRT-LLM)**: Pure API-level. No hardware modification. User annotates token ranges with priority/duration, system biases eviction accordingly. 20% hit rate improvement. Deployable today on any NVIDIA GPU cluster.

**Layer 2 — Topology-aware eviction (Stabilarity)**: Schedulers use knowledge of prefix structure (radix tree), request-level prefix sharing, and batch size to inform eviction decisions. Internal nodes less likely to evict than leaf nodes. 50% reduction in memory variance vs. LRU. This is a scheduling/logic layer, not a hardware layer.

**Layer 3 — Heterogeneous hardware partitioning (HillInfer)**: Explicit partition of hot/cold KV between CPU DRAM and SmartSSD. Near-data processing on FPGA for importance evaluation. Adaptive workload balancing (APP) between CPU and FPGA to eliminate straggler effects. 8.56× speedup on AIPC. Requires SmartSSD hardware.

The three layers are complementary: Layer 1 and 2 can stack (TRT-LLM priority API + prefix-tree-aware scheduler), and Layer 3 is additive for edge/memory-constrained scenarios.

### The I/O thrashing problem is fundamental

All sources independently identify the same core problem: token importance is *query-dependent*, changing at every decoding step. A naive "evict low-importance tokens to SSD" strategy creates ping-pong I/O — tokens demoted to SSD become important in the next step, get promoted back, then demoted again. This is why LRU has 12.4% memory variance (HillInfer's measurements).

HillInfer's solution (Hot/Cold pool partition + bidirectional promotion/demotion) and the prefix-tree-aware eviction (don't evict internal nodes that serve multiple requests) are two different architectural answers to the same problem. The convergent design principle: *structure-aware eviction outperforms recency-only eviction*.

### Memory variance = multi-tenant density

Stabilarity's key insight: memory utilization variance (6.2% vs 12.4% stddev) directly determines how tightly you can pack concurrent model instances. Lower variance = tighter packing = higher multi-tenant density without OOM risk. This is an economic argument for investing in eviction policy quality, not just hit rate.

### Agentic workloads are a sweet spot

RAG (68% compute savings) and agentic (45%) workloads benefit most from cache-aware scheduling because they have the most structured prefix sharing (shared document chunks, shared conversation history across tool calls). This aligns with Hermes's agentic architecture — KVFlow's multi-agent prefix caching finding (45–68% compute savings) is directly relevant to the kind of multi-turn tool-use workflows Talos/Hestia run.

---

## Untracked Leads

- `https://arxiv.org/abs/2602.18750` — HillInfer full PDF (not yet fetched; arXiv abstract/html only)
- `https://cs.nju.edu.cn/tianchen/lunwen/2026/sigmod26-liyuhang.pdf` — HotPrefix SIGMOD 2026 full paper
- SGLang RadixAttention internal eviction policy details
- Mooncake global cache directory implementation for cross-cluster KV-aware routing

## Hermes Relevance

- **KVFlow (multi-agent prefix caching)**: 45–68% compute savings in agentic workloads — directly relevant to Talos governance pipeline and multi-agent coordination patterns
- **Memory variance metric**: Could be adapted for heartbeat_learning.py drift detection (stability of distilled patterns over time)
- **Priority-based eviction API**: TRT-LLM's `KvCacheRetentionConfig` is a concrete API design for explicit eviction control — relevant to WS-028 (agent lifecycle governance) resource management
- **HillInfer's hit-rate table**: Lightweight `2N` byte tracking for `N` tokens — similar to YantrikDB's temporal decay index (per-file metadata tracking)

## ✅ 本次探索完成

