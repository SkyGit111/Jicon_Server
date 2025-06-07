# check_models_vs_db.py
import os, sys
from sqlalchemy import inspect

# 确保能 import 到项目根的 app.py、extensions
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

from app import create_app
from extensions import db

app = create_app()
with app.app_context():
    insp = inspect(db.engine)
    db_tables    = set(insp.get_table_names())
    model_tables = set(db.metadata.tables.keys())

    print("数据库中实际表：", db_tables)
    print("模型中定义表：  ", model_tables)
    print("【缺失】模型有、DB 没有：", model_tables - db_tables)
    print("【多余】DB 有、模型没：", db_tables - model_tables)
