import feedparser
import requests
import os

# RSS feed URL
rss_url = 'https://feeds.soundon.fm/podcasts/954689a5-3096-43a4-a80b-7810b219cef3.xml'

# 解析 RSS feed
feed = feedparser.parse(rss_url)

# 確定下載目錄
download_folder = 'podcast_episodes'
os.makedirs(download_folder, exist_ok=True)

videos = feed.entries
first_video = videos[0]
print(first_video.enclosures[0]['href'])

# 遍歷所有項目
#for entry in feed.entries:
    # 顯示節目標題
   # print(entry)
   # print(f"Downloading: {entry.title}")
    
    # 取得音頻檔案的 URL
   # audio_url = entry.enclosures[0]['href']
    
    # 下載音頻檔案
   # response = requests.get(audio_url)
   # audio_filename = os.path.join(download_folder, f"{entry.title}.mp3")
    
    # 將音頻保存為 MP3 檔案
   # with open(audio_filename, 'wb') as audio_file:
   #     audio_file.write(response.content)
    
   # print(f"Saved: {audio_filename}")

#print("所有音頻已下載完畢！")