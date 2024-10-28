import openai, whisper, yt_dlp, os, re, warnings
from googleapiclient.discovery import build
from datetime import datetime

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

api_key = "AIzaSyBH1SjIqdyp9YvE34WqAVMWiuzYs6EqYsw" # Google API
# openai api
openai.api_key = "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"
model = whisper.load_model("base") # 載入whisper model, 1.tiny, 2.base, 3.small, 4.medium, 5.large，越大越準，但佔越多內存，需要更多計算時間。
youtube = build('youtube', 'v3', developerKey=api_key) # 指定 google api 要使用的服務：YouTube Data API 的第 3 版 

# 判斷輸入的url是哪個形式
def extract_channel_id(url):
    # Handle 網址的話交給get_channel_id_from_handle處理
    handle_match = re.match(r'https://www\.youtube\.com/@([^/]+)', url)
    if handle_match:
        handle = handle_match.group(1)
        return get_channel_id_from_handle(handle)

    # ID 網址的話直接返回channel/後面的部分
    id_match = re.match(r'https://www\.youtube\.com/channel/([^/]+)', url)
    if id_match:
        return id_match.group(1)

    # 自定義 URL 網址的話交給get_channel_id_from_custom_url處理
    custom_match = re.match(r'https://www\.youtube\.com/(c/|)([^/]+)', url)
    if custom_match:
        custom_url = custom_match.group(2)
        return get_channel_id_from_custom_url(custom_url)
    
    # 網址不正確的話返回None
    return None

# 處理 Handle 網址
def get_channel_id_from_handle(handle):
    request = youtube.search().list(
        part='snippet',
        q=handle,
        type='channel'
    )
    response = request.execute()

    if 'items' in response and len(response['items']) > 0:
        for item in response['items']:
            snippet = item['snippet']
            if 'customUrl' in snippet:
                custom_url = snippet['customUrl']
                if handle.lower() in custom_url.lower():
                    return item['id'].get('channelId', None)
            elif 'channelId' in item['id']:
                return item['id']['channelId']

    return None

# 處理自定義 URL 網址
def get_channel_id_from_custom_url(custom_url):
    request = youtube.search().list(
        part='snippet',
        q=custom_url,
        type='channel',
        maxResults=1
    )
    response = request.execute()

    if response['items']:
        return response['items'][0]['snippet']['channelId']
    else:
        return None  

# 獲得頻道名稱來建立資料夾
def get_channel_name(channel_id):
    request = youtube.channels().list(
        part='snippet',
        id=channel_id
    )
    response = request.execute()

    if 'items' in response and len(response['items']) > 0:
        channel_name = response['items'][0]['snippet']['title']
        return channel_name
    else:
        return None
    
#用channel id獲得播放清單
def get_upload_playlist_id(channel_id):
    return 'UU' + channel_id[2:]

#用channel id獲得特定期間內的video id
def get_videos_in_date_range(channel_id, start_date, end_date):
    upload_playlist_id = get_upload_playlist_id(channel_id)
    video_ids = []
    next_page_token = None
    
    while True:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=upload_playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        
        for item in response['items']:
            video_ids.append(item['snippet']['resourceId']['videoId'])
        
        next_page_token = response.get('nextPageToken')
        
        if not next_page_token:
            break
    
    videos_in_date_range = []
    for video_id in video_ids:
        video_request = youtube.videos().list(
            part="snippet",
            id=video_id
        )
        video_response = video_request.execute()
        video_data = video_response['items'][0]['snippet']
        
        published_at = datetime.strptime(video_data['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
        if start_date <= published_at <= end_date:
            videos_in_date_range.append({
                'videoId': video_id,
                'title': video_data['title'],
                'publishedAt': published_at
            })
    
    return videos_in_date_range

#用video id下載影片的mp3檔
def download_audio_yt(video_url, output_path="."):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_path}/voice.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        print("音頻下載成功")
    except Exception as e:
        print(f"下載音頻時出錯: {e}")


# 用whisper讀取mp3檔
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

# 建立input，輸入所有連結、開始日期、結束日期
def get_urls_and_dates():
    channel_list = []
    print("請輸入網址，按 Enter 鍵結束。")
    while True:
        url = input("輸入網址（或直接按 Enter 鍵結束）：")
        if url == "":
            break
        channel_list.append(url)

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

    return channel_list, start_date, end_date

channel_list, start_date, end_date = get_urls_and_dates()

for channel_url in channel_list:
    channel_id = extract_channel_id(channel_url) #從url獲得id
    channel_name = get_channel_name(channel_id) #從id獲得名稱
    folder_path = f"{channel_name}的summaries" #用名稱定義資料夾名稱
    os.makedirs(folder_path, exist_ok=True) #資料夾不存在的話建立資料夾
    videos = get_videos_in_date_range(channel_id, start_date, end_date) #根據id,日期區間來獲得所有影片的id
    remain_videos = len(videos) #用來計算尚未下載的影片數

    print(f"範圍內的影片總數: {len(videos)}")
    for video in videos:
        videoid = video['videoId']
        video_url = f"https://www.youtube.com/watch?v={videoid}"
        download_audio_yt(video_url)
        transcription = transcribe_audio_with_whisper('/Users/tseng/Desktop/code/case/python/voice.mp3')
        summary = generate_summary(transcription)
        output_path = os.path.join(folder_path, f"Summary of {video['videoId']}.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"標題: {video['title']}")        
            f.write(f"上傳日期: {video['publishedAt']}")     
            f.write(f"影片ID: {video['videoId']}\n")         
            f.write(f"摘要:\n{summary}")              
        remain_videos = remain_videos-1
        print(f"摘要已保存至 {output_path}, 剩下 {remain_videos} 個影片")
        
    print(f"下載完成！摘要已全部保存至 {folder_path}")