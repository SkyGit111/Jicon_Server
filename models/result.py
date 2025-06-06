# models/result.py
from extensions import db

class Result(db.Model):
    __tablename__ = 'result'

    id           = db.Column(db.Integer, primary_key=True)
    message_id   = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=True)
    label        = db.Column(db.String(20), nullable=False)
    # detection_id 字段已被你删除，这里就不再出现
    # detection_id = db.Column(db.Integer, db.ForeignKey('detection.id'), nullable=False)

    # 新增：标记该用户反馈是否已同步到 CSV
    written      = db.Column(db.Boolean, default=False, nullable=False)

    # 关联 Message（单向）
    message   = db.relationship('Message', lazy=True)
    # 如果你之前保留了 detection 字段，可删掉或注释
    # detection = db.relationship('Detection', backref=db.backref('results', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "message_id": self.message_id,
            "label": self.label,
            "written": self.written
        }
