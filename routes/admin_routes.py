# routes/admin_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

from extensions import db
from models.admin import Admin
from schemas.admin_schema import AdminSchema

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Schemas
admin_schema   = AdminSchema()
admins_schema  = AdminSchema(many=True)


@admin_bp.route('/signup', methods=['POST'])
def signup():
    """
    注册新管理员（公开接口，不需登录）。
    """
    try:
        data = admin_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    if Admin.query.filter_by(email=data['email']).first():
        return jsonify({"error": "邮箱已被使用"}), 400

    admin = Admin(**data)
    try:
        db.session.add(admin)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return admin_schema.jsonify(admin), 201


@admin_bp.route('/signin', methods=['POST'])
def signin():
    """
    管理员登录，返回 JWT token（公开接口）。
    """
    body = request.get_json() or {}
    email = body.get('email')
    password = body.get('password')
    if not email or not password:
        return jsonify({"error": "缺少 email 或 password"}), 400

    admin = Admin.query.filter_by(email=email).first()
    if not admin or admin.disabled or admin.password != password:
        return jsonify({"error": "账号或密码错误"}), 401

    token = create_access_token(identity=admin.id)
    return jsonify({"access_token": token}), 200


@admin_bp.route('/<int:id>/password', methods=['PUT'])
@jwt_required()
def change_password(id):
    """
    修改管理员密码（需登录）。
    """
    admin = Admin.query.get_or_404(id)
    data = request.get_json() or {}
    new_pwd = data.get('password')
    if not new_pwd or len(new_pwd) < 6:
        return jsonify({"error": "密码长度至少 6 位"}), 400

    admin.password = new_pwd
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "密码更新成功"}), 200


@admin_bp.route('/<int:id>/disable', methods=['PUT'])
@jwt_required()
def disable_admin(id):
    """
    禁用管理员账号（需登录）。
    """
    admin = Admin.query.get_or_404(id)
    admin.disabled = True
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "管理员已禁用"}), 200


@admin_bp.route('/', methods=['GET'])
@jwt_required()
def list_admins():
    """
    分页查询管理员列表（需登录）。
    """
    page = request.args.get('page', 1, type=int)
    size = min(request.args.get('size', 10, type=int), 100)
    pag = Admin.query.paginate(page=page, per_page=size, error_out=False)
    return jsonify({
        "total": pag.total,
        "pages": pag.pages,
        "items": admins_schema.dump(pag.items)
    }), 200


@admin_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_admin(id):
    """
    获取单个管理员详情（需登录）。
    """
    admin = Admin.query.get_or_404(id)
    return admin_schema.jsonify(admin), 200


@admin_bp.route('/', methods=['POST'])
@jwt_required()
def create_admin():
    """
    创建管理员（需登录）。
    """
    try:
        data = admin_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    if Admin.query.filter_by(email=data['email']).first():
        return jsonify({"error": "邮箱已存在"}), 400

    admin = Admin(**data)
    try:
        db.session.add(admin)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return admin_schema.jsonify(admin), 201


@admin_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_admin(id):
    """
    更新管理员信息（需登录）。
    """
    admin = Admin.query.get_or_404(id)
    try:
        data = admin_schema.load(request.get_json() or {}, partial=True)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    for key, val in data.items():
        setattr(admin, key, val)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return admin_schema.jsonify(admin), 200


@admin_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_admin(id):
    """
    删除管理员（需登录）。
    """
    admin = Admin.query.get_or_404(id)
    try:
        db.session.delete(admin)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "删除成功"}), 200
