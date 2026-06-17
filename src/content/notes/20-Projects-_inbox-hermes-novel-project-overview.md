---
_slug: 20-Projects-_inbox-hermes-novel-project-overview
_vault_path: 20-Projects/_inbox/hermes-novel-project-overview.md
date: 2026-05-12
tags:
- novel
- chinese-classics
- automation
- scraping
- github
project_path: ~/hermes-novel-project/
title: Hermes Novel Project
created: '2026-05-13'
updated: '2026-06-15'
type: research
status: budding
---

# Hermes Novel Project

> Auto-fetch Chinese classical novels and push to GitHub.

## Structure

```
hermes-novel-project/
├── docs/
├── novels/       # Fetched novels
├── reading/      # Reading progress
└── scripts/
    └── auto_fetch.py   # Daily fetch script
```

## Automation

- **Daily fetch**: Cronjob `daily-book-fetch` at 6 AM
- **Daily reading**: Cronjob `西遊記每日閲讀心得` at 9 AM
- **Progress tracking**: `~/reading/by_book/<book>/progress.json`

## Current Books

- 《西遊記》(Journey to the West) — Daily reading in progress

## GitHub Integration

Pushes fetched content to GitHub repo automatically.

## See Also

- [[project-map-index]] — Central index of all active projects
