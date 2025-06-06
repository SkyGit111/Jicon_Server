# app.py

import pkgutil
import importlib
from flask import Flask, Blueprint

from config import Config
from extensions import init_extensions

# APScheduler 相关
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# 定时任务函数
from services.batch_update import check_and_update_csv_and_vdb


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ── 1. 初始化所有扩展插件 ─────────────────────────────
    init_extensions(app)

    # ── 2. 自动扫描 routes 目录下所有 Blueprint ──────────
    import routes
    # 我们会把少数需要前缀的 Blueprint 单独注册
    # 先收集所有 Blueprint 对象
    blueprint_map = {}  # { blueprint_name: blueprint_object }
    for finder, module_name, ispkg in pkgutil.iter_modules(routes.__path__):
        module = importlib.import_module(f"routes.{module_name}")
        for attr in vars(module).values():
            if isinstance(attr, Blueprint):
                # attr.name 对应定义时传入的第一个参数
                blueprint_map[attr.name] = attr

    # 2.1) 手动给“结果反馈”这一组加 url_prefix="/results"
    if "res_bp" in blueprint_map:
        app.register_blueprint(blueprint_map["res_bp"], url_prefix="/results")

    # 2.2) 给“消息”这一组加 url_prefix="/messages"
    if "msg_bp" in blueprint_map:
        app.register_blueprint(blueprint_map["msg_bp"], url_prefix="/messages")

    # 2.3) 给“检测”这一组加 url_prefix="/detections"
    if "det_bp" in blueprint_map:
        app.register_blueprint(blueprint_map["det_bp"], url_prefix="/detections")

    # 2.4) 其余 Blueprint 若不需要前缀，就直接注册
    for name, bp in blueprint_map.items():
        if name not in ("res_bp", "msg_bp", "det_bp"):
            app.register_blueprint(bp)

    # ── 3. 定时任务：每隔一段时间批量更新 CSV + 重建向量库 ───
    scheduler = BackgroundScheduler()
    # 从配置读取任务间隔，默认 3600 秒（1 小时）
    interval_seconds = app.config.get("JOB_INTERVAL_SECONDS", 3600)
    trigger = IntervalTrigger(seconds=interval_seconds)

    # 把 Flask app 传进去，让任务内部能用 app.app_context()
    scheduler.add_job(
        func=check_and_update_csv_and_vdb,
        trigger=trigger,
        args=[app],
        id="batch_update_job",
        name="Batch update CSV and rebuild vector DB",
        replace_existing=True
    )
    scheduler.start()

    # ── 4. 基本测试接口 ────────────────────────────────────
    @app.route("/")
    def hello():
        return "系统后端运行中"

    return app
