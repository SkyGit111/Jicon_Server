from datetime import timedelta

from flask import Flask, jsonify

from extension import init_extension

from flask_cors import CORS

from Controller.MarketController import marketcontroller
from Controller.UserController import usercontroller
from Controller.ChatController import chatcontoller
from Controller.AgentCreationController import agentcreationcontroller

from databasecfg import Config

from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)


# 设置 JWT 的有效时长为 1 小时
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
# JWT配置
app.config['JWT_SECRET_KEY'] = 'wuchensercet123456789'  # Change this!
jwt = JWTManager(app)


# 跨域
CORS(app, resources={r"/*": {"origins": "*"}})

# class Config(object):
#     # 数据库配置
#     # mysql+pymysql://用户名:密码@localhost:3306/数据库名
#     SQLALCHEMY_DATABASE_URI = 'mysql://wuchen:WUchen24863179@101.37.88.111:3306/razor-ai'
#     # 设置每次请求结束后会自动提交数据库中的改动
#     SQLALCHEMY_COMMIT_ON_TEARDOWN = False
#     # 设置执行完操作后自动提交
#     SQLALCHEMY_TRACK_MODIFICATIONS = True

# 使用从 databasecfg 导入的 Config 类进行配置
app.config.from_object(Config)

# 初始化拓展
init_extension(app=app)

# app.register_blueprint(xxxx,url_prefix='/xxx')   # 添加蓝图
# app.register_blueprint(blueprint=admin)  # 后台管理
app.register_blueprint(blueprint=usercontroller)  # user
app.register_blueprint(blueprint=chatcontoller)  # chat
app.register_blueprint(blueprint=agentcreationcontroller)  #
app.register_blueprint(blueprint=marketcontroller)


# 路由
@app.route('/')
def hello_world():
    return 'RAZOR-AI后端'


@app.route('/test')
def frontend_test():
    data = {'code': 200, 'data': '前端请求测试'}
    return jsonify(data)

# if __name__ == '__main__':
#     app.run(debug=True)
