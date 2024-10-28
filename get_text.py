import whisper

# 加載 Whisper 模型
model = whisper.load_model("base")  # 或使用 "small", "medium", "large" 等型號
output_file = "transcription_test.txt"

# 將音頻文件轉換為文本
def transcribe_audio_with_whisper(audio_file):
    result = model.transcribe(audio_file, language='zh')
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result['text'])
    return result['text']
    

# 替換為下載的音頻文件路徑
audio_file_path = "/Users/tseng/Desktop/code/case/python/2023⧸12⧸25(一)2023大牛市 漲完了嗎？ 標普連八紅 上證連五黑 歐美股市脫鉤？【早晨財經速解讀】.mp3"
transcription = transcribe_audio_with_whisper(audio_file_path)

print(f"轉錄的文字已保存至 {output_file}")