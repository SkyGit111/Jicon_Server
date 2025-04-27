from flask import Blueprint, render_template, request, redirect, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from Models.Admin import Admin

admin_blue = Blueprint('admin', __name__)


@admin_blue.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    admin_name = data.get('admin_name')
    admin_password = data.get('admin_password')

    if not admin_name or not admin_password:
        return jsonify({'message': 'Username and password are required'}), 400

    # 检查管理员账户
    admin = Admin.query.filter_by(admin_name=admin_name,admin_password=admin_password).first()
    # if admin and check_password_hash(admin.admin_password, password):
    if admin:
        access_token = create_access_token(identity=admin_name)
        response = {
            "message": "user login successful",
            "user": {
                "access_token": access_token,
                "user_id": admin.admin_id,
                'user_name': admin_name
            }
        }
        return jsonify(response), 200
    else:
        response = {
            "message": "user login failed",
            "user": {

                "user_id": admin.admin_id,
                'user_name': admin_name
            }
        }
        return jsonify(response), 401

@admin_blue.route('/admin/info', methods=['GET'])
@jwt_required()  # 需要Token验证
def protected():
    # 获取当前Token中的用户信息
    current_admin = get_jwt_identity()
    return jsonify(logged_in_as=current_admin), 200