from flask import Blueprint, request, jsonify
from extensions import db
from models.result import Result
from schemas.result_schema import ResultSchema
from models.message import Message
from models.detection import Detection
from flask_jwt_extended import jwt_required

result_bp      = Blueprint('result', __name__, url_prefix='/results')
result_schema  = ResultSchema()
results_schema = ResultSchema(many=True)

# 列表 & 分页
@result_bp.route('/', methods=['GET'])
@jwt_required()
def list_results():
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))
    pag = Result.query.paginate(page=page, per_page=size, error_out=False)
    return jsonify({
        "total": pag.total,
        "pages": pag.pages,
        "items": results_schema.dump(pag.items)
    }), 200

# 获取单条
@result_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_result(id):
    res = Result.query.get_or_404(id)
    return result_schema.jsonify(res), 200

# 创建
@result_bp.route('/', methods=['POST'])
@jwt_required()
def create_result():
    data = result_schema.load(request.get_json())
    # 校验外键
    if data.get('message_id') is not None and not Message.query.get(data['message_id']):
        return jsonify({"msg": f"message_id {data['message_id']} 不存在"}), 400
    if not Detection.query.get(data['detection_id']):
        return jsonify({"msg": f"detection_id {data['detection_id']} 不存在"}), 400
    res = Result(**data)
    db.session.add(res)
    db.session.commit()
    return result_schema.jsonify(res), 201

# 更新
@result_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_result(id):
    res = Result.query.get_or_404(id)
    data = result_schema.load(request.get_json(), partial=True)
    if 'message_id' in data:
        if data['message_id'] is not None and not Message.query.get(data['message_id']):
            return jsonify({"msg": f"message_id {data['message_id']} 不存在"}), 400
        res.message_id = data['message_id']
    if 'detection_id' in data:
        if not Detection.query.get(data['detection_id']):
            return jsonify({"msg": f"detection_id {data['detection_id']} 不存在"}), 400
        res.detection_id = data['detection_id']
    if 'label' in data:
        res.label = data['label']
    db.session.commit()
    return result_schema.jsonify(res), 200

# 删除
@result_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_result(id):
    res = Result.query.get_or_404(id)
    db.session.delete(res)
    db.session.commit()
    return jsonify({"msg": "删除成功"}), 200
