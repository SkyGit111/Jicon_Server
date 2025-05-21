from extensions import db
from datetime import datetime

class ModelVersion(db.Model):
    __tablename__ = 'model_version'

    id           = db.Column(db.Integer, primary_key=True)
    finish_date  = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    description  = db.Column(db.String(255))
    is_active    = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "finish_date": self.finish_date.strftime('%Y-%m-%d %H:%M:%S'),
            "description": self.description,
            "is_active": self.is_active
        }
