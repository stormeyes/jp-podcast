#!/usr/bin/env python3
"""从 iCloud 日语听力 拷音频并生成 feed.xml。用法: python3 build.py && git add -A && git commit -m update && git push"""
import email.utils, re, shutil, subprocess
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

SRC = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/日语听力"
BASE = "https://stormeyes.github.io/jp-podcast"
here = Path(__file__).parent

items = []
for f in sorted(SRC.glob("第*单元单词.m4a"), key=lambda p: int(re.search(r"\d+", p.name).group())):
    n = int(re.search(r"\d+", f.name).group())
    dst = here / f"u{n:02d}.m4a"
    shutil.copy2(f, dst)
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", dst]))
    # 按单元号伪造发布时间，保证播客里顺序稳定
    date = email.utils.format_datetime(datetime(2026, 1, 1, 0, n, tzinfo=timezone.utc))
    items.append(f"""<item><title>第{n}单元单词</title><guid isPermaLink="false">jp-u{n:02d}-{int(f.stat().st_mtime)}</guid>
<enclosure url="{BASE}/{dst.name}" length="{dst.stat().st_size}" type="audio/x-m4a"/>
<pubDate>{date}</pubDate><itunes:duration>{round(dur)}</itunes:duration><itunes:episode>{n}</itunes:episode><description>第{n}单元单词</description></item>""")

(here / "feed.xml").write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
<channel><title>多邻国日语单词</title><link>{BASE}/</link><language>ja</language>
<description>{escape("多邻国日语各单元单词：日语一遍 + 中文意思")}</description>
<itunes:author>me</itunes:author><itunes:explicit>false</itunes:explicit><itunes:category text="Education"><itunes:category text="Language Learning"/></itunes:category>
<itunes:image href="{BASE}/cover.png"/>
{chr(10).join(reversed(items))}
</channel></rss>
""", encoding="utf-8")
print(f"{len(items)} episodes -> feed.xml")
