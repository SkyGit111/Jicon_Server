from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from User.UserService import UserService

usercontroller = Blueprint('user', __name__)


@usercontroller.route('/user/login', methods=['POST'])
def login():
    data = request.get_json()
    user_id = data.get('user_id')
    user_password = data.get('user_password')
    if UserService.login(user_id=user_id, user_password=user_password):
        # 创建访问令牌
        token = create_access_token(identity=user_id)
        user_name = UserService.getUsername(user_id)
        return jsonify(token=token, message='登陆成功',username=user_name), 200
    else:
        return jsonify(message='登陆失败，账号或密码错误'), 402


@usercontroller.route('/user/register', methods=['POST'])
def register():
    data = request.get_json()
    user_name = data.get('user_name')
    user_password = data.get('user_password')
    user_password = UserService.hash_password(user_password)
    user = UserService.register(user_name, user_password)
    return jsonify(user_id=UserService.getId(user), message='注册成功'), 200
