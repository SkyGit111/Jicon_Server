from extension import db

class DatabaseManager:
    @staticmethod
    def add_record(model_instance):
        """添加一条记录到数据库"""



        try:
            db.session.add(model_instance)
            db.session.commit()
            return model_instance
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def add_records(model_instances):
        """添加一个 model_instance 列表到数据库"""
        try:
            db.session.add_all(model_instances)  # 批量添加记录
            db.session.commit()
            return model_instances
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def delete_record(model_instance):
        """从数据库中删除一条记录"""


        try:
            db.session.delete(model_instance)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_record_by_id(model, record_id):
        """根据ID获取某条记录"""


        return model.query.get(record_id)

    @staticmethod
    def get_record(model, **kwargs):
        """获取某条记录"""
        return model.query.filter_by(**kwargs).first()

    @staticmethod
    def get_all_records(model):
        """获取所有记录"""

        return model.query.all()

    @staticmethod
    def update_record(model_instance):
        """更新记录"""

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e


    @staticmethod
    def query(model, **kwargs):
        """查询记录"""
        mdl = model.query.filter_by(**kwargs).first()
        return mdl


    @staticmethod
    def queryall(model, **kwargs):
        """查询符合要求的所有记录"""
        mdlist = model.query.filter_by(**kwargs).all()
        return mdlist


dbmanager = DatabaseManager()