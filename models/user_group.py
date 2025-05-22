from extensions import db

class UserGroup(db.Model):
    __tablename__ = 'user_group'

    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(20), nullable=False)
    members = db.Column(db.Text)



    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "members": self.members,
            "terminal_ids": [t.id for t in self.terminals]
        }
