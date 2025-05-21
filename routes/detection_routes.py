# routes/detection_routes.py

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from datetime import datetime
from extensions import db
from models.detection import Detection
from models.message import Message
from models.terminal import Terminal
from models.result import Result
from schemas.detection_schema import DetectionSchema
from schemas.result_schema import ResultSchema
from dbsearch.db_search import detect as detect_core
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

detection_bp = Blueprint('detection', __name__, url_prefix='/detections')
d_sch       = DetectionSchema()
d_list_sch  = DetectionSchema(many=True)
r_sch       = ResultSchema(many=True)


@detection_bp.route('/', methods=['GET'])
@jwt_required()
def list_detections():
    # 分页参数，自动转 int 并限制最大 page size
    page = request.args.get('page', default=1, type=int)
    size = min(request.args.get('size', default=10, type=int), 100)
    pag = Detection.query.paginate(page=page, per_page=size, error_out=False)
    return jsonify({
        "total": pag.total,
        "pages": pag.pages,
        "items": d_list_sch.dump(pag.items)
    }), 200


@detection_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_detection(id):
    det = Detection.query.get_or_404(id)
    return d_sch.jsonify(det), 200


@detection_bp.route('/', methods=['POST'])
@jwt_required()
def create_detection():
    try:
        data = d_sch.load(request.get_json() or {})
    except ValidationError as ve:
        return jsonify({"error": ve.messages}), 400

    # 校验外键
    if not Message.query.get(data['message_id']):
        return jsonify({"error": f"message_id {data['message_id']} 不存在"}), 400
    if not Terminal.query.get(data['terminal_id']):
        return jsonify({"error": f"terminal_id {data['terminal_id']} 不存在"}), 400

    # 解析日期
    try:
        date = datetime.strptime(data['date'], '%Y-%m-%d %H:%M:%S') \
               if data.get('date') else datetime.utcnow()
    except ValueError:
        return jsonify({"error": "date 格式错误，须 YYYY-MM-DD HH:MM:SS"}), 400

    det = Detection(
        date=date,
        message_id=data['message_id'],
        type=data['type'],
        terminal_id=data['terminal_id']
    )

    try:
        db.session.add(det)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "创建 Detection 失败"}), 500

    return d_sch.jsonify(det), 201


@detection_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_detection(id):
    det = Detection.query.get_or_404(id)
    try:
        data = d_sch.load(request.get_json() or {}, partial=True)
    except ValidationError as ve:
        return jsonify({"error": ve.messages}), 400

    # 外键校验 & 设置
    if 'message_id' in data:
        if not Message.query.get(data['message_id']):
            return jsonify({"error": f"message_id {data['message_id']} 不存在"}), 400
        det.message_id = data['message_id']
    if 'terminal_id' in data:
        if not Terminal.query.get(data['terminal_id']):
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
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "更新 Detection 失败"}), 500

    return d_sch.jsonify(det), 200


@detection_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_detection(id):
    det = Detection.query.get_or_404(id)
    try:
        db.session.delete(det)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "删除 Detection 失败"}), 500

    return jsonify({"msg": "删除成功"}), 200




















@detection_bp.route('/detect', methods=['POST'])
@jwt_required()
def detect_text():
    """
    核心检测接口：
    请求体：{ "text": "...", "type": "文本", "terminal_id": 1 }
    """
    body = request.get_json() or {}
    text = body.get('text')
    det_type = body.get('type', '文本')
    term_id = body.get('terminal_id')

    # 基本参数校验
    if not text:
        return jsonify({"error": "缺少 text 参数"}), 400
    if term_id and not Terminal.query.get(term_id):
        return jsonify({"error": f"terminal_id {term_id} 不存在"}), 400

    # 1) 将文本存入 Message 表
    msg = Message(content=text)
    db.session.add(msg)
    db.session.flush()  # 先拿到 msg.id

    # 2) 新建 Detection 记录
    det = Detection(
        date=datetime.utcnow(),
        message_id=msg.id,
        type=det_type,
        terminal_id=term_id
    )
    db.session.add(det)
    db.session.flush()  # 拿到 det.id

    # 3) 调用核心 detect() 逻辑
    try:
        results = detect_core(text)
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"detect_core 调用失败: {str(e)}"}), 500

    # 4) 保存多条 Result
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
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "保存检测结果失败"}), 500

    return jsonify({
        "detection": d_sch.dump(det),
        "results": r_sch.dump(saved)
    }), 200
