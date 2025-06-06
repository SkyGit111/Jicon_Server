# routes/message_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from models.message import Message
from schemas.message_schema import MessageSchema   # 假设已有
from marshmallow import ValidationError

msg_bp = Blueprint("msg_bp", __name__)
msg_sch = MessageSchema()
msgs_sch = MessageSchema(many=True)


# ------------------------------------------------------------------ CRUD
@msg_bp.route("/", methods=["POST"])
@jwt_required()
def create_message():
    """手动插入 Message（主要给调试/测试用）"""
    try:
        data = request.get_json()
        msg = msg_sch.load(data)
        db.session.add(msg)
        db.session.commit()
        return msg_sch.jsonify(msg), 201
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@msg_bp.route("/", methods=["GET"])
@jwt_required()
def list_messages():
    msgs = Message.query.order_by(Message.id.desc()).all()
    return msgs_sch.jsonify(msgs), 200


@msg_bp.route("/<int:msg_id>", methods=["GET"])
@jwt_required()
def get_message(msg_id):
    msg = Message.query.get_or_404(msg_id)
    return msg_sch.jsonify(msg), 200


@msg_bp.route("/<int:msg_id>", methods=["PUT"])
@jwt_required()
def update_message(msg_id):
    msg = Message.query.get_or_404(msg_id)
    data = request.get_json()
    try:
        msg = msg_sch.load(data, instance=msg, partial=True)
        db.session.commit()
        return msg_sch.jsonify(msg), 200
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@msg_bp.route("/<int:msg_id>", methods=["DELETE"])
@jwt_required()
def delete_message(msg_id):
    msg = Message.query.get_or_404(msg_id)
    db.session.delete(msg)
    db.session.commit()
    return "", 204
