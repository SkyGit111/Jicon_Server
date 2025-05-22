# routes/vectordb_routes.py

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from db_create.db_create import create_vdb, reload_vdb, vector_db

vectordb_bp = Blueprint('vectordb', __name__, url_prefix='/vectordb')


@vectordb_bp.route('/status', methods=['GET'])
@jwt_required()
def status():
    """
    查询向量库当前加载状态。
    GET /vectordb/status
    返回 JSON:
      { "loaded": <true|false> }
    """
    try:
        loaded = vector_db is not None
        return jsonify({"loaded": loaded}), 200
    except Exception as e:
        return jsonify({"error": f"查询向量库状态失败: {e}"}), 500


@vectordb_bp.route('/reload', methods=['POST'])
@jwt_required()
def reload_db():
    """
    在线重载本地向量库（调用 reload_vdb）。
    POST /vectordb/reload
    返回 JSON:
      { "status": "reloaded" }
    """
    try:
        reload_vdb()
        return jsonify({"status": "reloaded"}), 200
    except Exception as e:
        return jsonify({"error": f"重载向量库失败: {e}"}), 500


@vectordb_bp.route('/create', methods=['POST'])
@jwt_required()
def create_db():
    """
    从源数据重建向量库（调用 create_vdb）。
    POST /vectordb/create
    返回 JSON:
      { "status": "created" }
    """
    try:
        create_vdb()
        return jsonify({"status": "created"}), 200
    except Exception as e:
        return jsonify({"error": f"创建向量库失败: {e}"}), 500
