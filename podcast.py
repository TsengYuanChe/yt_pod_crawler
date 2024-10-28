import requests, os, whisper, openai, warnings
from datetime import datetime
import feedparser

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

openai.api_key = "Your_OpenAI_API" # openai api
model = whisper.load_model("base") # 載入whisper model, 1.tiny, 2.base, 3.small, 4.medium, 5.large，越大越準，但佔越多內存，需要更多計算時間。

# 用頻道名稱或網址來收尋頻道RSS Feed
def search_podcast(podcast_name):
    
    url = f"https://itunes.apple.com/search?term={podcast_name}&entity=podcast"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  
        
        data = response.json()
        
        return data.get('results', [])
    except requests.exceptions.RequestException as e:
        print(f"發生錯誤: {e}")
        return []

# 根據日期來過濾頻道內的影片
def filter_podcasts_by_date(feed_url, start_date, end_date):
    feed = feedparser.parse(feed_url)
    filtered_entries = []

    for entry in feed.entries:
        pub_date = datetime(*entry.published_parsed[:6])

        if start_date <= pub_date <= end_date:
            filtered_entries.append(entry)

    return filtered_entries

# 下載影片的mp3檔
def get_podcasts_mp3s(filtered_podcasts):
    audio_url = filtered_podcasts.enclosures[0]['href']
    response = requests.get(audio_url)
    audio_filename = os.path.join(".", "voicep.mp3")
    with open(audio_filename, 'wb') as audio_file:
        audio_file.write(response.content)

# 用whisper生成音檔的文字
def transcribe_audio_with_whisper(audio_file):
    result = model.transcribe(audio_file, language='zh')
    return result['text']
    
# 讀取whisper生成的文字並生成摘要
def generate_summary(video_transcript):
    part_summaries = []
    transcript_parts = [video_transcript[i:i+3000] for i in range(0, len(video_transcript), 3000)]
    for part in transcript_parts:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一個針對財金相關內容的專業訊息整合生成器。"},
                {"role": "user", "content": "將稍後要整理的內容分常兩個區塊顯示，1.Summy 2.Future"},
                {"role": "user", "content": f"請閱讀以下內容：{part}，根據這些內容整理出: 1.內容中有討論到的一些主題，列出所有的討論主題，將所有主題都當作是一個子標題，並針對這些主題做出一個詳細的整理。 2.整理出內容中對未來情勢的判斷，包括股市。如果有提及實際的數字或是相關個股請直接列出來。一樣列出一些子標題。"},
                {"role": "user", "content": "將整理出來後的資料做檢查，確認所有提及的主題都有適當的詳細內容，並且有列出所有提及的個股和預測的未來走勢"},
            ],
            max_tokens=1000,  
            temperature=0.7  
        )
        part_summaries.append(response['choices'][0]['message']['content'])

    combined_summary = "\n".join(part_summaries)
    
    final_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "你是一個專業的訊息整合生成器。"},
                {"role": "user", "content": f"以下內容來自同篇報導，請將以下內容整合：{combined_summary}，將1.Summy的所有資料合併，將2.Future的所有資料合併，但不要刪除任何資料。最後一樣分為1.Summy 2.Future兩個段落輸出。"}
            ],
            max_tokens=1000,
            temperature=0.7
    )
    return final_response.choices[0].message['content']

# 建立input，輸入所有連結、開始日期、結束日期
def get_urls_and_dates():
    podcast_list = []
    print("請輸入網址，按 Enter 鍵結束。")
    while True:
        url = input("輸入網址（或直接按 Enter 鍵結束）：")
        if url == "":
            break
        podcast_list.append(url)

    while True:
        start_date_str = input("請輸入開始日期 (格式: YYYYMMDD): ")
        end_date_str = input("請輸入結束日期 (格式: YYYYMMDD): ")

        try:
            start_date = datetime.strptime(start_date_str, "%Y%m%d")
            end_date = datetime.strptime(end_date_str, "%Y%m%d")
            if end_date < start_date:
                print("錯誤：結束日期不能早於開始日期，請重新輸入。")
            else:
                break  
        except ValueError:
            print("日期格式錯誤，請使用 YYYYMMDD 格式。")

    return podcast_list, start_date, end_date

podcast_list, start_date, end_date = get_urls_and_dates()

for podcast_url in podcast_list:
    podcast_data = search_podcast(podcast_url)
    folder_path = f'{podcast_data[0]['collectionName']}的folder'
    os.makedirs(folder_path, exist_ok=True)
    feed_url = podcast_data[0]['feedUrl']
    filtered_podcasts = filter_podcasts_by_date(feed_url, start_date, end_date)
    remain_videos = len(filtered_podcasts)
    
    print(f"範圍內的影片總數: {len(filtered_podcasts)}")
    for video in filtered_podcasts:
        get_podcasts_mp3s(video)
        transcription = transcribe_audio_with_whisper('/Users/tseng/Desktop/code/case/python/voicep.mp3')
        summary = generate_summary(transcription)
        output_path = os.path.join(folder_path, f"Summary of {video.title}.txt")
        with open(output_path, "w", encoding="utf-8") as f:      
            f.write(f"標題: {video.title}")        
            f.write(f"上傳日期: {video.published}")      
            f.write(f"摘要:\n{summary}")        
            
        remain_videos = remain_videos-1
        print(f"摘要已保存至 {output_path}, 剩下 {remain_videos} 個影片")
    print(f"下載完成！摘要已全部保存至 {folder_path}")      
