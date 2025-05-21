# routes/audio_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import os
import shutil
from saveaudio import upload_audio as _upload_audio
from text_convert import convert as _convert
from db_search import detect as _detect_core

audio_bp = Blueprint('audio', __name__, url_prefix='/audio')

def _slice_audio(stream, headers):
    """
    解密并切片音频流，返回临时目录、user_id、time_stamp 及切片文件列表。
    """
    channels     = int(headers.get('Channels', 1))
    sample_width = int(headers.get('Samplewidth', 2))
    sample_rate  = int(headers.get('Samplerate', 16000))
    user_id      = headers.get('Userid', 'unknown')
    time_stamp   = headers.get('Time', '0')
    base_dir = os.path.join('tmp_audio', f"{user_id}_{time_stamp}")
    os.makedirs(base_dir, exist_ok=True)
    flac_list = _upload_audio(
        stream=stream,
        channels=channels,
        sample_width=sample_width,
        sample_rate=sample_rate,
        output_dir=base_dir
    )
    return base_dir, user_id, time_stamp, flac_list

def _transcribe_all(base_dir, user_id, time_stamp, max_len=2048):
    """
    遍历 base_dir 下所有切片，调用 Whisper 转写并拼接成单段文本。
    """
    return _convert(
        filepath=base_dir,
        user_id=user_id,
        time=time_stamp,
        text="",
        length=max_len
    )

@audio_bp.route('/upload_wav', methods=['POST'])
@jwt_required()
def upload_wav():
    base_dir = None
    try:
        # 1) 音频解密与切片
        base_dir, user_id, time_stamp, _ = _slice_audio(request.stream, request.headers)

        # 2) 转写所有切片
        text = _transcribe_all(base_dir, user_id, time_stamp)

        # 3) 伪声检测
        detections = _detect_core(text)

        return jsonify({
            "text": text,
            "detections": detections
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # 4) 清理临时目录
        if base_dir and os.path.exists(base_dir):
            shutil.rmtree(base_dir, ignore_errors=True)
