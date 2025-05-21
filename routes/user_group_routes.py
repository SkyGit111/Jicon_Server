# routes/user_group_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
from models.user_group import UserGroup
from models.terminal import Terminal
from schemas.user_group_schema import UserGroupSchema
from marshmallow import ValidationError

user_group_bp = Blueprint('user_group', __name__, url_prefix='/user_groups')
group_schema  = UserGroupSchema()
groups_schema = UserGroupSchema(many=True)


@user_group_bp.route('/', methods=['GET'])
@jwt_required()
def list_groups():
    """
    列表 & 分页
    GET /user_groups?page=1&size=10
    """
    page = request.args.get('page', default=1, type=int)
    size = min(request.args.get('size', default=10, type=int), 100)
    pag = UserGroup.query.paginate(page=page, per_page=size, error_out=False)
    return jsonify({
        "total": pag.total,
        "pages": pag.pages,
        "items": groups_schema.dump(pag.items)
    }), 200


@user_group_bp.route('/<int:group_id>', methods=['GET'])
@jwt_required()
def get_group(group_id):
    """
    获取单个用户组
    GET /user_groups/<group_id>
    """
    group = UserGroup.query.get_or_404(group_id)
    return group_schema.jsonify(group), 200


@user_group_bp.route('/', methods=['POST'])
@jwt_required()
def create_group():
    """
    创建用户组
    POST /user_groups
    Body: { "name": "...", "members": "..." }
    """
    try:
        data = group_schema.load(request.get_json() or {})
    except ValidationError as ve:
        return jsonify({"error": ve.messages}), 400

    group = UserGroup(**data)
    try:
        db.session.add(group)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"创建用户组失败: {str(e)}"}), 500

    return group_schema.jsonify(group), 201


@user_group_bp.route('/<int:group_id>', methods=['PUT'])
@jwt_required()
def update_group(group_id):
    """
    更新用户组
    PUT /user_groups/<group_id>
    Body: { "name": "...", "members": "..." }
    """
    group = UserGroup.query.get_or_404(group_id)
    try:
        data = group_schema.load(request.get_json() or {}, partial=True)
    except ValidationError as ve:
        return jsonify({"error": ve.messages}), 400

    for attr, val in data.items():
        setattr(group, attr, val)

    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"更新用户组失败: {str(e)}"}), 500

    return group_schema.jsonify(group), 200


@user_group_bp.route('/<int:group_id>', methods=['DELETE'])
@jwt_required()
def delete_group(group_id):
    """
    删除用户组
    DELETE /user_groups/<group_id>
    """
    group = UserGroup.query.get_or_404(group_id)
    try:
        db.session.delete(group)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"删除用户组失败: {str(e)}"}), 500

    return jsonify({"msg": "删除成功"}), 200


@user_group_bp.route('/<int:group_id>/members', methods=['POST'])
@jwt_required()
def add_member(group_id):
    """
    将指定 terminal_id 的终端添加到指定用户组
    POST /user_groups/<group_id>/members
    Body: { "terminal_id": 123 }
    """
    group = UserGroup.query.get_or_404(group_id)
    req = request.get_json() or {}
    terminal_id = req.get('terminal_id')
    if terminal_id is None:
        return jsonify({"error": "缺少 terminal_id 参数"}), 400

    term = Terminal.query.get(terminal_id)
    if not term:
        return jsonify({"error": f"终端 {terminal_id} 不存在"}), 400

    try:
        # 更新 Terminal.group_id
        term.group_id = group_id

        # 可选：同步维护 group.members 字段
        members = [m for m in (group.members or '').split(',') if m]
        if str(terminal_id) not in members:
            members.append(str(terminal_id))
        group.members = ','.join(members)

        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"添加成员失败: {str(e)}"}), 500

    current_members = [int(x) for x in (group.members or '').split(',') if x]
    return jsonify({
        "group_id": group_id,
        "members": current_members
    }), 200


@user_group_bp.route('/<int:group_id>/members/<int:terminal_id>', methods=['DELETE'])
@jwt_required()
def remove_member(group_id, terminal_id):
    """
    从指定用户组移除终端
    DELETE /user_groups/<group_id>/members/<terminal_id>
    """
    group = UserGroup.query.get_or_404(group_id)
    term = Terminal.query.get_or_404(terminal_id)

    # 解除关联
    try:
        if term.group_id != group_id:
            return jsonify({"error": f"终端 {terminal_id} 不在组 {group_id} 中"}), 400
        term.group_id = None

        # 更新 members 字段
        members = [m for m in (group.members or '').split(',') if m]
        str_id = str(terminal_id)
        if str_id in members:
            members.remove(str_id)
        group.members = ','.join(members)

        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"移除成员失败: {str(e)}"}), 500

    current_members = [int(x) for x in (group.members or '').split(',') if x]
    return jsonify({
        "group_id": group_id,
        "members": current_members
    }), 200


@user_group_bp.route('/<int:group_id>/members', methods=['GET'])
@jwt_required()
def get_members(group_id):
    """
    获取用户组所有成员
    GET /user_groups/<group_id>/members
    """
    group = UserGroup.query.get_or_404(group_id)
    members = [int(m) for m in (group.members or '').split(',') if m]
    return jsonify({"group_id": group_id, "members": members}), 200
