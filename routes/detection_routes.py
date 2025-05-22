# routes/detection_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from models.message import Message
from models.detection import Detection
from models.terminal import Terminal
from models.result import Result
from schemas.detection_schema import DetectionSchema
from schemas.result_schema import ResultSchema
from db_search.db_search import detect as detect_core

detection_bp = Blueprint('detection', __name__, url_prefix='/detections')

# Schema 实例
detection_schema      = DetectionSchema()
detection_list_schema = DetectionSchema(many=True)
result_list_schema    = ResultSchema(many=True)


@detection_bp.route('/', methods=['GET'])
@jwt_required()
def list_detections():
    """
    分页查询所有检测记录。
    GET /detections?page=<页码>&size=<每页数量>
    """
    page = request.args.get('page', default=1, type=int)
    size = min(request.args.get('size', default=10, type=int), 100)
    pag = Detection.query.paginate(page=page, per_page=size, error_out=False)
    return jsonify({
        "total": pag.total,
        "pages": pag.pages,
        "items": detection_list_schema.dump(pag.items)
    }), 200


@detection_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_detection(id):
    """
    获取单条检测记录详情。
    GET /detections/<id>
    """
    det = Detection.query.get_or_404(id)
    return detection_schema.jsonify(det), 200


@detection_bp.route('/', methods=['POST'])
@jwt_required()
def create_detection():
    """
    创建新的检测任务，并执行一次文本检测。
    请求 JSON:
      {
        "text": "<待检测文本>",
        "type": "<检测类型，可选，默认 '文本'>",
        "terminal_id": <终端 ID，可选>
      }
    """
    body = request.get_json() or {}
    text       = body.get('text')
    det_type   = body.get('type', '文本')
    terminal_id= body.get('terminal_id')

    # 参数校验
    if not text:
        return jsonify({"error": "缺少 text 参数"}), 400
    if terminal_id and not Terminal.query.get(terminal_id):
        return jsonify({"error": f"terminal_id {terminal_id} 不存在"}), 400

    # 1) 写入 Message 表
    msg = Message(content=text)
    db.session.add(msg)
    db.session.flush()  # 获得 msg.id

    # 2) 写入 Detection 表
    det = Detection(
        date=datetime.utcnow(),
        message_id=msg.id,
        type=det_type,
        terminal_id=terminal_id
    )
    db.session.add(det)
    db.session.flush()  # 获得 det.id

    # 3) 调用核心检测逻辑
    try:
        results = detect_core(text)
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"detect_core 调用失败: {e}"}), 500

    # 4) 保存 Result
    saved = []
    for item in results:
        res = Result(
            message_id=msg.id,
            label=item.get('label'),
            detection_id=det.id
        )
        db.session.add(res)
        saved.append(res)

    # 5) 提交事务
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"保存检测结果失败: {e}"}), 500

    # 6) 返回组合结果
    return jsonify({
        "detection": detection_schema.dump(det),
        "results": result_list_schema.dump(saved)
    }), 201


@detection_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_detection(id):
    """
    更新已有的检测记录（不重跑检测，只改元数据）。
    PUT /detections/<id>
    Body: { "type": "...", "terminal_id": <id>, "date": "YYYY-MM-DD HH:MM:SS" }
    """
    det = Detection.query.get_or_404(id)
    try:
        data = DetectionSchema().load(request.get_json() or {}, partial=True)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    # 外键及字段校验
    if 'terminal_id' in data:
        term = Terminal.query.get(data['terminal_id'])
        if not term:
            return jsonify({"error": f"terminal_id {data['terminal_id']} 不存在"}), 400
        det.terminal_id = data['terminal_id']
    if 'type' in data:
        det.type = data['type']
    if 'date' in data:
        try:
            det.date = datetime.strptime(data['date'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return jsonify({"error": "date 格式错误，须 YYYY-MM-DD HH:MM:SS"}), 400

    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"更新 Detection 失败: {e}"}), 500

    return detection_schema.jsonify(det), 200


@detection_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_detection(id):
    """
    删除指定的检测记录。
    DELETE /detections/<id>
    """
    det = Detection.query.get_or_404(id)
    try:
        db.session.delete(det)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"删除 Detection 失败: {e}"}), 500

    return jsonify({"message": "删除成功"}), 200


@detection_bp.route('/detect', methods=['POST'])
@jwt_required()
def detect_text():
    """
    仅做文本检测，不写数据库。
    POST /detections/detect
    Body: { "text": "...", "type": "...", "terminal_id": <id> }
    """
    body = request.get_json() or {}
    text       = body.get('text')
    det_type   = body.get('type', '文本')
    terminal_id= body.get('terminal_id')

    # 参数校验
    if not text:
        return jsonify({"error": "缺少 text 参数"}), 400
    if terminal_id and not Terminal.query.get(terminal_id):
        return jsonify({"error": f"terminal_id {terminal_id} 不存在"}), 400

    # 调用核心 detect
    try:
        results = detect_core(text)
    except Exception as e:
        return jsonify({"error": f"detect_core 调用失败: {e}"}), 500

    return jsonify({"text": text, "type": det_type, "terminal_id": terminal_id, "results": results}), 200
