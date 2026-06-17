#!/usr/bin/env python3
"""
build-graph.py — W3.2 知識地圖資料生成

從 vault .md 解析 [[wikilink]] → 生成 graph.json（nodes + edges）
給 vis-network 在首頁 render

節點 = 每個 .md
邊 = wikilink 引用關係
- 節省空間：只算 top 5 tags 的節點（or top N 連接數）
- 過濾孤兒節點（無 wikilink 進出）

輸出：site/public/graph.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

CONTENT_DIR = Path(__file__).parent.parent / "src" / "content" / "notes"
OUTPUT = Path(__file__).parent.parent / "public" / "graph.json"

WIKILINK_RE = re.compile(r"(?<!!)\[\[([^\[\]]+?)\]\]")


def normalize_target(target: str) -> str:
    if "#" in target:
        target = target.split("#", 1)[0]
    if "|" in target:
        target = target.split("|", 1)[0]
    return target.strip()


def filename_to_slug(path: Path) -> str:
    return path.stem  # sync-vault.py 用同樣命名


def collect_wikilinks(md_path: Path, slug_to_path: Dict[str, str]) -> Set[str]:
    """從一個 .md 抓所有 wikilink，回傳目標 slug 集合"""
    try:
        content = md_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return set()
    links = set()
    for m in WIKILINK_RE.finditer(content):
        raw = normalize_target(m.group(1))
        if not raw or raw.startswith(("http://", "https://", "file://")):
            continue
        # 試直接當 slug、or 加 .md、or 加 .md extension
        for cand in (raw, raw + ".md"):
            if cand in slug_to_path:
                links.add(slug_to_path[cand])
                break
        else:
            # 試 basename
            base = raw.split("/")[-1]
            for cand in (base, base + ".md"):
                if cand in slug_to_path:
                    links.add(slug_to_path[cand])
                    break
    return links


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=300, help="max nodes 數（取連接數 top N）")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not CONTENT_DIR.is_dir():
        print(f"ERROR: {CONTENT_DIR} not found. Run sync-vault.py first.", file=sys.stderr)
        return 2

    # 建 slug -> path 索引
    slug_to_path: Dict[str, str] = {}
    md_files = sorted(CONTENT_DIR.glob("*.md"))
    for md in md_files:
        slug_to_path[md.name] = md.stem

    # 建 basename -> full slug 索引（vault wikilink 寫 basename 如 [[2026-05-12-facts]]，要對到 full slug 10-Daily-2026-05-12-facts）
    basename_to_slug: Dict[str, str] = {}
    for full_slug in slug_to_path.values():
        # full slug 像 "10-Daily-2026-05-12-facts"，basename = "2026-05-12-facts"
        basename = full_slug.rsplit("-", 1)[-1]  # 簡單取最後段（日期型檔名適用）
        # 但要避免 "facts" 之類非唯一 basename 撞名
        # 完整 basename（去掉 -YYYY-MM-DD- 前綴）:
        parts = full_slug.split("-")
        if len(parts) >= 4:  # 至少 30-Areas + 2026 + 05 + 12 + facts = 5 段
            base = "-".join(parts[3:])  # 從 index 3 開始
            if base not in basename_to_slug:  # 第一個贏，避免撞名
                basename_to_slug[base] = full_slug

    print(f"Found {len(md_files)} notes, {len(basename_to_slug)} unique basenames")

    # 算每個 note 的連接數
    edges: List[Dict] = []
    out_degree: Counter = Counter()
    in_degree: Counter = Counter()
    notes_data: List[Dict] = []

    # 先讀 manifest 拿 title + tags + status
    manifest_path = CONTENT_DIR.parent / "_manifest.json"
    manifest = {}
    if manifest_path.is_file():
        try:
            d = json.loads(manifest_path.read_text(encoding="utf-8"))
            for n in d.get("notes", []):
                manifest[n["slug"]] = n
        except Exception:
            pass

    def resolve_target(target: str) -> str | None:
        """wikilink target → full slug"""
        # 1. 直接命中 full slug（slug_to_path 的 value）
        if target in slug_to_path.values():
            return target
        # 2. basename 對照
        if target in basename_to_slug:
            return basename_to_slug[target]
        # 3. 加 .md 試
        if (target + ".md") in slug_to_path:
            return slug_to_path[target + ".md"]
        # 4. 含 / 試 partial path
        if "/" in target:
            # 試對應 "10-Daily/2026-05-12-facts" 形式
            for full in slug_to_path.values():
                if full.endswith("-" + target.replace("/", "-")):
                    return full
                if full == target.replace("/", "-"):
                    return full
        return None

    for md in md_files:
        slug = md.stem
        try:
            content = md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for m in WIKILINK_RE.finditer(content):
            raw = normalize_target(m.group(1))
            if not raw or raw.startswith(("http://", "https://", "file://")):
                continue
            target_slug = resolve_target(raw)
            if not target_slug or target_slug == slug:
                continue
            edges.append({"from": slug, "to": target_slug})
            out_degree[slug] += 1
            in_degree[target_slug] += 1

    # 計算每個 note 的「總度」= in + out（重要性）
    all_slugs = {md.stem for md in md_files}
    degree: Dict[str, int] = {}
    for s in all_slugs:
        degree[s] = out_degree.get(s, 0) + in_degree.get(s, 0)

    # 取 top N 連接數節點（其餘過濾掉，避免 graph 太雜）
    top_slugs = set(s for s, _ in sorted(degree.items(), key=lambda x: -x[1])[:args.limit])
    # 過濾 edges：from / to 都要在 top_slugs
    edges_filtered = [e for e in edges if e["from"] in top_slugs and e["to"] in top_slugs]

    # 組 nodes
    nodes = []
    for slug in top_slugs:
        info = manifest.get(slug, {})
        nodes.append({
            "id": slug,
            "label": info.get("title", slug)[:50],  # 截短避免太長
            "title": info.get("title", slug),
            "type": info.get("type", "note"),
            "status": info.get("status", "seedling"),
            "tags": info.get("tags", []),
            "degree": degree.get(slug, 0),
            "url": f"/notes/{slug}/",
        })

    result = {
        "generated_at": "2026-06-17",  # build time
        "node_count": len(nodes),
        "edge_count": len(edges_filtered),
        "total_notes": len(all_slugs),
        "filtered_to_top": args.limit,
        "nodes": nodes,
        "edges": edges_filtered,
    }

    if args.dry_run:
        print(f"DRY-RUN: {len(nodes)} nodes, {len(edges_filtered)} edges (out of {len(edges)})")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"→ {len(nodes)} nodes, {len(edges_filtered)} edges (filtered from {len(edges)})")
    print(f"→ {args.output}")
    print(f"  size: {args.output.stat().st_size / 1024:.1f} KB")

    return 0


if __name__ == "__main__":
    sys.exit(main())
