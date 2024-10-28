from googleapiclient.discovery import build
from datetime import datetime

def get_upload_playlist_id(channel_id):
    return 'UU' + channel_id[2:]

def get_videos_in_date_range(channel_id, api_key, start_date, end_date):
    youtube = build('youtube', 'v3', developerKey=api_key)
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

channel_id = 'UC0lbAQVpenvfA2QqzsRtL_g'  
api_key = "AIzaSyBH1SjIqdyp9YvE34WqAVMWiuzYs6EqYsw"  

# 設置日期範圍
start_date = datetime(2023, 12, 25)
end_date = datetime(2023, 12, 31)

videos = get_videos_in_date_range(channel_id, api_key, start_date, end_date)

print(f"範圍內的影片總數: {len(videos)}")
for video in videos:
    print(f"標題: {video['title']}, 上傳日期: {video['publishedAt']}, 視頻 ID: {video['videoId']}")