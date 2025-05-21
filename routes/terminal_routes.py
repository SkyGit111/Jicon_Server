from flask import Blueprint, request, jsonify
from extensions import db
from models.terminal import Terminal
from schemas.terminal_schema import TerminalSchema
from models.user_group import UserGroup
from datetime import datetime
from flask_jwt_extended import jwt_required

terminal_bp = Blueprint('terminal', __name__, url_prefix='/terminals')
terminal_schema  = TerminalSchema()
terminals_schema = TerminalSchema(many=True)

# 列表 & 分页
@terminal_bp.route('/', methods=['GET'])
@jwt_required()
def list_terminals():
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))
    pag = Terminal.query.paginate(page=page, per_page=size, error_out=False)
    return jsonify({
        "total": pag.total,
        "pages": pag.pages,
        "items": terminals_schema.dump(pag.items)
    }), 200

# 获取单个
@terminal_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_terminal(id):
    terminal = Terminal.query.get_or_404(id)
    return terminal_schema.jsonify(terminal), 200

# 创建
@terminal_bp.route('/', methods=['POST'])
@jwt_required()
def create_terminal():
    json_data = request.get_json()
    # 验证输入
    data = terminal_schema.load(json_data)
    # 检查所属组是否存在
    if not UserGroup.query.get(data['group_id']):
        return jsonify({"msg": f"group_id {data['group_id']} 不存在"}), 400
    # 解析日期
    signin_date = datetime.strptime(data['signin_date'], '%Y-%m-%d %H:%M:%S')
    terminal = Terminal(
        signin_date=signin_date,
        state=data['state'],
        group_id=data['group_id']
    )
    db.session.add(terminal)
    db.session.commit()
    return terminal_schema.jsonify(terminal), 201

# 更新
@terminal_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_terminal(id):
    terminal = Terminal.query.get_or_404(id)
    json_data = request.get_json()
    data = terminal_schema.load(json_data, partial=True)

    if 'signin_date' in data:
        terminal.signin_date = datetime.strptime(data['signin_date'], '%Y-%m-%d %H:%M:%S')
    if 'state' in data:
        terminal.state = data['state']
    if 'group_id' in data:
        if not UserGroup.query.get(data['group_id']):
            return jsonify({"msg": f"group_id {data['group_id']} 不存在"}), 400
        terminal.group_id = data['group_id']

    db.session.commit()
    return terminal_schema.jsonify(terminal), 200

# 删除
@terminal_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_terminal(id):
    terminal = Terminal.query.get_or_404(id)
    db.session.delete(terminal)
    db.session.commit()
    return jsonify({"msg": "删除成功"}), 200
