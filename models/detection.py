from extensions import db
from datetime import datetime

class Detection(db.Model):
    __tablename__ = 'detection'

    id          = db.Column(db.Integer, primary_key=True)
    date        = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    message_id  = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    # 🔴 删去原有的 type 字段
    # type        = db.Column(db.String(20), nullable=False)

    # 🟢 新增：prob（综合概率）和 label（综合标签）
    prob        = db.Column(db.Float, nullable=False, default=0.0)
    label       = db.Column(db.String(20), nullable=False, default="未知")

    terminal_id = db.Column(db.Integer, db.ForeignKey('terminal.id'), nullable=False)

    # 反向关系：Message / Terminal
    message     = db.relationship('Message', lazy=True)
    terminal    = db.relationship('Terminal', backref=db.backref('detections', lazy=True))

    def to_dict(self):
        """
        返回一本检测记录的完整字典，
        包含 id, date, message_id, prob, label, terminal_id
        """
        return {
            "id": self.id,
            "date": self.date.strftime('%Y-%m-%d %H:%M:%S'),
            "message_id": self.message_id,
            "prob": round(self.prob, 3),
            "label": self.label,
            "terminal_id": self.terminal_id
        }
