from extensions import db

class Admin(db.Model):
    __tablename__ = 'admin'

    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(20), nullable=False)
    email    = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    disabled = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "disabled": self.disabled
        }
