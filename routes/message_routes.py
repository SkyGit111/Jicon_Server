# routes/message_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
from sqlalchemy import func

from extensions import db
from models.message import Message
from schemas.message_schema import MessageSchema

message_bp = Blueprint('message', __name__, url_prefix='/messages')
message_schema = MessageSchema()
messages_schema = MessageSchema(many=True)


@message_bp.route('/', methods=['GET'])
@jwt_required()
def list_messages():
    """
    分页查询消息记录。
    GET /messages?page=<页码>&size=<每页大小>
    """
    page = request.args.get('page', 1, type=int)
    size = min(request.args.get('size', 10, type=int), 100)
    pag = Message.query.paginate(page=page, per_page=size, error_out=False)
    return jsonify({
        "total": pag.total,
        "pages": pag.pages,
        "items": messages_schema.dump(pag.items)
    }), 200


@message_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_message(id):
    """
    获取单条消息详情。
    GET /messages/<id>
    """
    msg = Message.query.get_or_404(id)
    return message_schema.jsonify(msg), 200


@message_bp.route('/', methods=['POST'])
@jwt_required()
def create_message():
    """
    创建新消息。
    POST /messages
    Body JSON:
      { "content": "...", "label": "..." }
    """
    try:
        data = message_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    msg = Message(**data)
    try:
        db.session.add(msg)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return message_schema.jsonify(msg), 201


@message_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_message(id):
    """
    更新消息。
    PUT /messages/<id>
    Body JSON: 只需包含要修改的字段
    """
    msg = Message.query.get_or_404(id)
    try:
        data = message_schema.load(request.get_json() or {}, partial=True)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    for key, val in data.items():
        setattr(msg, key, val)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return message_schema.jsonify(msg), 200


@message_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_message(id):
    """
    删除指定消息。
    DELETE /messages/<id>
    """
    msg = Message.query.get_or_404(id)
    try:
        db.session.delete(msg)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "删除成功"}), 200


@message_bp.route('/statistics', methods=['GET'])
@jwt_required()
def message_statistics():
    """
    按 label 分组统计消息数。
    GET /messages/statistics
    返回 JSON:
      { "statistics": [ { "label": "...", "count": N }, ... ] }
    """
    stats = db.session.query(
        Message.label,
        func.count(Message.id).label('count')
    ).group_by(Message.label).all()
    result = [{"label": label, "count": count} for label, count in stats]
    return jsonify({"statistics": result}), 200
