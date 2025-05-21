from extensions import db
from datetime import datetime

class KnowledgeVersion(db.Model):
    __tablename__ = 'knowledge_version'

    id          = db.Column(db.Integer, primary_key=True)
    version     = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "version": self.version,
            "description": self.description,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
