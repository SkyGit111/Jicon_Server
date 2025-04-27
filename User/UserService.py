from DatabaseManager.Dbmanager import dbmanager

from User.UserEntity import User
from werkzeug.security import generate_password_hash, check_password_hash


class UserService:



    @classmethod
    # 登陆查询
    def login(cls, user_id, user_password):
        user = dbmanager.query(User, user_id=user_id)
        return cls.verify_password(user_password, cls.getPassword(user))



    @classmethod
    def register(cls, user_name, user_password):
        new_user = User(user_name=user_name, user_password=user_password)
        return dbmanager.add_record(new_user)

    @classmethod
    def getId(cls, user: User):
        return user.getid()

    @classmethod
    def getPassword(cls, user: User):
        return user.getpassword()

    # 加密密码
    @classmethod
    def hash_password(cls, plain_password):
        return generate_password_hash(plain_password)

    # 验证密码
    @classmethod
    def verify_password(cls, plain_password, hashed_password):
        return check_password_hash(hashed_password, plain_password)

    @classmethod
    def getUsername(cls, user_id):
        user = dbmanager.query(User, user_id=user_id)
        return user.getname()

