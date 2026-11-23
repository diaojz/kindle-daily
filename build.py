#!/usr/bin/env python3
"""抓取 feeds.py 里过去 WINDOW 小时的新文章，合成一本 EPUB：site/<日期>.epub + site/version.txt。"""
import concurrent.futures as cf, datetime as dt, html, os, re, subprocess, sys, tempfile, time
from pathlib import Path
import feedparser, requests, trafilatura
from feeds import SECTIONS

WINDOW = float(os.environ.get("WINDOW_HOURS", str(24 * 7)))
SEEN_FILE = Path(__file__).parent / "seen.txt"  # 已收录过的文章链接，每篇只进一期
SEEN = set(SEEN_FILE.read_text().split()) if SEEN_FILE.exists() else set()
TZ = dt.timezone(dt.timedelta(hours=8))
UA = {"User-Agent": "Mozilla/5.0 (Macintosh) kindle-daily/1.0"}
SITE = Path(__file__).parent / "site"
now = dt.datetime.now(dt.timezone.utc)
today = now.astimezone(TZ).date().isoformat()

DROP = re.compile(r"<(script|style|iframe|video|audio|form|svg|noscript)\b.*?</\1>|<(img|source|input|button)\b[^>]*>", re.S | re.I)
ATTR = re.compile(r'\s(style|class|id|width|height|on\w+|srcset|data-[\w-]+)="[^"]*"', re.I)

def clean(fragment):
    return ATTR.sub("", DROP.sub("", fragment or ""))

def text_len(fragment):
    return len(re.sub(r"<[^>]+>|\s", "", fragment or ""))

def fetch_full(url):
    try:
        r = requests.get(url, headers=UA, timeout=30)
        r.raise_for_status()
        out = trafilatura.extract(r.text, output_format="html", include_images=False,
                                  include_links=False, include_tables=True, url=url)
        return out if text_len(out) > 300 else None
    except Exception as e:
        print(f"  抓原文失败 {url}: {e}", file=sys.stderr)
        return None

def published(e):
    t = e.get("published_parsed") or e.get("updated_parsed")
    return dt.datetime(*t[:6], tzinfo=dt.timezone.utc) if t else None

def collect(source):
    name, url, limit, full = source
    try:
        feed = feedparser.parse(requests.get(url, headers=UA, timeout=30).content)
    except Exception as e:
        print(f"订阅源失败 {name}: {e}", file=sys.stderr)
        return []
    items = []
    for e in feed.entries:
        when = published(e)
        if not when or now - when > dt.timedelta(hours=WINDOW) or e.get("link", "") in SEEN:
            continue
        body = (e.get("content") or [{}])[0].get("value") or e.get("summary", "")
        if not full or text_len(body) < 800:
            time.sleep(2)  # 同一来源串行慢抓，避免 429
            body = fetch_full(e.get("link", "")) or body
        items.append({"title": e.get("title", "(无标题)").strip(), "link": e.get("link", ""),
                      "when": when, "body": clean(body), "source": name})
        if len(items) >= limit:
            break
    print(f"{name}: {len(items)} 篇")
    return items

def main():
    with cf.ThreadPoolExecutor(12) as ex:
        futures = {src[0]: ex.submit(collect, src) for _, srcs in SECTIONS for src in srcs}
        got = {k: v.result() for k, v in futures.items()}
    parts, toc, total = [], [], 0
    for section, srcs in SECTIONS:
        arts = [a for src in srcs for a in got[src[0]]]
        if not arts:
            continue
        total += len(arts)
        toc.append(f"<li><b>{section}</b>（{len(arts)}）<ul>" +
                   "".join(f"<li>{html.escape(a['title'])} <small>· {html.escape(a['source'])}</small></li>" for a in arts) + "</ul></li>")
        parts.append(f"<h1>{section}</h1>")
        for a in arts:
            stamp = a["when"].astimezone(TZ).strftime("%m-%d %H:%M")
            parts.append(f"<h2>{html.escape(a['title'])}</h2>\n<p class=meta>{html.escape(a['source'])} · {stamp}</p>\n"
                         f"{a['body']}\n<p class=meta>原文：{html.escape(a['link'])}</p>")
    if not total:
        sys.exit("没有新文章")
    d = dt.date.fromisoformat(today)
    cover = (f"<h1>今日导读</h1><p class=meta>{d.month} 月 {d.day} 日 · 星期{'一二三四五六日'[d.weekday()]}"
             f" · 共 {total} 篇</p><ul>{''.join(toc)}</ul>")
    SITE.mkdir(exist_ok=True)
    for old in SITE.glob("*.epub"):
        old.unlink()
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp, "book.html")
        src.write_text(f"<html><body>{cover}\n" + "\n".join(parts) + "</body></html>", encoding="utf-8")
        css = Path(tmp, "eink.css")
        css.write_text("body{line-height:1.6} .meta{color:#555;font-size:.85em} h1{page-break-before:always}"
                       " h2{page-break-before:always;font-size:1.3em} pre,code{white-space:pre-wrap;font-size:.85em}"
                       " table{font-size:.85em} blockquote{margin-left:1em;padding-left:.8em;border-left:3px solid #999}")
        subprocess.run(["pandoc", str(src), "-f", "html", "-o", str(SITE / f"{today}.epub"), "--toc", "--toc-depth=2",
                        "--split-level=2", "--css", str(css), "--metadata", f"title=每日简报 {today}",
                        "--metadata", "author=kindle-daily", "--metadata", "lang=zh-CN"], check=True)
    new = sorted(a["link"] for v in got.values() for a in v if a["link"])
    SEEN_FILE.write_text("\n".join(sorted(SEEN | set(new))[-5000:]) + "\n")
    (SITE / "version.txt").write_text(today + "\n")
    (SITE / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
    (SITE / "index.html").write_text("<meta name=robots content=noindex><meta charset=utf-8>"
                                     f"<p>每日简报 {today}：<a href='{today}.epub'>{today}.epub</a>（个人 Kindle 阅读用）</p>")
    print(f"完成：{today}.epub，共 {total} 篇")

if __name__ == "__main__":
    main()
