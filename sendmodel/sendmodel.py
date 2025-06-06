import requests
import os
import argparse

SEVER_URL = 'http://localhost:6006/update_model'
FILE_PATH = 'model.ckpt'  # 默认模型文件路径

def send_model():
    """
    发送模型文件到服务器

    参数:
        file_path (str): 本地模型文件路径
        server_url (str): 服务器更新模型的URL
    """
    # 验证文件是否存在
    if not os.path.exists(FILE_PATH):
        print(f"错误: 文件 '{FILE_PATH}' 不存在")
        return

    # 验证文件扩展名
    if not FILE_PATH.lower().endswith('.ckpt'):
        print("错误: 仅支持 .ckpt 格式文件")
        return

    try:
        # 准备文件数据
        files = {'file': (os.path.basename(FILE_PATH), open(FILE_PATH, 'rb'))}
        print(f"正在发送文件: {FILE_PATH} 到服务器: {SEVER_URL}")
        # 发送POST请求
        response = requests.post(SEVER_URL, files=files)

        # 处理响应
        if response.status_code == 200:
            result = response.json()
            print(f"成功: {result['message']}")
            print(f"响应代码: {result['code']}")
        else:
            try:
                error_data = response.json()
                print(f"错误: {error_data.get('message', '未知错误')}")
                print(f"响应代码: {error_data.get('code', response.status_code)}")
            except:
                print(f"请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text[:200]}...")

    except Exception as e:
        print(f"发送文件时出错: {str(e)}")
    finally:
        # 确保文件被关闭
        if 'files' in locals():
            files['file'][1].close()


