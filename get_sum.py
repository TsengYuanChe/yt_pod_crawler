import openai

openai.api_key = "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"

txt_file = "/Users/tseng/Desktop/code/case/python/transcription_test.txt"  # 替換為您的文件名
with open(txt_file, 'r', encoding='utf-8') as file:
    file_content = file.read()


def generate_summary(video_transcript):
    # 發送請求到 chat-completion 端點，使用聊天模型生成摘要
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # 或 gpt-4，如果你有權限
        messages=[
            {"role": "system", "content": "你是一個針對財金相關內容的專業訊息整合生成器。"},
            {"role": "user", "content": f"請閱讀以下內容：{video_transcript}，根據這些內容整理出: 1.內容中有討論到的一些主題，並簡單敘述這些主題的內容。 2.整理出內容中對未來情勢的判斷，包括股市。 "},
            {"role": "user", "content": "將前面整理出的內容分常兩個區塊顯示，1.Summy 2.Future"},
        ],
        max_tokens=1000,  # 可以根據需要調整生成字數
        temperature=0.7  # 控制生成的隨機性，0.7 是比較平衡的選擇
    )

    # 返回生成的摘要
    return response.choices[0].message['content']

summary = generate_summary(file_content)
video_title = "影片的標題"
upload_date = "2024-01-01" 
video_id = "abcd1234"
output_summary_file = "summary.txt"
with open(output_summary_file, "w", encoding="utf-8") as f:
    f.write(f"標題: {video_title}")        
    f.write(f"上傳日期: {upload_date}")     
    f.write(f"影片ID: {video_id}\n")         
    f.write(f"摘要:\n{summary}")              

print(f"摘要已保存至 {output_summary_file}")