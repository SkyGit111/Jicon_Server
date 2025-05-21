# routes/model_version_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
from models.model_version import ModelVersion
from schemas.model_version_schema import ModelVersionSchema
from marshmallow import ValidationError

model_version_bp = Blueprint('model_version', __name__, url_prefix='/model_versions')
mv_schema        = ModelVersionSchema()
mv_list_schema   = ModelVersionSchema(many=True)

MAX_PAGE_SIZE = 100

@model_version_bp.route('/', methods=['GET'])
@jwt_required()
def list_model_versions():
    """
    列表 & 分页
    GET /model_versions?page=1&size=10
    """
    page = request.args.get('page', default=1, type=int)
    size = min(request.args.get('size', default=10, type=int), MAX_PAGE_SIZE)
    pag = ModelVersion.query.order_by(ModelVersion.id.desc()) \
             .paginate(page=page, per_page=size, error_out=False)
    return jsonify({
        "total": pag.total,
        "pages": pag.pages,
        "items": mv_list_schema.dump(pag.items)
    }), 200


@model_version_bp.route('/<int:version_id>', methods=['GET'])
@jwt_required()
def get_model_version(version_id):
    """
    获取单条模型版本
    GET /model_versions/<version_id>
    """
    mv = ModelVersion.query.get_or_404(version_id)
    return mv_schema.jsonify(mv), 200


@model_version_bp.route('/', methods=['POST'])
@jwt_required()
def create_model_version():
    """
    创建新模型版本
    POST /model_versions
    Body: { "description": "说明" }
    """
    try:
        data = request.get_json() or {}
        desc = data.get('description', '')
        # 可选：长度校验
        if len(desc) > 255:
            return jsonify({"error": "description 长度不能超过 255"}), 400

        mv = ModelVersion(description=desc)
        db.session.add(mv)
        db.session.commit()
        return mv_schema.jsonify(mv), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"创建模型版本失败: {str(e)}"}), 500


@model_version_bp.route('/<int:version_id>', methods=['PUT'])
@jwt_required()
def update_model_version(version_id):
    """
    更新模型版本描述
    PUT /model_versions/<version_id>
    Body: { "description": "新说明" }
    """
    mv = ModelVersion.query.get_or_404(version_id)
    data = request.get_json() or {}
    desc = data.get('description')

    if desc is None:
        return jsonify({"error": "缺少 description 参数"}), 400
    if len(desc) > 255:
        return jsonify({"error": "description 长度不能超过 255"}), 400

    try:
        mv.description = desc
        db.session.commit()
        return mv_schema.jsonify(mv), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"更新模型版本失败: {str(e)}"}), 500


@model_version_bp.route('/<int:version_id>', methods=['DELETE'])
@jwt_required()
def delete_model_version(version_id):
    """
    删除模型版本
    DELETE /model_versions/<version_id>
    """
    mv = ModelVersion.query.get_or_404(version_id)
    try:
        db.session.delete(mv)
        db.session.commit()
        return jsonify({"msg": "删除成功"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"删除模型版本失败: {str(e)}"}), 500


@model_version_bp.route('/<int:version_id>/online', methods=['PUT'])
@jwt_required()
def online_model_version(version_id):
    """
    上线指定模型版本
    PUT /model_versions/<version_id>/online
    """
    try:
        # 开启事务
        # 先置为非激活，再置指定版本为激活
        ModelVersion.query.update({ModelVersion.is_active: False})
        mv = ModelVersion.query.get_or_404(version_id)
        mv.is_active = True
        db.session.commit()
        return jsonify({"msg": f"版本 {version_id} 已上线"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"上线模型版本失败: {str(e)}"}), 500


@model_version_bp.route('/current', methods=['GET'])
@jwt_required()
def get_current_model_version():
    """
    获取当前在线模型版本
    GET /model_versions/current
    """
    mv = ModelVersion.query.filter_by(is_active=True).first()
    if not mv:
        return jsonify({"error": "暂无在线版本"}), 404
    return mv_schema.jsonify(mv), 200
