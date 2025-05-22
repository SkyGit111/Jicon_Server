import os
from dotenv import load_dotenv

# 自动加载项目根目录下的 .env 文件
load_dotenv()

class Config:
    # 从环境变量读取数据库 URI，若未设置则使用默认值
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:Qwer1234@localhost:3306/jicon_db"
    )

    # 数据库行为设置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False

    # JWT 设置
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "oirjfOOIEFOaiehfiaiuhf91h3r10d"
    )
    # 将字符串环境变量转为整数
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "86400"))

    # CORS 配置
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
