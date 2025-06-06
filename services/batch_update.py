# services/batch_update.py
import os
import csv
from datetime import datetime

from flask import current_app
from extensions import db
from models.result import Result
from models.message import Message
from db_create import create_vdb

# CSV 文件路径（确保与 result_routes 中一致）
CSV_PATH = os.path.join(os.getcwd(), "fraud_data.csv")

def check_and_update_csv_and_vdb(app):
    """
    定时调度的任务入口。
    1) 查询所有 written == False 的 Result
    2) 如果数量 < 阈值 (配置里)，直接返回
    3) 否则先把所有这些 Result 对应的 (message.content, label) 批量追加到 CSV
    4) 标记这些 Result.written = True，提交事务
    5) 调用 create_vdb() 重建向量库
    """
    with app.app_context():
        # 从配置文件或环境变量读取阈值，默认 10 条
        threshold = app.config.get("UPDATE_THRESHOLD", 10)

        # 1) 查出所有 written=False 的反馈条
        pending_results = Result.query.filter_by(written=False).all()
        count = len(pending_results)
        current_app.logger.info(f"[BatchUpdate] {datetime.utcnow()}: Found {count} pending results")

        # 2) 如果未达阈值，什么都不做
        if count < threshold:
            return

        # 3) 批量追加 CSV
        #    如果 CSV 不存在，就先写表头
        file_existed = os.path.exists(CSV_PATH)
        with open(CSV_PATH, "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            if not file_existed:
                writer.writerow(["text", "label"])
            # 对每条 feedback，查 Message.content，再写
            for res in pending_results:
                msg = Message.query.get(res.message_id)
                content = msg.content if msg else ""
                writer.writerow([content, res.label])
                current_app.logger.info(f"[BatchUpdate] Appended: ({content}, {res.label})")

        # 4) 标记为已写入
        for res in pending_results:
            res.written = True

        # 提交事务（⼀次性标记所有 pending_results 为 written=True）
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"[BatchUpdate] DB commit failed: {e}")
            return

        # 5) 重建向量库
        try:
            create_vdb()
            current_app.logger.info("[BatchUpdate] Vector DB rebuilt successfully")
        except Exception as e:
            current_app.logger.error(f"[BatchUpdate] create_vdb() failed: {e}")
            # 如果重建失败，本地 CSV 已经被改写，但结果已标记为 written=True
            # 根据业务需要，你可以选择把 written 重置为 False，让下一次调度再试。
            # 举例：res.written = False 并 db.session.commit()
            # 但一般来说只记录日志即可。

        current_app.logger.info(f"[BatchUpdate] Completed batch update for {count} results")
