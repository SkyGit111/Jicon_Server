from extensions import db
from sqlalchemy import Text

class Message(db.Model):
    __tablename__ = 'message'

    id       = db.Column(db.Integer, primary_key=True)
    content  = db.Column(Text, nullable=False)      # 改为 Text 类型
    label    = db.Column(db.String(20))

    detections = db.relationship('Detection', lazy=True)
    results    = db.relationship('Result',    lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "label": self.label
        }
