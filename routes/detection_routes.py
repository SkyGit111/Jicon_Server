from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from extensions import db
from models.detection import Detection
from schemas.detection_schema import DetectionSchema
from datetime import datetime

det_bp = Blueprint("det_bp", __name__)
det_schema = DetectionSchema()

@det_bp.route("/", methods=["POST"])
@jwt_required()
def create_detection():
    """
    创建一条新的检测记录（双模态综合后端调用时使用）。
    请求 JSON 应包含：
      - message_id: int
      - terminal_id: int
      - prob: float
      - label: str
      - date: 可选，"YYYY-MM-DD HH:MM:SS" 格式；若不传，后端会使用当前时间
    返回：
      - 检测记录的完整内容
    """
    try:
        data = request.get_json()
        # 校验必填字段
        for field in ("message_id", "terminal_id", "prob", "label"):
            if field not in data:
                return jsonify({"error": f"缺少字段: {field}"}), 400

        # 如果后台传入 date，则做简单解析，否则使用 now()
        date_str = data.get("date")
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except Exception:
                return jsonify({"error": "date 格式必须为 YYYY-MM-DD HH:MM:SS"}), 400
        else:
            date_obj = datetime.utcnow()

        det = Detection(
            date       = date_obj,
            message_id = data["message_id"],
            terminal_id= data["terminal_id"],
            prob       = float(data["prob"]),
            label      = data["label"]
        )
        db.session.add(det)
        db.session.commit()

        return jsonify(det.to_dict()), 201

    except (ValidationError, KeyError, ValueError) as e:
        return jsonify({"error": str(e)}), 400


@det_bp.route("/latest", methods=["GET"])
def get_latest_by_terminal():
    """
    查询某个终端 (terminal_id) 在给定 timestamp 之后的最新一条检测记录。
    请求 Header 中预期包含：
      - TerminalId: <int>    （终端 ID）
      - Timestamp: <str>     （UTC 时间戳，格式 "YYYY-MM-DD HH:MM:SS"）
    响应：
      - { 检测记录的 JSON } 或 {"error": "..."} + 相应 HTTP 状态码
    """
    try:
        # 从 Header 中解析两个值
        terminal_id = request.headers.get("TerminalId")
        ts_str      = request.headers.get("Timestamp")
        if not terminal_id or not ts_str:
            return jsonify({"error": "缺少 Header: TerminalId 或 Timestamp"}), 400

        try:
            terminal_id = int(terminal_id)
        except ValueError:
            return jsonify({"error": "TerminalId 必须是整数"}), 400

        try:
            ts_obj = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
        except Exception:
            return jsonify({"error": "Timestamp 格式必须为 'YYYY-MM-DD HH:MM:SS'"}), 400

        # 查询：terminal_id 相同，且 date > ts_obj，按 date 倒序取第一条
        det = (
            db.session.query(Detection)
            .filter(Detection.terminal_id == terminal_id, Detection.date > ts_obj)
            .order_by(Detection.date.desc())
            .first()
        )
        if not det:
            return jsonify({"message": "未找到匹配记录"}), 404

        return jsonify(det.to_dict()), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
