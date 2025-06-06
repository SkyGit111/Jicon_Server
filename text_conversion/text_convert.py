import whisper
import math
from pathlib import Path

model = whisper.load_model("base")


def convert(filepath, user_id, timestamp, text, detect_times=1):
    result_text = text
    print(detect_times)
    for i in range(1, detect_times+1):
        filename = Path(f"{filepath}/chunk_{user_id}_{timestamp}_{i}.flac")
        if not filename.exists():
            print(f"文件 {filename} 不存在，终止处理")
            break  # 提前结束循环
        print(f"正在处理: {filename}")
        result = sendAndConvert(filename)
        result_text += result["data"]
    return result_text


import requests
import time
import os


# 配置参数
SERVER_URL = 'http://localhost:8080/audio_convert'  # Flask 服务地址
TIMESTAMP = int(time.time() * 1000)  # 当前时间戳（毫秒）


def sendAndConvert(audiopath):
    # 检查文件是否存在
    if not os.path.exists(audiopath):
        print(f"错误：音频文件 {audiopath} 不存在")
        return
    try:
        # 构造请求头和文件数据
        headers = {
            'Time': str(TIMESTAMP)
        }

        files = {
            'file': ('audio.flac', open(audiopath, 'rb'), 'audio/flac')
        }

        # 发送 POST 请求
        response = requests.post(
            SERVER_URL,
            headers=headers,
            files=files
        )

        # 处理响应
        if response.status_code == 200:
            print("上传成功！服务端返回：")
            return response.json()
        else:
            print(f"请求失败，状态码：{response.status_code}")
            return response.json()

    except Exception as e:
        return response.json()
    finally:
        if 'files' in locals():
            files['file'][1].close()  # 确保关闭文件
