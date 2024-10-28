# YouTube Channel Data Integration and Summarization

本部分([yt.py](./yt_pod資料整合fin/yt.py))程式主要用於抓取 YouTube 頻道內容，並進行音頻下載和文字轉錄，以結構化的方式儲存成為摘要，便於進一步分析。

## 功能說明

1. **頻道 URL 解析**：自動判別頻道 URL 類型並提取頻道 ID。
2. **頻道資訊獲取**：根據頻道 ID 獲得頻道名稱、影片清單及上傳日期。
3. **MP3 下載**：透過 `yt-dlp` 下載音頻。
4. **音頻轉錄**：使用 OpenAI 的 `whisper` 模型生成音頻文字轉錄。
5. **摘要生成**：將轉錄文字分塊摘要，並整合成兩個區塊（1. 摘要 2. 未來走勢）。

---

# Podcast Data Integration and Summarization

本部分程式([podcast.py](./yt_pod資料整合fin/podcast.py))針對 Podcast RSS Feed 進行處理，包括過濾指定日期的節目，下載音檔並生成摘要。

## 功能說明

1. **Podcast RSS Feed 搜尋**：根據頻道名稱或網址來搜尋 RSS Feed。
2. **日期篩選**：透過 RSS Feed 過濾特定日期範圍內的影片。
3. **MP3 下載**：下載符合篩選條件的節目音頻。
4. **音頻轉錄**：使用 OpenAI 的 `whisper` 模型進行音檔文字轉錄。
5. **生成摘要**：使用 GPT-3.5 模型分析並總結轉錄的文字。

---

## 使用方法

### YouTube 頻道

1. **設定 API 金鑰**  
2. **輸入頻道 URL 和日期範圍**  
3. **執行程式**  
   - 自動解析頻道、下載音檔、轉錄並生成摘要。
4. **查看輸出**  
   - 結果將自動存至由頻道名稱建立的資料夾，並存為對應影片名稱的檔案。
### Podcast 頻道

1. **設定 API 金鑰**  
2. **輸入 Podcast URL 和日期範圍**  
3. **執行程式**  
   - 自動下載音檔、轉錄並生成摘要。
4. **查看輸出**
   - 結果將自動存至由頻道名稱建立的資料夾，並存為對應影片名稱的檔案。

## 環境需求

請參考 : [requirements.txt](./requirements.txt)

## 注意事項

- 該程式需用到 OpenAI 的 `whisper` 和 GPT-3.5 模型。
- 需自行申請 OpenAI API 金鑰和 Google API 金鑰。

## 授權

本專案基於 MIT 許可證開源。

## 開發過程

我先深入理解客戶需求，釐清所需的功能，包括 URL 解析、音頻下載、轉錄和摘要生成。隨後分步開發每項功能，並在最終階段整合所有功能。為了客戶的使用便利性，調整了輸出的路徑及支援多頻道輸入，實現一次處理多個頻道的功能。
