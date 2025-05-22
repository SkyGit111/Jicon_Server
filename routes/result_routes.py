# routes/result_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from models.result import Result
from models.message import Message
from models.detection import Detection
from schemas.result_schema import ResultSchema

res_bp = Blueprint('results', __name__, url_prefix='/results')
r_sch = ResultSchema()
r_list_sch = ResultSchema(many=True)
MAX_PAGE_SIZE = 100


@res_bp.route('/', methods=['GET'])
@jwt_required()
def list_results():
    """
    分页查询检测结果，可按 message_id 或 detection_id 过滤。
    GET /results?page=<页码>&size=<每页大小>&message_id=<>&detection_id=<>
    """
    page = request.args.get('page', 1, type=int)
    size = min(request.args.get('size', 10, type=int), MAX_PAGE_SIZE)
    q = Result.query
    msg_id = request.args.get('message_id', type=int)
    if msg_id is not None:
        q = q.filter_by(message_id=msg_id)
    det_id = request.args.get('detection_id', type=int)
    if det_id is not None:
        q = q.filter_by(detection_id=det_id)
    pag = q.paginate(page=page, per_page=size, error_out=False)
    return jsonify({
        "total": pag.total,
        "pages": pag.pages,
        "items": r_list_sch.dump(pag.items)
    }), 200


@res_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_result(id):
    """
    获取单条检测结果详情。
    GET /results/<id>
    """
    res = Result.query.get_or_404(id)
    return r_sch.jsonify(res), 200


@res_bp.route('/', methods=['POST'])
@jwt_required()
def create_result():
    """
    创建检测结果。
    POST /results
    Body JSON:
      {
        "message_id": <int>,      # 可选
        "detection_id": <int>,    # 必填
        "label": "<label 字符串>"
      }
    """
    try:
        data = r_sch.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    # 外键校验
    mid = data.get('message_id')
    if mid is not None and not Message.query.get(mid):
        return jsonify({"error": f"message_id {mid} 不存在"}), 400
    did = data.get('detection_id')
    if not Detection.query.get(did):
        return jsonify({"error": f"detection_id {did} 不存在"}), 400

    res = Result(**data)
    try:
        db.session.add(res)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return r_sch.jsonify(res), 201


@res_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_result(id):
    """
    更新检测结果（局部更新）。
    PUT /results/<id>
    Body JSON 可包含：message_id、detection_id、label
    """
    res = Result.query.get_or_404(id)
    try:
        data = r_sch.load(request.get_json() or {}, partial=True)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    # 外键校验并赋值
    if 'message_id' in data:
        mid = data['message_id']
        if mid is not None and not Message.query.get(mid):
            return jsonify({"error": f"message_id {mid} 不存在"}), 400
        res.message_id = mid

    if 'detection_id' in data:
        did = data['detection_id']
        if not Detection.query.get(did):
            return jsonify({"error": f"detection_id {did} 不存在"}), 400
        res.detection_id = did

    if 'label' in data:
        res.label = data['label']

    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return r_sch.jsonify(res), 200


@res_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_result(id):
    """
    删除指定的检测结果。
    DELETE /results/<id>
    """
    res = Result.query.get_or_404(id)
    try:
        db.session.delete(res)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "删除成功"}), 200
