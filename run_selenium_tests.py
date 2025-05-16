#!/usr/bin/env python3
"""
Selenium Test Runner for SentiSocial

This script runs the Selenium tests for the SentiSocial application.
It ensures the Flask application is running before executing the tests.

Usage:
    python run_selenium_tests.py
"""

import os
import sys
import time
import subprocess
import signal
import pytest
import tempfile
import shutil

def main():
    """Main function to run the tests"""
    print("启动真实的 Flask 应用进行测试...")
    
    # 设置测试环境变量
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TESTING'] = 'True'
    os.environ['FLASK_DEBUG'] = '1'
    
    # 创建临时目录作为实例文件夹
    temp_instance_dir = tempfile.mkdtemp()
    temp_upload_dir = os.path.join(temp_instance_dir, 'uploads')
    os.makedirs(temp_upload_dir, exist_ok=True)
    
    # 设置测试数据库路径
    test_db_path = os.path.join(temp_instance_dir, 'test_database.db')
    
    # 设置测试密钥
    os.environ['SQLITE_SECRET'] = 'test_secret_key'
    
    # 获取当前目录的绝对路径
    current_dir = os.path.abspath(os.path.dirname(__file__))
    
    # 创建一个测试脚本来启动 Flask 应用，使用 mock 包
    test_script = f"""
import sys
import os
from unittest.mock import patch, MagicMock

# 添加当前目录到 Python 路径
sys.path.insert(0, '{current_dir}')

# 创建 mock 对象
class MockTwitterCrawler:
    @staticmethod
    def fetch_twitter_comments(query, limit=100):
        return [
            {{"date": "2023-01-01", "content": "This is a great product!", "username": "user1", "sentiment": "positive"}},
            {{"date": "2023-01-02", "content": "I love this service.", "username": "user2", "sentiment": "positive"}},
            {{"date": "2023-01-03", "content": "Not very satisfied with the quality.", "username": "user3", "sentiment": "negative"}},
        ]

class MockCrawler:
    twitter_crawler = MockTwitterCrawler()
    
    @staticmethod
    def fetch_twitter_comments(*args, **kwargs):
        return MockTwitterCrawler.fetch_twitter_comments(*args, **kwargs)

class MockBertModel:
    @staticmethod
    def predict(texts):
        results = []
        for text in texts:
            if "great" in text.lower() or "love" in text.lower():
                results.append("positive")
            elif "not" in text.lower() or "bad" in text.lower():
                results.append("negative")
            else:
                results.append("neutral")
        return results

# 使用 mock 替换真实的包
packages_crawler_mock = MagicMock()
packages_crawler_mock.twitter_crawler = MockTwitterCrawler()
packages_crawler_mock.fetch_twitter_comments = MockCrawler.fetch_twitter_comments

bert_model_mock = MagicMock()
bert_model_mock.predict = MockBertModel.predict

sys.modules['packages'] = MagicMock()
sys.modules['packages.crawler'] = packages_crawler_mock
sys.modules['bert_model'] = bert_model_mock

# 导入应用
from app import create_app
app = create_app()
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.run(host='localhost', port=5001, debug=True)
"""

    # 将测试脚本写入临时文件
    test_script_path = os.path.join(temp_instance_dir, 'test_script.py')
    with open(test_script_path, 'w') as f:
        f.write(test_script)

    # 启动 Flask 应用
    print("启动 Flask 应用...")
    flask_process = subprocess.Popen(
        [sys.executable, test_script_path],
        env={**os.environ, 'FLASK_APP': 'app', 'FLASK_ENV': 'testing', 'FLASK_DEBUG': '1'},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # 等待 Flask 应用启动
    print("等待 Flask 应用启动...")
    time.sleep(2)
    
    # 检查 Flask 应用是否成功启动
    if flask_process.poll() is not None:
        # 如果进程已经结束，打印错误信息
        stdout, stderr = flask_process.communicate()
        print("Flask 应用启动失败:")
        print("标准输出:", stdout)
        print("错误输出:", stderr)
        return 1
    
    # 等待 Flask 应用完全启动
    time.sleep(6)
    
    # 检查 Flask 应用是否正在运行
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 5001))
        if result == 0:
            print("Flask 应用成功启动在端口 5001")
        else:
            print("警告: Flask 应用可能未在端口 5001 上运行")
        sock.close()
    except:
        print("无法检查 Flask 应用状态")
    
    try:
        # Run the Selenium tests
        print("运行 Selenium 测试...")
        pytest_args = [
            '-xvs',  # -x: exit on first failure, -v: verbose, -s: show output
            'tests/test_selenium.py'  # Run the selenium tests
        ]
        
        # Add any command line arguments
        pytest_args.extend(sys.argv[1:])
        
        # Run pytest
        exit_code = pytest.main(pytest_args)
        
        # Return the exit code from pytest
        return exit_code
    
    finally:
        # Terminate the Flask process
        print("Stopping Flask application...")
        flask_process.terminate()
        
        # Wait for the process to terminate
        try:
            flask_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("Flask process did not terminate gracefully, forcing termination...")
            flask_process.kill()
            flask_process.wait()

if __name__ == "__main__":
    sys.exit(main())
