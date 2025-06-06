# services/audio_pipeline.py
import os, math, uuid
from pathlib import Path
from typing import Dict, Any, List

from audio_detect.audio_detect import sendAndDetect as _voice_detect
from text_conversion.text_convert import convert as _convert_text
from services.detect_util import detect_and_save

COMBINE_ALPHA = float(os.getenv("COMBINE_ALPHA", 0.5))  # 声纹权重

def process(user_id: str, ts: str, chunk_dir: str, chunk_count: int) -> Dict[str, Any]:
    """
    统一业务逻辑：
    1. 对每个 chunk 进行伪声检测 → p_voice
    2. 将所有 chunk 转写成文本 → transcript
    3. 文本诈骗检测 → p_text
    4. 加权融合 → p_final
    """
    # ---------- 1. 声纹检测 ----------
    voice_probs: List[float] = []
    for idx in range(1, chunk_count + 1):
        flac_path = f"{chunk_dir}/chunk_{user_id}_{ts}_{idx}.flac"
        if not Path(flac_path).exists():
            break
        resp = _voice_detect(flac_path) or {}
        if resp.get("probability") is not None:
            voice_probs.append(resp["probability"])

    p_voice = sum(voice_probs) / len(voice_probs) if voice_probs else 0.0

    # ---------- 2. 语音转写 ----------
    transcript = _convert_text(chunk_dir, user_id, ts, "", chunk_count * 10)

    # ---------- 3. 文本诈骗检测 ----------
    p_text, t_label, msg_id, det_id = detect_and_save(transcript)

    # ---------- 4. 加权 ----------
    alpha = min(max(COMBINE_ALPHA, 0.0), 1.0)
    p_final = alpha * p_voice + (1 - alpha) * p_text

    return {
        "request_id": ts,
        "text": transcript,
        "detections": [
            {"label": "AI伪声",    "probability": round(p_voice, 3)},
            {"label": t_label, "probability": round(p_text, 3)}
        ],
        "combined_probability": round(p_final, 3)
    }
