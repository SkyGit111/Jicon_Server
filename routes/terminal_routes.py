# routes/terminal_routes.py

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
@jwt_required()
def create_terminal():
    """
    注册新设备。
    POST /terminals
    Body JSON:
      {
        "signin_date": "YYYY-MM-DD HH:MM:SS",
        "state": <true|false>,
        "group_id": <int>
      }
    """
    # 1) 数据校验
    try:
        data = terminal_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    # 2) 所属用户组检查
    if not UserGroup.query.get(data['group_id']):
        return jsonify({"error": f"group_id {data['group_id']} 不存在"}), 400

    # 3) 解析日期
    try:
        sd = datetime.strptime(data['signin_date'], '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({"error": "signin_date 格式错误，须 YYYY-MM-DD HH:MM:SS"}), 400

    # 4) 创建并提交
    term = Terminal(signin_date=sd, state=data['state'], group_id=data['group_id'])
    try:
        db.session.add(term)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return terminal_schema.jsonify(term), 201


@terminal_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_terminal(id):
    """
    更新设备信息（可选更新 signin_date、state、group_id）。
    PUT /terminals/<id>
    """
    term = Terminal.query.get_or_404(id)

    # 1) 数据校验（部分更新）
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
