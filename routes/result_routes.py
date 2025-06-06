# routes/result_routes.py

import os
import csv
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

from extensions import db
from models.result import Result
from models.message import Message
from schemas.result_schema import ResultSchema

# 如果你使用了批量更新功能（APScheduler 任务）：
# from services.batch_update import check_and_update_csv_and_vdb

# 如果你希望每次立即重建向量库，可引入下面这个函数：
from db_create import create_vdb

# CSV 文件路径（相对于项目根目录）
CSV_PATH = os.path.join(os.getcwd(), "fraud_data.csv")

res_bp = Blueprint("res_bp", __name__)
res_sch = ResultSchema()
ress_sch = ResultSchema(many=True)


def _append_to_csv_and_rebuild(message_content: str, label: str):
    """
    将一条 (message_content, label) 追加到 fraud_data.csv，
    然后调用 create_vdb() 完全重建向量库。
    """
    file_existed = os.path.exists(CSV_PATH)
    with open(CSV_PATH, mode="a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if not file_existed:
            # 如果文件是新创建，先写表头
            writer.writerow(["text", "label"])
        writer.writerow([message_content, label])
    current_app.logger.info(f"已将新行写入 CSV: ({message_content}, {label})")

    # 调用 create_vdb() 重建向量库
    try:
        # create_vdb()
        current_app.logger.info("向量库重建成功")
    except Exception as e:
        current_app.logger.error(f"向量库重建失败: {e}")
        raise


def _sync_message_label(result_obj: Result):
    """
    如果 Result.message_id 以及 Result.label 有值，则把对应的 Message.label 覆盖掉。
    """
    if result_obj.message_id and result_obj.label:
        msg = Message.query.get(result_obj.message_id)
        if msg:
            msg.label = result_obj.label


# ------------------------ CREATE ------------------------
@res_bp.route("/", methods=["POST"])
def create_result():
    """
    创建一条新的用户反馈 (Result)，并同步更新对应 Message.label 。
    如果 written=False，则把记录的 (message.content, label) 写入 CSV，重建向量库，
    并将 Result.written 标为 True。
    """
    try:
        raw = request.get_json() or {}
        # 1) 校验并反序列化为 dict
        data = res_sch.load(raw)
        # data 比如：{ "message_id": 19, "label": "诈骗" }

        # 2) 手动构造 Result 模型实例
        res_obj = Result(
            message_id=data["message_id"],
            label=data["label"],
            written=False
        )
        db.session.add(res_obj)

        # 3) 同步更新 Message.label
        _sync_message_label(res_obj)

        # 4) Flush，让 res_obj.id & res_obj.written (=False) 可见
        db.session.flush()

        # 5) 如果尚未写入 CSV，则追加并重建向量库
        if not res_obj.written:
            msg = Message.query.get(res_obj.message_id)
            content = msg.content if msg else ""
            _append_to_csv_and_rebuild(content, res_obj.label)
            # res_obj.written = True

        # 6) 提交事务
        db.session.commit()
        return res_sch.jsonify(res_obj), 201

    except ValidationError as e:
        db.session.rollback()
        return jsonify({"error": e.messages}), 400

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"CSV 更新或向量库重建失败: {e}"}), 500


# ------------------------ LIST ------------------------
@res_bp.route("/", methods=["GET"])
@jwt_required()
def list_results():
    """
    列出所有 Result 记录，按 id 倒序排列。
    """
    ress = Result.query.order_by(Result.id.desc()).all()
    return ress_sch.jsonify(ress), 200


# ------------------------ UPDATE ------------------------
@res_bp.route("/<int:res_id>", methods=["PUT"])
@jwt_required()
def update_result(res_id):
    """
    更新某条已存在的反馈（如修改 label）。
    如果之前 written=False，或用户修改了 label，都会再追加一行到 CSV 并重建向量库。
    """
    # 先在数据库中找到该 res_id 对应的 Result 实例
    res_obj = Result.query.get_or_404(res_id)
    old_written = res_obj.written

    try:
        raw = request.get_json() or {}
        # 1) 校验客户端传入字段（只会有 message_id、label）
        data = res_sch.load(raw, partial=True)
        # data 可能包含 label 更改，也可能包含 message_id 更改

        # 2) 手动把能修改的字段应用到模型实例上
        if "message_id" in data:
            res_obj.message_id = data["message_id"]
        if "label" in data:
            res_obj.label = data["label"]

        # 3) 同步更新 Message.label
        _sync_message_label(res_obj)

        # 4) Flush，让修改在本事务中可见
        db.session.flush()

        # 5) 如果之前未写（old_written=False）或 label 被修改，则追加 CSV 并重建向量库
        if (not old_written) or ("label" in data):
            msg = Message.query.get(res_obj.message_id)
            content = msg.content if msg else ""
            _append_to_csv_and_rebuild(content, res_obj.label)
            res_obj.written = True

        # 6) 提交事务
        db.session.commit()
        return res_sch.jsonify(res_obj), 200

    except ValidationError as e:
        db.session.rollback()
        return jsonify({"error": e.messages}), 400

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"CSV 更新或向量库重建失败: {e}"}), 500


# ------------------------ DELETE ------------------------
@res_bp.route("/<int:res_id>", methods=["DELETE"])
@jwt_required()
def delete_result(res_id):
    """
    删除某条反馈。删除后不修改 CSV 和向量库（如需同步做到 CSV 里删行，可自行扩展）。
    """
    res_obj = Result.query.get_or_404(res_id)
    try:
        db.session.delete(res_obj)
        db.session.commit()
        return "", 204
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
