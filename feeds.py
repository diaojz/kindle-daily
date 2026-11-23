# 每日简报订阅源。limit = 每期最多几篇；full = True 表示 RSS 已带全文，不再抓原网页。
SECTIONS = [
    ("AI 前沿", [
        ("Simon Willison", "https://simonwillison.net/atom/everything/", 6, True),
        ("Latent Space", "https://www.latent.space/feed", 1, True),
        ("Import AI", "https://importai.substack.com/feed", 1, True),
        ("Interconnects", "https://www.interconnects.ai/feed", 1, True),
        ("One Useful Thing", "https://www.oneusefulthing.org/feed", 1, True),
        ("Dwarkesh", "https://www.dwarkesh.com/feed", 1, True),
        ("OpenAI", "https://openai.com/news/rss.xml", 3, False),
        ("量子位", "https://www.qbitai.com/feed", 5, False),
        ("宝玉", "https://baoyu.io/feed.xml", 2, False),
    ]),
    ("科技与商业", [
        ("Stratechery", "https://stratechery.com/feed/", 2, True),
        ("The Pragmatic Engineer", "https://newsletter.pragmaticengineer.com/feed", 1, True),
        ("MIT Technology Review", "https://www.technologyreview.com/feed/", 3, True),
        ("极客公园", "https://www.geekpark.net/rss", 3, True),
        ("少数派", "https://sspai.com/feed", 3, False),
        ("Hacker News 精选", "https://hnrss.org/best", 5, False),
    ]),
    ("世界新闻", [
        ("FT 中文网", "https://www.ftchinese.com/rss/feed", 5, False),
        ("BBC 中文", "https://feeds.bbci.co.uk/zhongwen/simp/rss.xml", 6, False),
        ("纽约时报中文网", "https://cn.nytimes.com/rss/", 5, False),
    ]),
    ("深度长文", [
        ("阮一峰·科技爱好者周刊", "https://www.ruanyifeng.com/blog/atom.xml", 1, True),
        ("Astral Codex Ten", "https://www.astralcodexten.com/feed", 1, True),
        ("Noahpinion", "https://www.noahpinion.blog/feed", 1, True),
        ("Farnam Street", "https://fs.blog/feed/", 1, True),
        ("Aeon", "https://aeon.co/feed.rss", 2, False),
        ("Quanta Magazine", "https://www.quantamagazine.org/feed/", 2, False),
        ("Martin Fowler", "https://martinfowler.com/feed.atom", 1, True),
    ]),
]
