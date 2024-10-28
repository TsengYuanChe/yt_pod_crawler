import yt_dlp

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

videoid = '7GnuDxct1Bs'
video_url = f"https://www.youtube.com/watch?v={videoid}"
download_audio_yt(video_url)