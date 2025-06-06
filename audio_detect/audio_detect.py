import requests
import time
import os


# 配置参数
SERVER_URL = 'http://localhost:6006/audio_detect'  # Flask 服务地址
TIMESTAMP = int(time.time() * 1000)  # 当前时间戳（毫秒）


def sendAndDetect(audiopath):
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
            print("safeear上传成功！服务端返回：")
            return response.json()
        else:
            print(f"safeear请求失败，状态码：{response.status_code}")
            return response.json()

    except Exception as e:
        return response.json()
    finally:
        if 'files' in locals():
            files['file'][1].close()  # 确保关闭文件
