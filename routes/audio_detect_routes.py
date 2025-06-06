"""
routes/audio_detect_routes.py
=============================

增量双模态检测（声纹 + 文本）
--------------------------------
前端（WebSocket 或 Postman）每次调用一次 /audio/detect，都只会：

1. 对 **单个** 切片文件：
       chunk_{terminal_id}_{timestamp}_{detect_times}.flac
   调 SafeEar → 得到 AI 伪声概率 p_voice

2. 对 [1..detect_times] 所有切片做 Whisper 转写
   （text_convert.convert 会自己拼文本）→ 得到完整文本

3. 对完整文本调用 detect_text_only() → p_text, label_text, message_id

4. 加权融合：
       combined = ALPHA * p_voice + (1-ALPHA) * p_text
       label_final: 0-0.3 正常 | 0.3-0.7 可疑 | 0.7-1 诈骗

5. 持久化 Detection(prob, label, terminal_id, message_id, date)

6. 返回 JSON：
   {
     "voice_prob": 0.123,
     "text_prob":  0.456,
     "combined_prob": 0.30,
     "label_voice": "真人/AI伪声",
     "label_text":  "...",
     "label_final": "...",
     "message_id":  123
   }
"""

import os
import math
from pathlib import Path
from statistics import mean

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from datetime import datetime, timezone, timedelta

from extensions import db
from models.detection import Detection
from services.detect_util import detect_text_only     # (p_text, label_text, msg_id)
from audio_detect.audio_detect import sendAndDetect                # 返回 SafeEar JSON
from text_conversion.text_convert import convert                      # 返回本轮增量文本

# ────────── 配置 ──────────
CHUNK_DIR   = os.getenv("CHUNK_DIR", "audio_chunks")
ALPHA       = float(os.getenv("COMBINE_ALPHA", 0.1))  # 声纹权重
CHINA_TZ    = timezone(timedelta(hours=8))

bp = Blueprint("audio_detect", __name__, url_prefix="/audio")


# ────────── 帮助函数 ──────────
def _extract_safeear_prob(resp: dict) -> float:
    """
    适配 SafeEar JSON: {"code":200,"data":{"probs":[[real,fake]]}}
    返回 fake 概率 (float 0-1)，解析失败返回 0.
    """
    try:
        if resp.get("code") != 200:
            return 0.0
        probs = resp["data"]["probs"]
        if isinstance(probs, list) and probs and isinstance(probs[0], list):
            return float(probs[0][1])          # fake_prob
    except Exception as e:
        current_app.logger.error("解析 SafeEar JSON 失败: %s", e)
    return 0.0


def _voice_label(prob: float) -> str:
    return "AI伪声" if prob >= 0.5 else "真人"


def _final_label(prob: float) -> str:
    if prob >= 0.7:
        return "诈骗"
    if prob >= 0.3:
        return "可疑"
    return "正常"


# ────────── 主接口 ──────────
@bp.route("/detect", methods=["POST"])
def detect_increment():
    """
    POST /audio/detect
    JSON Body:
      {
        "terminal_id": "t1",
        "timestamp":   "20250605123456",
        "detect_times": 3        # 本次检测的 chunk 序号
      }
    Header:
      Authorization: Bearer <jwt>
    """
    body = request.get_json() or {}
    required = ("terminal_id", "timestamp", "detect_times")
    miss = [k for k in required if k not in body]
    if miss:
        return jsonify({"error": f"缺少字段: {', '.join(miss)}"}), 400

    terminal_id = str(body["terminal_id"])
    ts          = str(body["timestamp"])
    detect_times = int(body["detect_times"])

    # ── 1. 声纹检测（单片文件） ──
    flac_path = Path(CHUNK_DIR) / f"chunk_{terminal_id}_{ts}_{detect_times}.flac"
    if not flac_path.exists():
        return jsonify({"error": f"音频文件不存在: {flac_path}"}), 404

    safeear_json = sendAndDetect(str(flac_path))
    p_voice = _extract_safeear_prob(safeear_json)
    current_app.logger.info("SafeEar fake_prob = %.6f", p_voice)

    # ── 2. Whisper 转写增量 → 完整文本 ──
    try:
        full_text = convert(
            CHUNK_DIR, user_id=terminal_id, timestamp=ts,
            text="", detect_times=detect_times
        )
    except TypeError:
        # 兼容老版签名 convert(dir_path, user_id, timestamp, detect_times)
        full_text = convert(CHUNK_DIR, terminal_id, ts, detect_times)

    # ── 3. 文本检测 ──
    p_text, label_text, msg_id = detect_text_only(full_text)
    current_app.logger.info("TextDet prob=%.3f label=%s", p_text, label_text)

    # ── 4. 融合概率 ──
    combined = ALPHA * p_voice + (1 - ALPHA) * p_text
    label_final = _final_label(combined)

    # ── 5. 写 Detection 表 ──
    try:
        det = Detection(
            date=datetime.now(CHINA_TZ),
            message_id=msg_id,
            terminal_id=int(terminal_id) if str(terminal_id).isdigit() else None,
            prob=combined,
            label=label_final
        )
        db.session.add(det)
        db.session.commit()
    except Exception as e:
        current_app.logger.error("写 Detection 失败: %s", e)

    # ── 6. 返回 ──
    return jsonify({
        "voice_prob":      round(p_voice, 6),
        "text_prob":       round(p_text, 6),
        "combined_prob":   round(combined, 6),
        "label_voice":     _voice_label(p_voice),
        "label_text":      label_text,
        "label_final":     label_final,
        "message_id":      msg_id
    }), 200


# ────────── 健康检查 ──────────
@bp.route("/healthz", methods=["GET"])
def healthz():
    return "ok", 200
