from flask import Blueprint, request, jsonify
from extensions import db
from models.message import Message
from schemas.message_schema import MessageSchema
from flask_jwt_extended import jwt_required

message_bp     = Blueprint('message', __name__, url_prefix='/messages')
message_schema = MessageSchema()
messages_schema= MessageSchema(many=True)

# 列表 & 分页
@message_bp.route('/', methods=['GET'])
@jwt_required()
def list_messages():
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))
    pag = Message.query.paginate(page=page, per_page=size, error_out=False)
    return jsonify({
        "total": pag.total,
        "pages": pag.pages,
        "items": messages_schema.dump(pag.items)
    }), 200

# 获取单条
@message_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_message(id):
    msg = Message.query.get_or_404(id)
    return message_schema.jsonify(msg), 200

# 创建
@message_bp.route('/', methods=['POST'])
@jwt_required()
def create_message():
    data = message_schema.load(request.get_json())
    msg = Message(**data)
    db.session.add(msg)
    db.session.commit()
    return message_schema.jsonify(msg), 201

# 更新
@message_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_message(id):
    msg = Message.query.get_or_404(id)
    data = message_schema.load(request.get_json(), partial=True)
    for k, v in data.items():
        setattr(msg, k, v)
    db.session.commit()
    return message_schema.jsonify(msg), 200

# 删除
@message_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_message(id):
    msg = Message.query.get_or_404(id)
    db.session.delete(msg)
    db.session.commit()
    return jsonify({"msg": "删除成功"}), 200

# 统计分析
@message_bp.route('/statistics', methods=['GET'])
@jwt_required()
def statistical_analysis():
    # 示例：按 label 分组计数
    from sqlalchemy import func
    stats = db.session.query(
        Message.label,
        func.count(Message.id).label('count')
    ).group_by(Message.label).all()
    result = [{ "label": label, "count": count } for label, count in stats]
    return jsonify({"statistics": result}), 200
