# routes/terminal_routes.py

import random
from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from models.terminal import Terminal
from models.user_group import UserGroup
from schemas.terminal_schema import TerminalSchema

terminal_bp      = Blueprint('terminals', __name__, url_prefix='/terminals')
terminal_schema  = TerminalSchema()
terminals_schema = TerminalSchema(many=True)
MAX_PAGE_SIZE    = 100


@terminal_bp.route('/', methods=['GET'])
@jwt_required()
def list_terminals():
    """
    分页查询设备列表。
    GET /terminals?page=<页码>&size=<每页数量>
    """
    page = request.args.get('page', 1, type=int)
    size = min(request.args.get('size', 10, type=int), MAX_PAGE_SIZE)
    pag = Terminal.query.paginate(page=page, per_page=size, error_out=False)
    return jsonify({
        "total": pag.total,
        "pages": pag.pages,
        "items": terminals_schema.dump(pag.items)
    }), 200


@terminal_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_terminal(id):
    """
    获取单个设备详情。
    GET /terminals/<id>
    """
    term = Terminal.query.get_or_404(id)
    return terminal_schema.jsonify(term), 200


@terminal_bp.route('/', methods=['POST'])
def create_terminal():
    """
    注册新设备。
    POST /terminals
    Body JSON:
      {
        "signin_date": "YYYY-MM-DD HH:MM:SS"
      }
    说明：
      - 用户端只需要传 signin_date，系统自动：
        1) 生成一个唯一的 terminal.id（由数据库自增）
        2) state 默认为 True
        3) 从 [UserGroup] 中随机选一个 group_id
      - 返回新建终端记录 JSON，包括自动分配的 id、signin_date、state、group_id。
    """
    # 1) 校验并读取 signin_date
    try:
        data = request.get_json() or {}
        # 只关心 signin_date；其余字段忽略
        if 'signin_date' not in data:
            return jsonify({"error": "缺少必填字段 signin_date"}), 400
        signin_date_str = data['signin_date']
        # 解析 datetime
        sd = datetime.strptime(signin_date_str, '%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return jsonify({"error": "signin_date 格式错误，须 YYYY-MM-DD HH:MM:SS"}), 400

    # 2) 随机从 UserGroup 表中选一个 group_id
    user_groups = UserGroup.query.with_entities(UserGroup.id).all()
    if not user_groups:
        return jsonify({"error": "系统中没有可用的用户组，请先创建至少一个 UserGroup"}), 400

    # user_groups 是 [(1,), (2,), ...]，转换成单纯的列表 [1,2,...]
    group_ids = [ug[0] for ug in user_groups]
    random_group_id = random.choice(group_ids)

    # 3) state 默认为 True
    default_state = True

    # 4) 构造并保存 Terminal 实例
    term = Terminal(
        signin_date=sd,
        state=default_state,
        group_id=random_group_id
    )
    try:
        db.session.add(term)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    # 5) 返回新建的终端对象
    return terminal_schema.jsonify(term), 201


@terminal_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_terminal(id):
    """
    更新设备信息（可选更新 signin_date、state、group_id）。
    PUT /terminals/<id>
    Body JSON 可包含任意组合的字段：
      {
        "signin_date": "YYYY-MM-DD HH:MM:SS",  # 可选
        "state": <true|false>,                  # 可选
        "group_id": <int>                       # 可选
      }
    """
    term = Terminal.query.get_or_404(id)

    # 1) 校验（部分更新）
    try:
        data = terminal_schema.load(request.get_json() or {}, partial=True)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    # 2) 字段赋值与校验
    if 'signin_date' in data:
        try:
            term.signin_date = datetime.strptime(data['signin_date'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return jsonify({"error": "signin_date 格式错误，须 YYYY-MM-DD HH:MM:SS"}), 400

    if 'state' in data:
        term.state = data['state']

    if 'group_id' in data:
        # 检查 group_id 是否存在
        if not UserGroup.query.get(data['group_id']):
            return jsonify({"error": f"group_id {data['group_id']} 不存在"}), 400
        term.group_id = data['group_id']

    # 3) 提交事务
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return terminal_schema.jsonify(term), 200


@terminal_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_terminal(id):
    """
    删除指定设备。
    DELETE /terminals/<id>
    """
    term = Terminal.query.get_or_404(id)

    try:
        db.session.delete(term)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "删除成功"}), 200
