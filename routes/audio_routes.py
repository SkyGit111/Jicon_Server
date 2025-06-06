# routes/audio_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import uuid, os
from saveaudio import upload_audio as _upload_audio
from services.audio_pipeline import process as _process
from flask import current_app

audio_bp = Blueprint("audio_bp", __name__)

@audio_bp.route("/audio/upload_wav", methods=["POST"])
@jwt_required()
def upload_wav():
    try:
        # 1. 读取头部
        user_id     = request.headers.get("Userid", "unknown")
        ts          = request.headers.get("Time") or str(uuid.uuid4().int)[:13]
        channels    = int(request.headers.get("Channels", 1))
        samplewidth = int(request.headers.get("Samplewidth", 2))
        samplerate  = int(request.headers.get("Samplerate", 16000))

        # 2. 切片
        result = _upload_audio(
            stream=request.stream,
            channels=channels,
            sample_width=samplewidth,
            sample_rate=samplerate,
            user_id=user_id,
            time=ts
        )
        if result.get("status") != "success":
            return jsonify({"error": result.get("message")}), 500

        chunk_dir   = "audio_chunks"
        chunk_count = result["chunks_saved"]

        # 3. 统一业务逻辑
        payload = _process(user_id, ts, chunk_dir, chunk_count)
        return jsonify(payload), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# routes/audio_routes.py （追加到文件末尾）



@audio_bp.route("/audio_detect", methods=["POST"])
def audio_detect():
    """
    内部接口：WebSocket 服务调用。
    Body: { "user_id": <str/int>, "timestamp": <str>, "chunk_count": <int> }
    """
    try:
        data        = request.get_json() or {}
        user_id     = str(data["user_id"])
        ts          = str(data["timestamp"])
        chunk_count = int(data["chunk_count"])
        chunk_dir   = "audio_chunks"   # 与 websocket.py 保持一致

        payload = _process(user_id, ts, chunk_dir, chunk_count)
        # 可在此记录一次完整检测日志
        current_app.logger.info(f"[audio_detect] 完成 user={user_id}, ts={ts}, chunks={chunk_count}")
        return jsonify(payload), 200

    except KeyError as e:
        return jsonify({"error": f"缺少字段 {e}"}), 400
    except Exception as e:
        current_app.logger.error(f"[audio_detect] 失败: {e}")
        return jsonify({"error": str(e)}), 500
