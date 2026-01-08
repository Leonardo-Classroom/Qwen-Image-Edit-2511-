# Qwen-Image-Edit-2511-
因應B站網友的需求寫的批量改圖功能，使用的是刘悦的技术博客提供的Qwen-Image-Edit-2511，將"auto_process.py"放置於專案根目錄，執行"py312\python.exe auto_process.py"即可，code中可以改輸入輸出的文件夾


# auto_process.py 使用教學

## 簡介

`auto_process.py` 是一個批量圖片處理腳本，可以自動調用 ComfyUI API 對多張圖片進行批量編輯處理，無需在 Gradio UI 中逐張手動操作。

## 前置準備

### 1. 啟動 ComfyUI 服務

**重要：必須先啟動 ComfyUI 服務，等待完全啟動後才能執行批量處理腳本。**

1. 找到 **"刘悦的技术博客(Qwen-Edit-2511-rapid-GGUF)"** 目錄
2. 雙擊執行 `開始.bat`
3. 等待 ComfyUI 完全啟動
   - 觀察控制台輸出
   - 看到類似 "ComfyUI 服務已就緒" 或服務器啟動完成的提示
   - 通常需要等待 30 秒到 2 分鐘（取決於電腦配置）

⚠️ **注意：如果 ComfyUI 未完全啟動就執行批量處理，會導致連接失敗！**

### 2. 準備輸入圖片

將需要批量處理的圖片放入指定的輸入目錄：

- 默認輸入目錄：`D:\OneDrive\Desktop\test\input`
- 支援的圖片格式：`.jpg`, `.jpeg`, `.png`, `.bmp`, `.webp`

## 執行批量處理

1. 打開命令提示字元（CMD）或 PowerShell
2. 切換到專案目錄：
   ```bash
   cd /d F:\AI\Qwen-Image-Edit-2511
   ```
3. 執行批量處理腳本：
   ```bash
   py312\python.exe auto_process.py
   ```

## 配置說明

在執行前，可以根據需求修改 `auto_process.py` 中的配置參數：

### 基本配置

```python
# 輸入輸出目錄
INPUT_DIR = r"D:\OneDrive\Desktop\test\input"   # 批量輸入圖片目錄
OUTPUT_DIR = r"D:\OneDrive\Desktop\test\output"  # 輸出目錄

# 工作流配置
WORKFLOW_PATH = "work/QwenImageEdit_2511_GGUF_rapid.json"
```

### 提示詞配置

```python
PROMPT_TEXT = "加上面光"        # 正面提示詞
NEGATIVE_PROMPT_TEXT = ""       # 負面提示詞
```

**提示詞範例：**
- `"穿上外套"` - 為圖片中的人物添加外套
- `"改成紅色衣服"` - 將衣服顏色改為紅色
- `"添加帽子"` - 為人物添加帽子
- `"加上面光"` - 添加面部光線效果
- `"背景改成海邊"` - 更換背景為海邊場景

### 採樣器配置

```python
SAMPLING_STEPS = 4  # 採樣步數，建議 4-8 步
```

**注意：** CFG Scale 已設定為使用工作流預設值，不需要手動配置。

### Lora 配置

```python
LORA_1_NAME = "None"           # Lora 1 模型名稱
LORA_1_STRENGTH = 1.0          # Lora 1 強度 (0.0 - 1.0)

LORA_2_NAME = "None"           # Lora 2 模型名稱
LORA_2_STRENGTH = 1.0          # Lora 2 強度

LORA_3_NAME = "None"           # Lora 3 模型名稱
LORA_3_STRENGTH = 1.0          # Lora 3 強度
```

設定為 `"None"` 表示不使用該 Lora。

### 其他配置

```python
SKIP_PROCESSED = True  # 是否跳過已處理的圖片
```

## 處理流程

腳本執行時會按照以下流程處理：

1. **載入配置** - 讀取工作流和配置參數
2. **掃描圖片** - 獲取輸入目錄中的所有圖片
3. **過濾已處理** - 如果啟用 `SKIP_PROCESSED`，會跳過已處理的圖片
4. **逐張處理** - 對每張圖片執行以下操作：
   - 上傳圖片到 ComfyUI
   - 更新工作流參數（提示詞、Lora、採樣器等）
   - 提交任務到處理隊列
   - 等待處理完成
   - 下載處理結果
5. **保存結果** - 將處理後的圖片保存到輸出目錄

## 輸出結果

處理完成的圖片會保存在輸出目錄中：

- 默認輸出目錄：`D:\OneDrive\Desktop\test\output`
- 檔名格式：`{原檔名}_processed.{副檔名}`

**範例：**
- 輸入：`photo001.jpg`
- 輸出：`photo001_processed.jpg`

## 執行範例

### 完整操作流程

```
步驟 1: 啟動 ComfyUI 服務
---------------------------------------
> 雙擊執行 "開始.bat"
> 等待服務啟動完成...
> ✓ ComfyUI 服務已就緒

步驟 2: 準備圖片
---------------------------------------
> 將 10 張圖片放入 D:\OneDrive\Desktop\test\input
> 支援格式: .jpg, .png, .webp

步驟 3: 執行批量處理
---------------------------------------
> py312\python.exe auto_process.py

============================================================
ComfyUI 批量圖片處理工具
============================================================
輸入目錄: D:\OneDrive\Desktop\test\input
輸出目錄: D:\OneDrive\Desktop\test\output
ComfyUI 服務器: http://127.0.0.1:8187

提示詞配置:
  正面提示詞: 加上面光
  反面提示詞: (未設置)

採樣器配置:
  CFG Scale: 使用工作流預設值
  採樣步數: 4

Lora 配置:
  Lora 1: None (強度: 1.0)

工作流: work/QwenImageEdit_2511_GGUF_rapid.json
============================================================

載入工作流模板...
✓ 工作流已載入

找到 10 個圖片文件
✓ 待處理: 10 個圖片

進度: 1/10
============================================================
處理圖片: photo001.jpg
============================================================
  上傳圖片: photo001.jpg
  ✓ 上傳成功: photo001.jpg
  ✓ 任務已提交: a1b2c3d4-e5f6-7890-abcd-ef1234567890
  等待處理完成...
  ✓ 處理完成!
  [調試] ComfyUI 返回的檔名: ComfyUI_00001_.png
  下載: photo001_processed.png
  ✓ 已保存: D:\OneDrive\Desktop\test\output\photo001_processed.png
✓ 成功處理: 1 個輸出文件

進度: 2/10
...

============================================================
批量處理完成!
============================================================
成功: 10
失敗: 0
總計: 10
輸出目錄: D:\OneDrive\Desktop\test\output
============================================================
```

## 常見問題

### Q1: 執行時出現 "連接失敗" 錯誤

**原因：** ComfyUI 服務未啟動或未完全啟動

**解決方法：**
1. 確認已執行 `開始.bat`
2. 等待 ComfyUI 完全啟動（通常需要 30 秒到 2 分鐘）
3. 檢查 ComfyUI 控制台是否有錯誤信息
4. 確認端口 8187 未被其他程序佔用

### Q2: 如何修改輸入/輸出目錄？

**解決方法：**

編輯 `auto_process.py` 文件，修改以下配置：

```python
INPUT_DIR = r"你的輸入目錄路徑"
OUTPUT_DIR = r"你的輸出目錄路徑"
```

**注意：** 路徑前面要加 `r` 前綴，或使用正斜線 `/`

### Q3: 如何跳過已處理的圖片？

**解決方法：**

確保配置中 `SKIP_PROCESSED = True`（默認已啟用）

腳本會自動檢查輸出目錄，如果發現 `{檔名}_processed.*` 已存在，就會跳過該圖片。

### Q4: 處理速度很慢怎麼辦？

**可能原因：**
- GPU 性能不足
- 採樣步數設置過高
- 同時處理的圖片解析度過大

**解決方法：**
1. 減少採樣步數（例如從 8 改為 4）
2. 確保 GPU 有足夠的 VRAM
3. 關閉其他佔用 GPU 的程序

### Q5: 處理失敗的圖片會怎樣？

**行為：**
- 腳本會顯示錯誤信息和堆疊追蹤
- 繼續處理下一張圖片
- 最後統計中會顯示失敗數量

**建議：**
- 查看錯誤信息找出原因
- 檢查失敗的圖片是否損壞或格式不支援
- 確認工作流配置是否正確

## 技術細節

### 工作流節點映射

當前腳本針對 `QwenImageEdit_2511_GGUF_rapid.json` 工作流配置：

| 節點 ID | 節點類型 | 功能 | 更新內容 |
|---------|----------|------|----------|
| 197 | LoadImage | 載入輸入圖片 | 圖片檔名 |
| 204 | TextEncodeQwenImageEditPlus | 正面提示詞編碼 | 提示詞文本 |
| 192 | CLIPTextEncode | 反面提示詞編碼 | 反面提示詞文本 |
| 216 | Lora Loader Stack | Lora 載入器 | Lora 名稱和強度 |
| 31 | KSampler | 採樣器 | Seed、採樣步數 |
| 219 | ImageScaleToTotalPixels | 圖片縮放 | （可選）圖片大小 |

### API 端點

腳本使用以下 ComfyUI API 端點：

- `POST /upload/image` - 上傳圖片
- `POST /prompt` - 提交工作流任務
- `GET /history/{prompt_id}` - 查詢任務狀態
- `GET /view` - 下載處理結果

### 超時設置

默認超時時間為 600 秒（10 分鐘），可在 `wait_for_completion()` 函數中修改：

```python
def wait_for_completion(prompt_id: str, timeout: int = 600):
    # 改為 1200 秒（20 分鐘）
    # timeout: int = 1200
```

## 注意事項

1. **確保 ComfyUI 服務已啟動** - 這是最重要的前提條件
2. **端口配置** - 確保 `config.py` 中的 `comfyui_port` 與實際服務端口一致（默認 8187）
3. **資源佔用** - 批量處理會佔用大量 GPU 資源，建議分批處理
4. **磁碟空間** - 確保輸出目錄有足夠的磁碟空間
5. **工作流兼容性** - 不同工作流的節點 ID 可能不同，需要相應調整代碼
6. **CFG 值** - 當前版本使用工作流預設的 CFG 值，不進行覆蓋

## 相關文件

- `auto_process.py` - 批量處理主程序
- `config.py` - 端口配置文件
- `work/QwenImageEdit_2511_GGUF_rapid.json` - 工作流配置文件
- `開始.bat` - ComfyUI 服務啟動腳本

## 技術支持

如遇到問題，請檢查：

1. ComfyUI 控制台的錯誤信息
2. 批量處理腳本的錯誤輸出
3. 工作流 JSON 文件是否正確
4. 圖片文件是否損壞或格式不支援

---

**最後更新：** 2026-01-08

