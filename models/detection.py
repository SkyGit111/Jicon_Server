from extensions import db
from datetime import datetime

class Detection(db.Model):
    __tablename__ = 'detection'

    id          = db.Column(db.Integer, primary_key=True)
    date        = db.Column(db.DateTime, nullable=False)
    message_id  = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    type        = db.Column(db.String(20), nullable=False)
    terminal_id = db.Column(db.Integer, db.ForeignKey('terminal.id'), nullable=False)

    # 反向关系
     # 只保留普通关系，不自动创建 backref
    message     = db.relationship('Message', lazy=True)
    terminal   = db.relationship('Terminal', backref=db.backref('detections', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.strftime('%Y-%m-%d %H:%M:%S'),
            "message_id": self.message_id,
            "type": self.type,
            "terminal_id": self.terminal_id
        }
