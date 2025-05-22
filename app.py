# app.py

import pkgutil
import importlib
from flask import Flask, Blueprint
from config import Config
from extensions import init_extensions

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ── 1. 初始化所有扩展插件 ─────────────────────────────
    init_extensions(app)

    # ── 2. 自动扫描并注册 routes 目录下所有 Blueprint ──────
    import routes
    for finder, module_name, ispkg in pkgutil.iter_modules(routes.__path__):
        module = importlib.import_module(f"routes.{module_name}")
        for attr in vars(module).values():
            if isinstance(attr, Blueprint):
                app.register_blueprint(attr)

    # ── 3. 基本测试接口 ────────────────────────────────────
    @app.route('/')
    def hello():
        return '系统后端运行中'

    return app

