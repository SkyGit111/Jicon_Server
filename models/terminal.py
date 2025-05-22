from extensions import db

class Terminal(db.Model):
    __tablename__ = 'terminal'

    id = db.Column(db.Integer, primary_key=True)
    signin_date = db.Column(db.DateTime, nullable=False)
    state = db.Column(db.Boolean, default=False)

    # 外键：关联 UserGroup，并自动给 UserGroup.terminals 创建反向访问
    group_id = db.Column(db.Integer, db.ForeignKey('user_group.id'), nullable=False)
    group    = db.relationship('UserGroup', backref=db.backref('terminals', lazy=True))


    def to_dict(self):
        return {
            "id": self.id,
            "signin_date": self.signin_date.strftime('%Y-%m-%d %H:%M:%S'),
            "state": self.state,
            "group_id": self.group_id,
            "group_name": self.group.name if self.group else None
        }
