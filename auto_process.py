#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量圖片處理腳本
模仿 Gradio UI 調用 ComfyUI API 進行批量圖片編輯
"""

import os
import sys
import json
import uuid
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, Any, List
import time

# 導入配置
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
from config import comfyui_port

# ComfyUI 服務器地址
COMFYUI_SERVER = f"127.0.0.1:{comfyui_port}"
COMFYUI_URL = f"http://{COMFYUI_SERVER}"

# 工作流配置
WORKFLOW_PATH = "work/QwenImageEdit_2511_GGUF_rapid.json"  # 使用全圖編輯工作流

# 批量處理配置
INPUT_DIR = r"D:\OneDrive\Desktop\test\input"  # 批量輸入圖片目錄
OUTPUT_DIR = r"D:\OneDrive\Desktop\test\output2"  # 輸出目錄

# 提示詞配置
PROMPT_TEXT = "戴上眼鏡"    # 正面提示詞
NEGATIVE_PROMPT_TEXT = ""   # 負面提示詞

# 採樣器配置
SAMPLING_STEPS = 4  # 採樣步數，建議 4-8 步（使用 Lightning 模型時）

# 是否跳過已處理的圖片（根據輸出目錄中的檔案判斷）
SKIP_PROCESSED = True

# Lora 配置（設定為 "None" 表示不使用該 Lora）
LORA_1_NAME = "None" 
LORA_1_STRENGTH = 1.0
LORA_2_NAME = "None"  # 第二個 Lora，不使用則設為 "None"
LORA_2_STRENGTH = 1.0
LORA_3_NAME = "None"  # 第三個 Lora，不使用則設為 "None"
LORA_3_STRENGTH = 1.0

# 支援的圖片格式
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}


def load_workflow(workflow_path: str) -> Dict[str, Any]:
    """載入工作流 JSON 文件"""
    with open(workflow_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def upload_image_to_comfyui(image_path: str) -> Dict[str, str]:
    """
    上傳圖片到 ComfyUI
    
    Returns:
        {"name": filename, "subfolder": subfolder, "type": type}
    """
    print(f"  上傳圖片: {os.path.basename(image_path)}")
    
    # 準備 multipart/form-data
    boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'
    
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    filename = os.path.basename(image_path)
    
    # 構建 multipart body
    body = []
    body.append(f'--{boundary}'.encode())
    body.append(f'Content-Disposition: form-data; name="image"; filename="{filename}"'.encode())
    body.append(b'Content-Type: image/jpeg')
    body.append(b'')
    body.append(image_data)
    body.append(f'--{boundary}'.encode())
    body.append(b'Content-Disposition: form-data; name="type"')
    body.append(b'')
    body.append(b'input')
    body.append(f'--{boundary}'.encode())
    body.append(b'Content-Disposition: form-data; name="overwrite"')
    body.append(b'')
    body.append(b'true')
    body.append(f'--{boundary}--'.encode())
    body.append(b'')
    
    body_bytes = b'\r\n'.join(body)
    
    # 發送請求
    req = urllib.request.Request(
        f"{COMFYUI_URL}/upload/image",
        data=body_bytes,
        headers={
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'Content-Length': str(len(body_bytes))
        }
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"  ✓ 上傳成功: {result['name']}")
            return result
    except Exception as e:
        print(f"  ✗ 上傳失敗: {e}")
        raise


def update_workflow_for_image(
    workflow: Dict[str, Any],
    uploaded_image: Dict[str, str],
    prompt: str,
    negative_prompt: str = "",
    sampling_steps: int = 4,
    lora_1_name: str = "None",
    lora_1_strength: float = 1.0,
    lora_2_name: str = "None",
    lora_2_strength: float = 1.0,
    lora_3_name: str = "None",
    lora_3_strength: float = 1.0
) -> Dict[str, Any]:
    """
    更新工作流配置

    Args:
        workflow: 原始工作流
        uploaded_image: 上傳的圖片信息 {"name": ..., "subfolder": ..., "type": ...}
        prompt: 正面提示詞
        negative_prompt: 反面提示詞（默認為空字符串）
        sampling_steps: 採樣步數（默認 4）
        lora_1_name: Lora 1 模型名稱
        lora_1_strength: Lora 1 強度 (0.0 - 1.0)
        lora_2_name: Lora 2 模型名稱（"None" 表示不使用）
        lora_2_strength: Lora 2 強度 (0.0 - 1.0)
        lora_3_name: Lora 3 模型名稱（"None" 表示不使用）
        lora_3_strength: Lora 3 強度 (0.0 - 1.0)
    """
    # 深拷貝工作流
    workflow = json.loads(json.dumps(workflow))

    # QwenImageEdit_2511_GGUF_rapid.json 的節點配置：
    # 更新 LoadImage 節點 (節點 197) - 主要輸入圖片
    if "197" in workflow:
        workflow["197"]["inputs"]["image"] = uploaded_image["name"]

    # 更新正向提示詞 (節點 204) - TextEncodeQwenImageEditPlus
    if "204" in workflow:
        workflow["204"]["inputs"]["prompt"] = prompt

    # 更新反面提示詞 (節點 192) - CLIPTextEncode
    if "192" in workflow:
        workflow["192"]["inputs"]["text"] = negative_prompt

    # 更新 Lora Loader Stack (節點 216) - 設定多個 Lora
    if "216" in workflow:
        workflow["216"]["inputs"]["lora_01"] = lora_1_name
        workflow["216"]["inputs"]["strength_01"] = lora_1_strength
        workflow["216"]["inputs"]["lora_02"] = lora_2_name
        workflow["216"]["inputs"]["strength_02"] = lora_2_strength
        workflow["216"]["inputs"]["lora_03"] = lora_3_name
        workflow["216"]["inputs"]["strength_03"] = lora_3_strength

    # 更新 KSampler (節點 31) - 採樣器配置
    if "31" in workflow:
        workflow["31"]["inputs"]["seed"] = int(time.time() * 1000) % (2**32)
        # CFG 使用工作流預設值，不進行覆蓋
        workflow["31"]["inputs"]["steps"] = sampling_steps

    return workflow


def queue_prompt(workflow: Dict[str, Any], client_id: str) -> str:
    """
    提交工作流到 ComfyUI 隊列

    Returns:
        prompt_id
    """
    prompt_id = str(uuid.uuid4())
    payload = {
        "prompt": workflow,
        "client_id": client_id,
        "prompt_id": prompt_id
    }

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        f"{COMFYUI_URL}/prompt",
        data=data,
        headers={'Content-Type': 'application/json'}
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            if 'error' in result:
                raise Exception(f"ComfyUI 錯誤: {result['error']}")
            print(f"  ✓ 任務已提交: {prompt_id}")
            return prompt_id
    except Exception as e:
        print(f"  ✗ 提交失敗: {e}")
        raise


def get_history(prompt_id: str) -> Dict[str, Any]:
    """獲取任務歷史記錄"""
    with urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}") as response:
        return json.loads(response.read().decode('utf-8'))


def wait_for_completion(prompt_id: str, timeout: int = 600) -> Dict[str, Any]:
    """
    等待任務完成

    Args:
        prompt_id: 任務 ID
        timeout: 超時時間（秒）

    Returns:
        任務歷史記錄
    """
    print(f"  等待處理完成...")
    start_time = time.time()

    while True:
        if time.time() - start_time > timeout:
            raise TimeoutError(f"任務超時 ({timeout}秒)")

        history = get_history(prompt_id)

        if prompt_id in history:
            task_info = history[prompt_id]
            if 'outputs' in task_info:
                print(f"  ✓ 處理完成!")
                return task_info

        time.sleep(2)


def download_output_images(task_info: Dict[str, Any], output_dir: str, original_filename: str) -> List[str]:
    """
    下載輸出圖片

    Returns:
        下載的文件路徑列表
    """
    os.makedirs(output_dir, exist_ok=True)
    downloaded_files = []

    outputs = task_info.get('outputs', {})

    for node_id, node_output in outputs.items():
        if 'images' in node_output:
            for idx, image_info in enumerate(node_output['images']):
                filename = image_info['filename']
                subfolder = image_info.get('subfolder', '')
                file_type = image_info.get('type', 'output')

                # 調試：顯示 ComfyUI 返回的原始檔名
                print(f"  [調試] ComfyUI 返回的檔名: {filename}")

                # 構建下載 URL
                params = {
                    'filename': filename,
                    'subfolder': subfolder,
                    'type': file_type
                }
                url = f"{COMFYUI_URL}/view?{urllib.parse.urlencode(params)}"

                # 生成輸出文件名
                base_name = Path(original_filename).stem
                ext = Path(filename).suffix
                output_filename = f"{base_name}_processed{ext}"
                output_path = os.path.join(output_dir, output_filename)

                # 下載圖片
                print(f"  下載: {output_filename}")
                with urllib.request.urlopen(url) as response:
                    with open(output_path, 'wb') as f:
                        f.write(response.read())

                downloaded_files.append(output_path)
                print(f"  ✓ 已保存: {output_path}")

    return downloaded_files


def is_already_processed(input_filename: str, output_dir: str) -> bool:
    """
    檢查圖片是否已經處理過

    Args:
        input_filename: 輸入檔案的檔名（不含路徑）
        output_dir: 輸出目錄

    Returns:
        True 如果已處理，False 如果未處理
    """
    if not os.path.exists(output_dir):
        return False

    # 獲取基礎檔名（不含副檔名）
    base_name = Path(input_filename).stem

    # 檢查輸出目錄中是否存在對應的處理後檔案
    # 可能的檔名格式：
    # - {base_name}_processed.png
    # - {base_name}_processed.jpg

    for file in os.listdir(output_dir):
        file_stem = Path(file).stem
        # 檢查是否匹配 base_name_processed
        if file_stem == f"{base_name}_processed":
            return True

    return False


def get_image_files(directory: str) -> List[str]:
    """獲取目錄下所有支援的圖片文件"""
    image_files = []

    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            ext = os.path.splitext(file)[1].lower()
            if ext in SUPPORTED_FORMATS:
                image_files.append(file_path)

    return sorted(image_files)


def process_single_image(image_path: str, workflow_template: Dict[str, Any], client_id: str) -> bool:
    """
    處理單張圖片

    Returns:
        是否成功
    """
    print(f"\n{'='*60}")
    print(f"處理圖片: {os.path.basename(image_path)}")
    print(f"{'='*60}")

    try:
        # 1. 上傳圖片
        uploaded_image = upload_image_to_comfyui(image_path)

        # 2. 更新工作流
        workflow = update_workflow_for_image(
            workflow_template,
            uploaded_image,
            PROMPT_TEXT,
            NEGATIVE_PROMPT_TEXT,
            SAMPLING_STEPS,
            LORA_1_NAME,
            LORA_1_STRENGTH,
            LORA_2_NAME,
            LORA_2_STRENGTH,
            LORA_3_NAME,
            LORA_3_STRENGTH
        )

        # 3. 提交任務
        prompt_id = queue_prompt(workflow, client_id)

        # 4. 等待完成
        task_info = wait_for_completion(prompt_id)

        # 5. 下載結果
        downloaded = download_output_images(task_info, OUTPUT_DIR, os.path.basename(image_path))

        print(f"✓ 成功處理: {len(downloaded)} 個輸出文件")
        return True

    except Exception as e:
        print(f"✗ 處理失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函數"""
    print("="*60)
    print("ComfyUI 批量圖片處理工具")
    print("="*60)
    print(f"輸入目錄: {INPUT_DIR}")
    print(f"輸出目錄: {OUTPUT_DIR}")
    print(f"ComfyUI 服務器: {COMFYUI_URL}")
    print(f"\n提示詞配置:")
    print(f"  正面提示詞: {PROMPT_TEXT if PROMPT_TEXT else '(未設置)'}")
    print(f"  反面提示詞: {NEGATIVE_PROMPT_TEXT if NEGATIVE_PROMPT_TEXT else '(未設置)'}")
    print(f"\n採樣器配置:")
    print(f"  CFG Scale: 使用工作流預設值")
    print(f"  採樣步數: {SAMPLING_STEPS}")
    print(f"\nLora 配置:")
    print(f"  Lora 1: {LORA_1_NAME} (強度: {LORA_1_STRENGTH})")
    if LORA_2_NAME != "None":
        print(f"  Lora 2: {LORA_2_NAME} (強度: {LORA_2_STRENGTH})")
    if LORA_3_NAME != "None":
        print(f"  Lora 3: {LORA_3_NAME} (強度: {LORA_3_STRENGTH})")
    print(f"\n工作流: {WORKFLOW_PATH}")
    print("="*60)

    # 檢查輸入目錄
    if not os.path.exists(INPUT_DIR):
        print(f"✗ 錯誤: 輸入目錄不存在: {INPUT_DIR}")
        print(f"提示: 請創建 '{INPUT_DIR}' 目錄並放入要處理的圖片")
        return

    # 檢查工作流文件
    if not os.path.exists(WORKFLOW_PATH):
        print(f"✗ 錯誤: 工作流文件不存在: {WORKFLOW_PATH}")
        return

    # 載入工作流模板
    print(f"\n載入工作流模板...")
    workflow_template = load_workflow(WORKFLOW_PATH)
    print(f"✓ 工作流已載入")

    # 獲取圖片列表
    image_files = get_image_files(INPUT_DIR)

    if not image_files:
        print(f"\n✗ 錯誤: 在 {INPUT_DIR} 中沒有找到支援的圖片文件")
        print(f"支援的格式: {', '.join(SUPPORTED_FORMATS)}")
        return

    print(f"\n找到 {len(image_files)} 個圖片文件")

    # 過濾已處理的圖片
    if SKIP_PROCESSED:
        unprocessed_files = []
        skipped_count = 0

        for image_path in image_files:
            filename = os.path.basename(image_path)
            if is_already_processed(filename, OUTPUT_DIR):
                skipped_count += 1
            else:
                unprocessed_files.append(image_path)

        if skipped_count > 0:
            print(f"✓ 跳過 {skipped_count} 個已處理的圖片")

        if not unprocessed_files:
            print(f"\n✓ 所有圖片都已處理完成！")
            print(f"輸出目錄: {os.path.abspath(OUTPUT_DIR)}")
            return

        image_files = unprocessed_files
        print(f"✓ 待處理: {len(image_files)} 個圖片")

    # 生成客戶端 ID
    client_id = str(uuid.uuid4())

    # 批量處理
    success_count = 0
    fail_count = 0

    for idx, image_path in enumerate(image_files, 1):
        print(f"\n進度: {idx}/{len(image_files)}")

        if process_single_image(image_path, workflow_template, client_id):
            success_count += 1
        else:
            fail_count += 1

    # 總結
    print(f"\n{'='*60}")
    print(f"批量處理完成!")
    print(f"{'='*60}")
    print(f"成功: {success_count}")
    print(f"失敗: {fail_count}")
    print(f"總計: {len(image_files)}")
    print(f"輸出目錄: {os.path.abspath(OUTPUT_DIR)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

