#!/usr/bin/env python3
"""
简单的 RSS 聚合器：
- 读取 `feeds.yaml` 中的 feed
- 抓取近 24 小时内的文章
- 提取每篇文章的第一段或 meta 描述作为要点
- 输出 `out/digest-YYYYMMDD.md`

使用方法：
  python src/aggregator.py
"""
import os
import sys
import yaml
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
from pathlib import Path

OUT_DIR = Path("out")
OUT_DIR.mkdir(exist_ok=True)


def load_feeds(path="feeds.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("feeds", [])


def entry_published_dt(entry):
    # 尝试使用 published_parsed/updated_parsed
    for key in ("published_parsed", "updated_parsed"):
        t = entry.get(key)
        if t:
            return datetime.fromtimestamp(t, tz=timezone.utc) if isinstance(t, (int, float)) else None
    return None


def fetch_summary(url, fallback=""):
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        # 优先取第一段较长的 <p>
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if len(text) >= 40:
                return text
        # 尝试 meta description
        md = soup.find("meta", attrs={"name": "description"})
        if md and md.get("content"):
            return md.get("content").strip()
    except Exception:
        pass
    return fallback


def build_digest(items):
    today = datetime.now().strftime("%Y%m%d")
    path = OUT_DIR / f"digest-{today}.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# AI 每日快讯 — {datetime.now().strftime('%Y-%m-%d')}")
        f.write("\n\n本摘要为近 24 小时内聚合内容，按来源排序。\n\n")
        for it in items:
            f.write(f"- **{it['source']}**: [{it['title']}]({it['link']})\n")
            if it.get("summary"):
                f.write(f"  \n  要点: {it['summary']}\n\n")
            else:
                f.write("\n")
    print("Wrote:", path)
    return path


def main():
    feeds = load_feeds()
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    all_items = []
    seen = set()
    for feed in feeds:
        name = feed.get("name")
        url = feed.get("url")
        if not url:
            continue
        try:
            d = feedparser.parse(url)
        except Exception:
            continue
        for entry in d.entries:
            link = entry.get("link")
            if not link:
                continue
            if link in seen:
                continue
            pubdt = entry_published_dt(entry)
            # 若无时间信息，保守地包含（因为可能是刚发布）
            if pubdt and pubdt < cutoff:
                continue
            seen.add(link)
            title = entry.get("title", "(no title)")
            fallback = entry.get("summary", "")
            summary = fetch_summary(link, fallback=fallback)
            # 简短化 summary 为一两句
            if summary and len(summary) > 300:
                summary = summary[:300].rsplit('.', 1)[0] + '.'

            all_items.append({
                "source": name or d.feed.get("title", "unknown"),
                "title": title,
                "link": link,
                "summary": summary,
            })

    if not all_items:
        print("No new items in last 24 hours.")
        return
    # 按来源排序
    all_items.sort(key=lambda x: x.get("source", ""))
    build_digest(all_items)


if __name__ == "__main__":
    main()
