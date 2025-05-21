from extensions import db
from datetime import datetime

class Detection(db.Model):
    __tablename__ = 'detection'

    id          = db.Column(db.Integer, primary_key=True)
    date        = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    message_id  = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    type        = db.Column(db.String(20), nullable=False)
    terminal_id = db.Column(db.Integer, db.ForeignKey('terminal.id'), nullable=False)

    # 反向关系
    message    = db.relationship('Message', backref=db.backref('detections', lazy=True))
    terminal   = db.relationship('Terminal', backref=db.backref('detections', lazy=True))
    result     = db.relationship('Result', backref='detection', uselist=False)

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.strftime('%Y-%m-%d %H:%M:%S'),
            "message_id": self.message_id,
            "type": self.type,
            "terminal_id": self.terminal_id
        }
