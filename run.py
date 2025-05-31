#!/usr/bin/env python3
# run.py

from dotenv import load_dotenv
load_dotenv()

import os
from waitress import serve

from app import create_app
from extensions import db
from db_create import reload_vdb

def main():
    app = create_app()

    with app.app_context():
        # 1) 自动建表（若你不使用 Alembic 或手写迁移脚本）
        db.create_all()
        app.logger.info("数据库表已检查/创建完成")
        # 2) 加载向量库
        try:
            reload_vdb()
            app.logger.info("向量库已加载")
        except Exception as e:
            app.logger.error(f"向量库加载失败: {e}")

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5001))
    app.logger.info(f"▶ 启动服务：{host}:{port}")
    print(f"▶ 启动服务：{host}:{port}", flush=True)

    serve(app, host=host, port=port)

if __name__ == "__main__":
    main()
