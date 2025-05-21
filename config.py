
class Config:
    # 数据库 URI（使用 mysql+pymysql）
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Qwer1234@localhost:3306/jicon_db'

    # 数据库行为设置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False

    # JWT 设置
    JWT_SECRET_KEY = 'oirjfOOIEFOaiehfiaiuhf91h3r10d'
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 单位：秒（24小时）

    # CORS 配置（可选）
    CORS_ORIGINS = "*"
