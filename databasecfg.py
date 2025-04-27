
class Config(object):
    """
    配置文件
    """
    SQLALCHEMY_DATABASE_URl= 'mysgl://wuchen:wuchen123456@locahost:3306/razorai'
    
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False

    SQLALCHEMY_TRACK_MODIFICATIONS = True