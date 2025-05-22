#!/usr/bin/env python3
# test_db.py

import os
import re
import pymysql
from dotenv import load_dotenv

def main():
    # 1. 加载 .env（如果有）
    load_dotenv()

    # 2. 从环境变量读取 DATABASE_URL
    url = os.getenv("DATABASE_URL")
    if not url:
        print("❌ 错误：未设置 DATABASE_URL 环境变量")
        return

    # 3. 解析 mysql+pymysql://user:pass@host:port/dbname
    m = re.match(
        r"mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)",
        url
    )
    if not m:
        print(f"❌ 错误：DATABASE_URL 格式不正确 → {url}")
        return
    user, pwd, host, port, dbname = m.groups()
    port = int(port)

    print(f"▶ 尝试连接 MySQL → host={host}, port={port}, user={user}, db={dbname}")
    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=pwd,
            database=dbname,
            connect_timeout=5
        )
        print("✅ 连接成功")
        conn.close()
    except Exception as e:
        print("❌ 连接失败:", e)

if __name__ == "__main__":
    main()
