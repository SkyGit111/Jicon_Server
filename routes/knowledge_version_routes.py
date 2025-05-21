from flask import Blueprint, request, jsonify
from extensions import db
from models.knowledge_version import KnowledgeVersion
from schemas.knowledge_version_schema import KnowledgeVersionSchema
from flask_jwt_extended import jwt_required

knowledge_version_bp = Blueprint('knowledge_version', __name__, url_prefix='/knowledge_versions')
kv_schema = KnowledgeVersionSchema()
kv_list_schema = KnowledgeVersionSchema(many=True)

# 获取所有知识库版本
@knowledge_version_bp.route('/', methods=['GET'])
@jwt_required()
def get_knowledge_versions():
    versions = KnowledgeVersion.query.order_by(KnowledgeVersion.created_at.desc()).all()
    return kv_list_schema.jsonify(versions), 200

# 获取指定ID的知识库版本
@knowledge_version_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_knowledge_version(id):
    version = KnowledgeVersion.query.get_or_404(id)
    return kv_schema.jsonify(version), 200

# 创建新的知识库版本
@knowledge_version_bp.route('/', methods=['POST'])
@jwt_required()
def create_knowledge_version():
    data = kv_schema.load(request.get_json())
    if KnowledgeVersion.query.filter_by(version=data['version']).first():
        return jsonify({"msg": f"版本号 '{data['version']}' 已存在"}), 400
    new_version = KnowledgeVersion(**data)
    db.session.add(new_version)
    db.session.commit()
    return kv_schema.jsonify(new_version), 201

# 更新指定ID的知识库版本
@knowledge_version_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_knowledge_version(id):
    version = KnowledgeVersion.query.get_or_404(id)
    data = kv_schema.load(request.get_json(), partial=True)
    if 'version' in data:
        existing = KnowledgeVersion.query.filter_by(version=data['version']).first()
        if existing and existing.id != id:
            return jsonify({"msg": f"版本号 '{data['version']}' 已存在"}), 400
        version.version = data['version']
    if 'description' in data:
        version.description = data['description']
    db.session.commit()
    return kv_schema.jsonify(version), 200

# 删除指定ID的知识库版本
@knowledge_version_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_knowledge_version(id):
    version = KnowledgeVersion.query.get_or_404(id)
    db.session.delete(version)
    db.session.commit()
    return jsonify({"msg": "删除成功"}), 200
