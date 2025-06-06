# services/detect_util.py
from datetime import datetime
from typing import Tuple, List
from extensions import db
from models.message import Message
from models.detection import Detection
from models.result import Result
from db_search.db_search import detect as detect_core

def detect_and_save(text: str,
                    det_type: str = "文本",
                    terminal_id: int | None = None
                    ) -> Tuple[float, str, int, int]:
    """
    运行文本检测 ➜ 将 Message / Detection / Result 写入数据库
    返回: (p_text, label, message_id, detection_id)
    """
    # 1) Message
    msg = Message(content=text)
    db.session.add(msg)
    db.session.flush()        # 生成 msg.id

    # 2) Detection
    det = Detection(date=datetime.utcnow(),
                    message_id=msg.id,
                    type=det_type,
                    terminal_id=terminal_id)
    db.session.add(det)
    db.session.flush()        # 生成 det.id

    # 3) 调核心检测
    results_raw = detect_core(text)

    # ---------------- 更严格的兼容处理 ----------------
    import json
    from collections.abc import Sequence

    # 先初始化空列表
    results = []

    # 情况 1： detect_core 直接返回字典，说明仅一个结果
    if isinstance(results_raw, dict):
        results = [results_raw]

    # 情况 2： detect_core 返回 JSON 字符串，需要 json.loads
    elif isinstance(results_raw, str):
        try:
            parsed = json.loads(results_raw)
            # parsed 可能是一个列表，也可能是单个 dict
            if isinstance(parsed, dict):
                results = [parsed]
            elif isinstance(parsed, Sequence):
                results = parsed
            else:
                results = []
        except json.JSONDecodeError:
            results = []

    # 情况 3： detect_core 返回的已经是 Python 列表
    elif isinstance(results_raw, Sequence):
        # 但要排除字符串走到这里的“每个字符也算序列”的情况
        # 所以多一层检查：列表内元素必须是 dict 才算
        if all(isinstance(elem, dict) for elem in results_raw):
            results = list(results_raw)
        else:
            # 如果列表里混了别的类型，也只挑 dict
            results = [elem for elem in results_raw if isinstance(elem, dict)]

    # 否则都归为空
    else:
        results = []

    # 4) 保存 Result 并统计最高概率
    p_text, label = 0.0, "未知"
    for item in results:
        # 保证确实拿到 dict
        if not isinstance(item, dict):
            continue
        lab  = item.get("label", "未知")
        try:
            prob = float(item.get("probability", 0))
        except (ValueError, TypeError):
            prob = 0.0

        # 写库
        db.session.add(Result(message_id=msg.id,
                              detection_id=det.id,
                              label=lab))

        # 取最高概率
        if prob > p_text:
            p_text, label = prob, lab


    # 5) 把 Message.label 设为初始检测标签
    msg.label = label
    db.session.commit()
    return p_text, label, msg.id, det.id





def detect_text_only(text: str) -> Tuple[float, str, int]:
    """
    仅做文本检测，返回综合概率、标签、message_id
    - 不负责写入 Detection 表
    - 可用于复合检测中音频检测之后，单独调用文本检测
    """
    # 1. Message 入库
    msg = Message(content=text)
    db.session.add(msg)
    db.session.flush()

    # 2. 检测（使用核心 detect）
    results_raw = detect_core(text)

    # ---------------- 严格兼容处理 ----------------
    import json
    from collections.abc import Sequence
    results = []

    if isinstance(results_raw, dict):
        results = [results_raw]
    elif isinstance(results_raw, str):
        try:
            parsed = json.loads(results_raw)
            if isinstance(parsed, dict):
                results = [parsed]
            elif isinstance(parsed, Sequence):
                results = parsed
        except json.JSONDecodeError:
            results = []
    elif isinstance(results_raw, Sequence):
        if all(isinstance(x, dict) for x in results_raw):
            results = list(results_raw)
        else:
            results = [x for x in results_raw if isinstance(x, dict)]

    # 3. 保存 result（不写 detection 表）
    p_text, label = 0.0, "未知"
    for item in results:
        if not isinstance(item, dict):
            continue
        lab = item.get("label", "未知")
        try:
            prob = float(item.get("probability", 0))
        except (ValueError, TypeError):
            prob = 0.0

        db.session.add(Result(message_id=msg.id, label=lab))

        if prob > p_text:
            p_text, label = prob, lab

    # 更新 Message
    msg.label = label
    db.session.commit()

    return p_text, label, msg.id

