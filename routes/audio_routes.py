# routes/audio_routes.py

import os
import shutil
import uuid

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from saveaudio import upload_audio as _upload_audio  # 切片解密模块
from text_convert import convert as _convert         # Whisper 转写模块
from db_search.db_search import detect as _detect_core  # 文本检测模块

audio_bp = Blueprint('audio', __name__, url_prefix='/audio')


@audio_bp.route('/upload_wav', methods=['POST'])
@jwt_required()
def upload_wav():
    """
    接收加密的 WAV 音频流，按 4 秒切片 → Whisper 转写 → 文本检测 → 返回结果。
    所有操作完成后会自动清理临时文件。

    Headers:
      - Channels: 音频通道数，默认 1
      - Samplewidth: 样本宽度（字节），默认 2
      - Samplerate: 采样率（Hz），默认 16000
      - Userid: 用户唯一标识，默认 "unknown"
      - Time: 客户端时间戳，默认 "0"

    返回 JSON:
    {
      "request_id": "<唯一请求 ID>",
      "text": "<完整转写文本>",
      "detections": [ ... 伪声检测结果 ... ]
    }
    """
    # 生成请求 ID，用于隔离并发目录
    request_id = uuid.uuid4().hex
    base_dir = os.path.join('tmp_audio', request_id)

    # 1) 解析并校验请求头
    try:
        channels     = int(request.headers.get('Channels', 1))
        sample_width = int(request.headers.get('Samplewidth', 2))
        sample_rate  = int(request.headers.get('Samplerate', 16000))
        user_id      = request.headers.get('Userid', 'unknown')
        time_stamp   = request.headers.get('Time', '0')
    except ValueError:
        return jsonify({"error": "音频参数格式错误"}), 400

    os.makedirs(base_dir, exist_ok=True)

    try:
        # 2) 解密并切片
        #    返回值为 FLAC 文件列表，但此处无需具体使用
        _upload_audio(
            stream=request.stream,
            channels=channels,
            sample_width=sample_width,
            sample_rate=sample_rate,
            output_dir=base_dir
        )
    except Exception as e:
        shutil.rmtree(base_dir, ignore_errors=True)
        return jsonify({"error": f"音频切片失败: {e}"}), 500

    try:
        # 3) 调用 Whisper 转写所有切片并拼接结果
        text = _convert(
            filepath=base_dir,
            user_id=user_id,
            time=time_stamp,
            text="",
            length=2048
        )
    except Exception as e:
        shutil.rmtree(base_dir, ignore_errors=True)
        return jsonify({"error": f"音频转写失败: {e}"}), 500

    try:
        # 4) 调用文本检测核心
        detections = _detect_core(text)
    except Exception as e:
        shutil.rmtree(base_dir, ignore_errors=True)
        return jsonify({"error": f"伪声检测失败: {e}"}), 500

    # 5) 返回结果
    response = jsonify({
        "request_id": request_id,
        "text": text,
        "detections": detections
    }), 200

    # 6) 清理临时目录
    shutil.rmtree(base_dir, ignore_errors=True)
    return response
