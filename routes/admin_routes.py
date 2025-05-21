from flask import Blueprint, request, jsonify
from extensions import db
from models.admin import Admin
from schemas.admin_schema import AdminSchema
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
admin_schema  = AdminSchema()
admins_schema = AdminSchema(many=True)

# 注册（signup）
@admin_bp.route('/signup', methods=['POST'])
def signup():
    data = admin_schema.load(request.get_json())
    if Admin.query.filter_by(email=data['email']).first():
        return jsonify({"msg": "Email 已被使用"}), 400
    admin = Admin(**data)
    db.session.add(admin)
    db.session.commit()
    return admin_schema.jsonify(admin), 201

# 登录（signin）
@admin_bp.route('/signin', methods=['POST'])
def signin():
    body = request.get_json()
    admin = Admin.query.filter_by(email=body.get('email')).first()
    if not admin or admin.disabled or admin.password != body.get('password'):
        return jsonify({"msg": "账号或密码错误"}), 401
    token = create_access_token(identity=admin.id)
    return jsonify({"access_token": token}), 200

# 修改密码（changePwd）
@admin_bp.route('/<int:id>/password', methods=['PUT'])
@jwt_required()
def change_pwd(id):
    admin = Admin.query.get_or_404(id)
    data = request.get_json()
    new_pwd = data.get('password')
    if not new_pwd or len(new_pwd) < 6:
        return jsonify({"msg": "密码长度至少 6 位"}), 400
    admin.password = new_pwd
    db.session.commit()
    return jsonify({"msg": "密码更新成功"}), 200

# 禁用（disable）
@admin_bp.route('/<int:id>/disable', methods=['PUT'])
@jwt_required()
def disable(id):
    admin = Admin.query.get_or_404(id)
    admin.disabled = True
    db.session.commit()
    return jsonify({"msg": "管理员已禁用"}), 200

# 查询所有 & 分页
@admin_bp.route('/', methods=['GET'])
@jwt_required()
def list_admins():
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))
    pag = Admin.query.paginate(page=page, per_page=size, error_out=False)
    return jsonify({
        "total": pag.total,
        "pages": pag.pages,
        "items": admins_schema.dump(pag.items)
    }), 200

# 获取单个
@admin_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_admin(id):
    admin = Admin.query.get_or_404(id)
    return admin_schema.jsonify(admin), 200

# CRUD: 创建
@admin_bp.route('/', methods=['POST'])
@jwt_required()
def create_admin():
    data = admin_schema.load(request.get_json())
    admin = Admin(**data)
    db.session.add(admin)
    db.session.commit()
    return admin_schema.jsonify(admin), 201

# CRUD: 更新
@admin_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_admin(id):
    admin = Admin.query.get_or_404(id)
    data = admin_schema.load(request.get_json(), partial=True)
    for k, v in data.items():
        setattr(admin, k, v)
    db.session.commit()
    return admin_schema.jsonify(admin), 200

# CRUD: 删除
@admin_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_admin(id):
    admin = Admin.query.get_or_404(id)
    db.session.delete(admin)
    db.session.commit()
    return jsonify({"msg": "删除成功"}), 200
