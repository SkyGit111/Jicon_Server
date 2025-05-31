# routes/knowledge_version_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from models.knowledge_version import KnowledgeVersion
from schemas.knowledge_version_schema import KnowledgeVersionSchema

kv_bp = Blueprint('knowledge_versions', __name__, url_prefix='/knowledge_versions')
kv_sch = KnowledgeVersionSchema()
kv_list_sch = KnowledgeVersionSchema(many=True)


@kv_bp.route('/', methods=['GET'], strict_slashes=True)
@jwt_required()
def list_knowledge_versions():
    """
    分页并按创建时间倒序查询知识库版本。
    GET /knowledge_versions?page=<页码>&size=<每页数量>
    """
    page = request.args.get('page', 1, type=int)
    size = min(request.args.get('size', 10, type=int), 100)
    pag = (KnowledgeVersion.query
           .order_by(KnowledgeVersion.created_at.desc())
           .paginate(page=page, per_page=size, error_out=False))
    return jsonify({
        "total": pag.total,
        "pages": pag.pages,
        "items": kv_list_sch.dump(pag.items)
    }), 200


@kv_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_knowledge_version(id):
    """
    获取指定 ID 的知识库版本详情。
    GET /knowledge_versions/<id>
    """
    kv = KnowledgeVersion.query.get_or_404(id)
    return kv_sch.jsonify(kv), 200


@kv_bp.route('/', methods=['POST'])
@jwt_required()
def create_knowledge_version():
    """
    创建新的知识库版本。
    POST /knowledge_versions
    Body JSON: { "version": "...", "description": "..." }
    """
    try:
        data = kv_sch.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    # 唯一性校验
    if KnowledgeVersion.query.filter_by(version=data['version']).first():
        return jsonify({"error": f"版本号 '{data['version']}' 已存在"}), 400

    kv = KnowledgeVersion(**data)
    try:
        db.session.add(kv)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return kv_sch.jsonify(kv), 201


@kv_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_knowledge_version(id):
    """
    更新已有知识库版本的元数据（仅支持 version 和 description 字段）。
    PUT /knowledge_versions/<id>
    """
    kv = KnowledgeVersion.query.get_or_404(id)
    try:
        data = kv_sch.load(request.get_json() or {}, partial=True)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    # version 唯一性校验
    if 'version' in data:
        existing = KnowledgeVersion.query.filter_by(version=data['version']).first()
        if existing and existing.id != id:
            return jsonify({"error": f"版本号 '{data['version']}' 已存在"}), 400
        kv.version = data['version']

    if 'description' in data:
        kv.description = data['description']

    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return kv_sch.jsonify(kv), 200


@kv_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_knowledge_version(id):
    """
    删除指定的知识库版本。
    DELETE /knowledge_versions/<id>
    """
    kv = KnowledgeVersion.query.get_or_404(id)
    try:
        db.session.delete(kv)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "删除成功"}), 200
