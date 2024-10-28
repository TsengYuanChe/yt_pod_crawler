from googleapiclient.discovery import build

api_key = "AIzaSyBH1SjIqdyp9YvE34WqAVMWiuzYs6EqYsw"
youtube = build('youtube', 'v3', developerKey=api_key)

import re

def extract_channel_id(url):
    handle_match = re.match(r'https://www\.youtube\.com/@([^/]+)', url)
    if handle_match:
        handle = handle_match.group(1)
        return get_channel_id_from_handle(handle)

    id_match = re.match(r'https://www\.youtube\.com/channel/([^/]+)', url)
    if id_match:
        return id_match.group(1)
    
    custom_match = re.match(r'https://www\.youtube\.com/(c/|)([^/]+)', url)
    if custom_match:
        custom_url = custom_match.group(2)
        return get_channel_id_from_custom_url(custom_url)

    return None

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

def get_channel_id_from_custom_url(custom_url):
    # 使用 YouTube API
    youtube = build('youtube', 'v3', developerKey=api_key)

    # 通過 YouTube API 查詢頻道資料
    request = youtube.search().list(
        part='snippet',
        q=custom_url,  # 使用自定義 URL 進行查詢
        type='channel',
        maxResults=1
    )
    response = request.execute()

    # 如果有結果，返回頻道 ID
    if response['items']:
        return response['items'][0]['snippet']['channelId']
    else:
        return None  # 如果查詢無結果，返回 None

channel_url = 'https://www.youtube.com/@yutinghaofinance/streams'
channel_id = extract_channel_id(channel_url)

print(f"Channel ID: {channel_id}")