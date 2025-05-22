# routes/user_group_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from models.user_group import UserGroup
from models.terminal   import Terminal
from schemas.user_group_schema import UserGroupSchema

user_group_bp  = Blueprint('user_groups', __name__, url_prefix='/user_groups')
group_schema   = UserGroupSchema()
groups_schema  = UserGroupSchema(many=True)
MAX_PAGE_SIZE  = 100


@user_group_bp.route('/', methods=['GET'])
@jwt_required()
def list_groups():
    """
    分页查询用户组列表。
    GET /user_groups?page=<页码>&size=<每页大小>
    """
    page = request.args.get('page', 1, type=int)
    size = min(request.args.get('size', 10, type=int), MAX_PAGE_SIZE)
    pagination = UserGroup.query.paginate(page=page, per_page=size, error_out=False)
    return jsonify({
        "total": pagination.total,
        "pages": pagination.pages,
        "items": groups_schema.dump(pagination.items)
    }), 200


@user_group_bp.route('/<int:group_id>', methods=['GET'])
@jwt_required()
def get_group(group_id):
    """
    获取单个用户组详情。
    GET /user_groups/<group_id>
    """
    group = UserGroup.query.get_or_404(group_id)
    return group_schema.jsonify(group), 200


@user_group_bp.route('/', methods=['POST'])
@jwt_required()
def create_group():
    """
    创建新用户组。
    POST /user_groups
    Body JSON: { "name": "<组名>", "members": "<逗号分隔的 terminal_id 列表，可选>" }
    """
    try:
        data = group_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    group = UserGroup(**data)
    try:
        db.session.add(group)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"创建用户组失败: {e}"}), 500

    return group_schema.jsonify(group), 201


@user_group_bp.route('/<int:group_id>', methods=['PUT'])
@jwt_required()
def update_group(group_id):
    """
    更新用户组信息（组名或成员列表）。
    PUT /user_groups/<group_id>
    Body JSON: 同创建接口，可部分字段更新
    """
    group = UserGroup.query.get_or_404(group_id)
    try:
        data = group_schema.load(request.get_json() or {}, partial=True)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    for key, val in data.items():
        setattr(group, key, val)

    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"更新用户组失败: {e}"}), 500

    return group_schema.jsonify(group), 200


@user_group_bp.route('/<int:group_id>', methods=['DELETE'])
@jwt_required()
def delete_group(group_id):
    """
    删除指定用户组。
    DELETE /user_groups/<group_id>
    """
    group = UserGroup.query.get_or_404(group_id)
    try:
        db.session.delete(group)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"删除用户组失败: {e}"}), 500

    return jsonify({"message": "删除成功"}), 200


@user_group_bp.route('/<int:group_id>/members', methods=['POST'])
@jwt_required()
def add_member(group_id):
    """
    将指定 terminal_id 的终端添加到用户组。
    POST /user_groups/<group_id>/members
    Body JSON: { "terminal_id": <int> }
    """
    group = UserGroup.query.get_or_404(group_id)
    payload = request.get_json() or {}
    term_id = payload.get('terminal_id')
    if term_id is None:
        return jsonify({"error": "缺少 terminal_id 参数"}), 400

    term = Terminal.query.get(term_id)
    if not term:
        return jsonify({"error": f"终端 {term_id} 不存在"}), 400

    try:
        # 1) 关联 Terminal
        term.group_id = group_id

        # 2) 同步维护 group.members 字段（逗号分隔）
        existing = [m for m in (group.members or '').split(',') if m]
        if str(term_id) not in existing:
            existing.append(str(term_id))
        group.members = ','.join(existing)

        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"添加成员失败: {e}"}), 500

    members = [int(x) for x in (group.members or '').split(',') if x]
    return jsonify({"group_id": group_id, "members": members}), 200


@user_group_bp.route('/<int:group_id>/members/<int:term_id>', methods=['DELETE'])
@jwt_required()
def remove_member(group_id, term_id):
    """
    从用户组中移除指定终端。
    DELETE /user_groups/<group_id>/members/<term_id>
    """
    group = UserGroup.query.get_or_404(group_id)
    term  = Terminal.query.get_or_404(term_id)

    if term.group_id != group_id:
        return jsonify({"error": f"终端 {term_id} 不在组 {group_id} 中"}), 400

    try:
        # 1) 解除关联
        term.group_id = None

        # 2) 更新 members 字段
        members = [m for m in (group.members or '').split(',') if m]
        members = [m for m in members if m != str(term_id)]
        group.members = ','.join(members)

        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"移除成员失败: {e}"}), 500

    members = [int(x) for x in (group.members or '').split(',') if x]
    return jsonify({"group_id": group_id, "members": members}), 200


@user_group_bp.route('/<int:group_id>/members', methods=['GET'])
@jwt_required()
def get_members(group_id):
    """
    获取用户组内所有终端成员 ID 列表。
    GET /user_groups/<group_id>/members
    """
    group = UserGroup.query.get_or_404(group_id)
    members = [int(m) for m in (group.members or '').split(',') if m]
    return jsonify({"group_id": group_id, "members": members}), 200
