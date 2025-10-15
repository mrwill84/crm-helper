"""
企业微信配置管理
"""
import os
from typing import Optional


class WeChatWorkConfig:
    """企业微信配置类"""
    
    def __init__(self):
        # 从环境变量获取配置，如果没有则使用默认值
        self.token: str = os.getenv("WECHAT_WORK_TOKEN", "")
        self.encoding_aes_key: str = os.getenv("WECHAT_WORK_ENCODING_AES_KEY", "")
        self.corp_id: str = os.getenv("WECHAT_WORK_CORP_ID", "")
        
        # 验证必要的配置是否存在
        if not self.token:
            raise ValueError("WECHAT_WORK_TOKEN 环境变量未设置")
        if not self.encoding_aes_key:
            raise ValueError("WECHAT_WORK_ENCODING_AES_KEY 环境变量未设置")
        if not self.corp_id:
            raise ValueError("WECHAT_WORK_CORP_ID 环境变量未设置")


# 全局配置实例
config = WeChatWorkConfig()
