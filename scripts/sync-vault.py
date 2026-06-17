#!/usr/bin/env python3
"""
sync-vault.py — 把 ~/obsidian-vault/*.md 同步到 site/src/content/notes/

W2.1 同步腳本：
- 走 vault 排除 _staging / .obsidian / .trash
- 解析 frontmatter（pyyaml）
- 補 status / type / title / tags fallback
- slug 從 filepath 算
- 寫到 site/src/content/notes/{slug}.md
- build-time 用 Astro content collection

輸出：
  site/src/content/notes/{slug}.md  ← 加上 frontmatter 強化的版本
  site/src/content/_manifest.json   ← 全 manifest 給 build script 用

用法：
    python3 sync-vault.py
    python3 sync-vault.py --dry-run
    python3 sync-vault.py --limit 20  # 測試用
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

VAULT_ROOT = Path.home() / "obsidian-vault"
SITE_CONTENT = Path(__file__).parent.parent / "src" / "content" / "notes"
SITE_MANIFEST = Path(__file__).parent.parent / "src" / "content" / "_manifest.json"

# 排除 vault 內不該 sync 的目錄
EXCLUDE_DIRS = {".git", ".obsidian", "_staging", "_rejected", "_quarantine"}

# status fallback（從 Hestia KB 設計 spec）
VALID_STATUSES = {"seedling", "budding", "evergreen"}

# type fallback（從 vault 觀察到的）
VALID_TYPES = {
    "research", "project", "daily", "moc", "pubmed", "report", "note", "log", "review",
    "concept", "resource", "template", "area", "inbox", "inbox-stub",
}


def parse_frontmatter(content: str) -> Tuple[Dict, str]:
    """解析 frontmatter，回傳 (dict, body)"""
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    try:
        fm = yaml.safe_load(parts[1]) or {}
        if not isinstance(fm, dict):
            fm = {}
        body = parts[2].lstrip("\n")
        return fm, body
    except yaml.YAMLError as e:
        # YAML 解析失敗：fallback — 把整段當 body，前面的 --- 區段去掉
        return {"_parse_error": str(e), "_raw_fm": parts[1]}, parts[2].lstrip("\n")


def normalize_tags(tags) -> List[str]:
    """tag 統一轉 list[str]，過濾空字串"""
    if not tags:
        return []
    if isinstance(tags, str):
        # YAML list inline: [a, b, c]
        if tags.startswith("[") and tags.endswith("]"):
            tags = [t.strip().strip('"').strip("'") for t in tags[1:-1].split(",")]
        else:
            tags = [tags]
    if isinstance(tags, list):
        return [str(t).strip().strip('"').strip("'") for t in tags if str(t).strip()]
    return [str(tags)]


def compute_slug(filepath: Path) -> str:
    """從 vault 內相對路徑算 URL slug（用於網址）

    例：30-Areas/swimming/drills/freestyle/fr01.md
       → 30-Areas-swimming-drills-freestyle-fr01
    """
    rel = filepath.relative_to(VAULT_ROOT)
    # 去掉 .md 副檔名
    parts = list(rel.parts)
    if parts[-1].endswith(".md"):
        parts[-1] = parts[-1][:-3]
    # 用 - 接，看起來乾淨
    return "-".join(parts)


def enrich_frontmatter(fm: Dict, filepath: Path, body: str) -> Dict:
    """補齊 frontmatter 缺的欄位"""
    # title: 從 frontmatter / 第一個 H1 / 檔名
    if "title" not in fm or not fm["title"]:
        m = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
        if m:
            fm["title"] = m.group(1).strip()
        else:
            fm["title"] = filepath.stem
    # type: 從 frontmatter / 父目錄推
    if "type" not in fm or not fm["type"]:
        rel = filepath.relative_to(VAULT_ROOT)
        first_dir = rel.parts[0] if rel.parts else ""
        dir_to_type = {
            "10-Daily": "daily",
            "20-Projects": "project",
            "30-Areas": "area",
            "40-Resources": "resource",
            "50-Archives": "archive",
            "90-MOCs": "moc",
            "99-Templates": "template",
            "research": "research",
        }
        fm["type"] = dir_to_type.get(first_dir, "note")
    # status: 從 frontmatter / 預設 seedling
    if "status" not in fm or not fm["status"]:
        fm["status"] = "seedling"
    elif fm["status"] not in VALID_STATUSES:
        # 嘗試 normalize
        s = str(fm["status"]).lower()
        if s in ("active", "open", "ongoing", "in-progress"):
            fm["status"] = "budding"
        elif s in ("done", "complete", "finished", "closed"):
            fm["status"] = "evergreen"
        else:
            fm["status"] = "seedling"
    # tags: 統一 list
    if "tags" in fm:
        fm["tags"] = normalize_tags(fm["tags"])
    # created/updated: 補 mtime（轉成 string 避免 json serialize 問題）
    stat = filepath.stat()
    mtime_str = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d")
    if "created" not in fm:
        fm["created"] = mtime_str
    if "updated" not in fm:
        fm["updated"] = mtime_str
    # 確保 created/updated 是 string（vault 裡有時是 datetime 物件）
    if hasattr(fm.get("created"), "strftime"):
        fm["created"] = fm["created"].strftime("%Y-%m-%d")
    if hasattr(fm.get("updated"), "strftime"):
        fm["updated"] = fm["updated"].strftime("%Y-%m-%d")
    # 網站內部用：vault 相對路徑 + slug
    fm["_vault_path"] = str(filepath.relative_to(VAULT_ROOT))
    fm["_slug"] = compute_slug(filepath)
    return fm


def render_note(fm: Dict, body: str) -> str:
    """重新 render .md（強化後的 frontmatter + 原 body）"""
    # 確保 _vault_path / _slug 在最前（網站 build 用）
    out = {"_slug": fm.pop("_slug", ""), "_vault_path": fm.pop("_vault_path", "")}
    out.update(fm)
    yaml_str = yaml.safe_dump(out, allow_unicode=True, sort_keys=False, default_flow_style=False)
    return f"---\n{yaml_str}---\n\n{body}"


def should_sync(filepath: Path) -> bool:
    rel = filepath.relative_to(VAULT_ROOT)
    return not any(part in EXCLUDE_DIRS for part in rel.parts)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync vault to Astro content collection")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--vault", type=Path, default=VAULT_ROOT)
    args = parser.parse_args()

    if not args.vault.is_dir():
        print(f"ERROR: vault not found: {args.vault}", file=sys.stderr)
        return 2

    # 收 vault .md
    md_files: List[Path] = []
    for p in args.vault.rglob("*.md"):
        if should_sync(p):
            md_files.append(p)
    md_files.sort()
    if args.limit:
        md_files = md_files[: args.limit]

    print(f"=== Sync vault → Astro content collection ===")
    print(f"Vault: {args.vault}")
    print(f"Found: {len(md_files)} .md")
    if args.dry_run:
        print(f"Mode:  DRY-RUN")
    print()

    SITE_CONTENT.mkdir(parents=True, exist_ok=True)

    manifest = []
    type_counter: Counter = Counter()
    status_counter: Counter = Counter()
    parse_errors = []

    for md in md_files:
        try:
            content = md.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"  ⚠ skip (read error): {md.relative_to(args.vault)} — {e}")
            continue

        fm, body = parse_frontmatter(content)
        if "_parse_error" in fm:
            parse_errors.append((str(md.relative_to(args.vault)), fm["_parse_error"]))
            # 仍然嘗試 fallback 處理

        fm = enrich_frontmatter(fm, md, body)
        slug = fm["_slug"]
        type_counter[fm["type"]] += 1
        status_counter[fm["status"]] += 1

        # 寫到 site
        out_path = SITE_CONTENT / f"{slug}.md"
        rendered = render_note(fm.copy(), body)

        if not args.dry_run:
            out_path.write_text(rendered, encoding="utf-8")

        # manifest 條目
        manifest.append({
            "slug": slug,
            "title": fm.get("title", ""),
            "type": fm.get("type", "note"),
            "status": fm.get("status", "seedling"),
            "tags": fm.get("tags", []),
            "created": fm.get("created", ""),
            "updated": fm.get("updated", ""),
            "vault_path": fm.get("_vault_path", ""),
            "url": f"/notes/{slug}/",
        })

    if not args.dry_run:
        SITE_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        SITE_MANIFEST.write_text(
            json.dumps({
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "vault_root": str(args.vault),
                "count": len(manifest),
                "type_breakdown": dict(type_counter),
                "status_breakdown": dict(status_counter),
                "notes": sorted(manifest, key=lambda m: m["slug"]),
            }, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    print(f"→ Wrote {len(manifest)} notes → {SITE_CONTENT}")
    print(f"→ Wrote manifest → {SITE_MANIFEST}")
    print()
    print(f"Type 分布:")
    for t, c in sorted(type_counter.items(), key=lambda x: -x[1]):
        print(f"  {t:15s}  {c}")
    print()
    print(f"Status 分布:")
    for s, c in sorted(status_counter.items(), key=lambda x: -x[1]):
        emoji = {"seedling": "🌱", "budding": "🌿", "evergreen": "🌳"}.get(s, "❓")
        print(f"  {emoji} {s:12s}  {c}")
    if parse_errors:
        print()
        print(f"⚠ {len(parse_errors)} parse errors:")
        for path, err in parse_errors[:5]:
            print(f"  {path}: {err[:100]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
