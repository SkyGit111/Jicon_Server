# app.py

import pkgutil
import importlib
from flask import Flask, Blueprint
from config import Config
from extensions import db, jwt, cors

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ── 1. 初始化所有扩展插件 ─────────────────────────────
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)

    # ── 2. 自动扫描并注册 routes 目录下所有 Blueprint ──────
    #    要求：每个路由文件都必须在顶部定义一个 Blueprint 实例
    import routes
    for finder, module_name, ispkg in pkgutil.iter_modules(routes.__path__):
        module = importlib.import_module(f"routes.{module_name}")
        # 遍历模块中所有属性，寻找 Blueprint 实例并注册
        for attr in vars(module).values():
            if isinstance(attr, Blueprint):
                app.register_blueprint(attr)

    # ── 3. 基本测试接口 ────────────────────────────────────
    @app.route('/')
    def hello():
        return '系统后端运行中'

    return app
