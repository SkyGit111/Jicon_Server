from extensions import db

class Result(db.Model):
    __tablename__ = 'result'

    id           = db.Column(db.Integer, primary_key=True)
    message_id   = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=True)
    label        = db.Column(db.String(20), nullable=False)
    detection_id = db.Column(db.Integer, db.ForeignKey('detection.id'), nullable=False)

    # 单向关联 Message（Message.results 由上面修改后的关系管理）
    message   = db.relationship('Message',   lazy=True)
    # 与 Detection 维持反向
    detection = db.relationship('Detection', backref=db.backref('results', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "message_id": self.message_id,
            "label": self.label,
            "detection_id": self.detection_id
        }
