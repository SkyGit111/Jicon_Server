from extension import db


class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)  # 用户ID账号，主键
    user_password = db.Column(db.String(255), nullable=False)  # 密码
    user_name = db.Column(db.String(20), nullable=False)  # 用户名
    user_gender = db.Column(db.Integer)


    def getid(self):
        return self.user_id

    def getpassword(self):
        return self.user_password

    def getname(self):
        return self.user_name

    def getgender(self):
        return self.user_gender
