#!/usr/bin/env python3
"""
测试运行脚本
使用测试配置启动服务，用于curl测试
"""
import os
import sys

# 设置测试环境变量
os.environ["WECHAT_WORK_TOKEN"] = "QDG6eK"
os.environ["WECHAT_WORK_ENCODING_AES_KEY"] = "jWmYm7qr5nMoAUwZRjGtBxmz3KA1tkAj3ykkR6q2B2C"
os.environ["WECHAT_WORK_CORP_ID"] = "wx5823bf96d3bd56c7"

print("=== 使用测试配置启动企业微信接口 ===")
print(f"Token: {os.environ['WECHAT_WORK_TOKEN']}")
print(f"EncodingAESKey: {os.environ['WECHAT_WORK_ENCODING_AES_KEY']}")
print(f"CorpID: {os.environ['WECHAT_WORK_CORP_ID']}")
print()

# 导入并运行主程序
if __name__ == "__main__":
    import uvicorn
    from main import app
    
    print("启动服务在 http://localhost:8000")
    print("可以使用 ./test_curl.sh 进行测试")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
