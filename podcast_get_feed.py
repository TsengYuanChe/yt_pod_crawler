import requests, os, whisper, openai, warnings
from datetime import datetime
import feedparser

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

openai.api_key = "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"
model = whisper.load_model("base")

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

def get_podcasts_mp3s(filtered_podcasts):
    audio_url = filtered_podcasts.enclosures[0]['href']
    response = requests.get(audio_url)
    audio_filename = os.path.join(".", "voicep.mp3")
    with open(audio_filename, 'wb') as audio_file:
        audio_file.write(response.content)
    
def transcribe_audio_with_whisper(audio_file):
    result = model.transcribe(audio_file, language='zh')
    return result['text']
    
def generate_summary(video_transcript):
    part_summaries = []
    transcript_parts = [video_transcript[i:i+3000] for i in range(0, len(video_transcript), 3000)]
    for part in transcript_parts:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一個專業的摘要生成器。"},
                {"role": "user", "content": f"請對以下內容生成摘要：{part}"}
            ],
            max_tokens=150,  # 可以根據需要調整生成字數
            temperature=0.7  # 控制生成的隨機性，0.7 是比較平衡的選擇
        )
        part_summaries.append(response['choices'][0]['message']['content'])

    combined_summary = "\n".join(part_summaries)
    
    final_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "你是一個專業的摘要生成器。"},
                {"role": "user", "content": f"請對以下內容生成摘要：{combined_summary}"}
            ],
            max_tokens=150,
            temperature=0.7
    )
    # 返回生成的摘要
    return final_response.choices[0].message['content']


podcast_name = "https://podcasts.apple.com/tw/podcast/gooaye-%E8%82%A1%E7%99%8C/id1500839292"
start_date = datetime(2023, 12, 25)
end_date = datetime(2023, 12, 31)
podcast_data = search_podcast(podcast_name)
folder_path = f'{podcast_data[0]['collectionName']}的folder'
os.makedirs(folder_path, exist_ok=True)
feed_url = podcast_data[0]['feedUrl']
filtered_podcasts = filter_podcasts_by_date(feed_url, start_date, end_date)
print(f"範圍內的影片總數: {len(filtered_podcasts)}")
for video in filtered_podcasts:
    get_podcasts_mp3s(video)
    transcription = transcribe_audio_with_whisper('/Users/tseng/Desktop/code/case/python/voicep.mp3')
    summary = generate_summary(transcription)
    output_path = os.path.join(folder_path, f"Summary of {video.title}.txt")
    with open(output_path, "w", encoding="utf-8") as f:        
        f.write(f"摘要:\n{summary}")              
