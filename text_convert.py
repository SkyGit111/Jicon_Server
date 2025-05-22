import whisper
import math
from pathlib import Path

model = whisper.load_model("base")  # 转文本应该单开模块


def convert(filepath, user_id, time, text, length=4):
    length = math.ceil(length / 4)  # 每个文件4秒
    result_text = text
    print(length)
    for i in range(1, length+1):
        filename = Path(f"{filepath}/chunk_{user_id}_{time}_{i}.flac")
        if not filename.exists():
            print(f"文件 {filename} 不存在，终止处理")
            break  # 提前结束循环
        print(f"正在处理: {filename}")
        result = model.transcribe(str(filename))  # 如果 model.transcribe 需要字符串路径
        result_text += result["text"]
    return result_text
