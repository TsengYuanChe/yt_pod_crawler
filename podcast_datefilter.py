import feedparser
from datetime import datetime
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

def filter_podcasts_by_date(feed_url, start_date, end_date):
    feed = feedparser.parse(feed_url)
    filtered_entries = []

    for entry in feed.entries:
        # 提取發布日期並轉換為 datetime 對象
        pub_date = datetime(*entry.published_parsed[:6])  # 解析日期

        # 篩選符合日期範圍的節目
        if start_date <= pub_date <= end_date:
            filtered_entries.append(entry)

    return filtered_entries

# 範例用法
feed_url = 'https://feeds.soundon.fm/podcasts/954689a5-3096-43a4-a80b-7810b219cef3.xml'
start_date = datetime(2023, 12, 21)
end_date = datetime(2023, 12, 31)
filtered_podcasts = filter_podcasts_by_date(feed_url, start_date, end_date)

# 打印篩選結果
for podcast in filtered_podcasts:
    print(f"標題: {podcast.title}, 發布日期: {podcast.published}")