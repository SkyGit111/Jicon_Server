# routes/model_version_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

from extensions import db
from models.model_version import ModelVersion
from schemas.model_version_schema import ModelVersionSchema
from sendmodel.sendmodel import send_model

mv_bp      = Blueprint('model_versions', __name__, url_prefix='/model_versions')
mv_sch     = ModelVersionSchema()
mv_list_sch = ModelVersionSchema(many=True)

@mv_bp.route('/send_model', methods=['POST'])
@jwt_required()
def send_model_to_autodl():
    """
    发送 model.ckpt 到 AutoDL 实例
    """
    try:
        success = send_model()
        if success:
            return jsonify({"msg": "模型推送成功"}), 200
        else:
            return jsonify({"msg": "模型推送失败"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@mv_bp.route('/', methods=['GET'])
@jwt_required()
def list_models():
    """分页查询模型版本"""
    page = request.args.get('page', 1, type=int)
    size = min(request.args.get('size', 10, type=int), 100)
    pag = ModelVersion.query.paginate(page=page, per_page=size, error_out=False)
    return jsonify({
        "total": pag.total,
        "pages": pag.pages,
        "items": mv_list_sch.dump(pag.items)
    }), 200

@mv_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_model(id):
    """获取单个模型版本"""
    mv = ModelVersion.query.get_or_404(id)
    return mv_sch.jsonify(mv), 200

@mv_bp.route('/', methods=['POST'])
@jwt_required()
def create_model():
    """创建模型版本"""
    try:
        data = mv_sch.load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    mv = ModelVersion(**data)
    try:
        db.session.add(mv)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return mv_sch.jsonify(mv), 201

@mv_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_model(id):
    """更新模型版本"""
    mv = ModelVersion.query.get_or_404(id)
    try:
        data = mv_sch.load(request.get_json(), partial=True)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    for k, v in data.items():
        setattr(mv, k, v)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return mv_sch.jsonify(mv), 200

@mv_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_model(id):
    """删除模型版本"""
    mv = ModelVersion.query.get_or_404(id)
    try:
        db.session.delete(mv)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    return jsonify({"message": "已删除"}), 200

@mv_bp.route('/<int:id>/online', methods=['POST'])
@jwt_required()
def set_online(id):
    """将指定版本设为在线，其他版本下线"""
    mv = ModelVersion.query.get_or_404(id)
    try:
        # 先全部下线
        ModelVersion.query.update({"is_active": False})
        mv.is_active = True
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    return jsonify({"message": f"版本 {id} 已上线"}), 200

@mv_bp.route('/current', methods=['GET'])
def get_current():
    """获取当前在线的模型版本"""
    mv = ModelVersion.query.filter_by(is_active=True).first()
    if not mv:
        return jsonify({"error": "无在线版本"}), 404
    return mv_sch.jsonify(mv), 200
