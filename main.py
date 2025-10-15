"""
企业微信消息接收接口
实现企业微信的URL验证和消息接收功能
"""
import os
import time
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse
import xml.etree.ElementTree as ET

from config import config
from crypto import WeChatWorkCrypto


app = FastAPI(title="企业微信消息接收接口", version="1.0.0")

# 初始化加解密实例
crypto = WeChatWorkCrypto(
    token=config.token,
    encoding_aes_key=config.encoding_aes_key,
    corp_id=config.corp_id
)


@app.get("/")
async def verify_url(
    msg_signature: str = Query(..., description="企业微信加密签名"),
    timestamp: str = Query(..., description="时间戳"),
    nonce: str = Query(..., description="随机数"),
    echostr: str = Query(..., description="加密的字符串")
):
    """
    验证URL有效性
    企业微信会发送GET请求到这个接口进行URL验证
    """
    try:
        # 验证URL并解密echostr
        decrypted_msg = crypto.verify_url(msg_signature, timestamp, nonce, echostr)
        
        # 原样返回明文消息内容（不能加引号，不能带bom头，不能带换行符）
        return PlainTextResponse(content=decrypted_msg)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"URL verification failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/")
async def receive_message(request: Request):
    """
    接收企业微信推送的消息
    企业微信会发送POST请求到这个接口推送消息
    """
    try:
        # 获取查询参数
        msg_signature = request.query_params.get("msg_signature")
        timestamp = request.query_params.get("timestamp")
        nonce = request.query_params.get("nonce")
        
        if not all([msg_signature, timestamp, nonce]):
            raise HTTPException(status_code=400, detail="Missing required query parameters")
        
        # 获取POST数据
        post_data = await request.body()
        post_data_str = post_data.decode('utf-8')
        
        # 解密消息
        decrypted_msg = crypto.decrypt_msg(msg_signature, timestamp, nonce, post_data_str)
        
        # 解析解密后的XML消息
        msg_root = ET.fromstring(decrypted_msg)
        
        # 提取消息字段
        to_user_name = msg_root.find('ToUserName')
        from_user_name = msg_root.find('FromUserName')
        create_time = msg_root.find('CreateTime')
        msg_type = msg_root.find('MsgType')
        content = msg_root.find('Content')
        msg_id = msg_root.find('MsgId')
        agent_id = msg_root.find('AgentID')
        
        # 构建消息对象
        message_data = {
            "ToUserName": to_user_name.text if to_user_name is not None else "",
            "FromUserName": from_user_name.text if from_user_name is not None else "",
            "CreateTime": create_time.text if create_time is not None else "",
            "MsgType": msg_type.text if msg_type is not None else "",
            "Content": content.text if content is not None else "",
            "MsgId": msg_id.text if msg_id is not None else "",
            "AgentID": agent_id.text if agent_id is not None else "",
            "raw_xml": decrypted_msg
        }
        
        # 处理不同类型的消息
        await handle_message(message_data)
        
        # 如果需要被动回复消息，可以构造回复
        reply_msg = await generate_reply(message_data)
        
        if reply_msg:
            # 生成时间戳和随机数
            current_timestamp = str(int(time.time()))
            reply_nonce = ''.join([str(i) for i in range(10)])
            
            # 加密回复消息
            encrypted_reply = crypto.encrypt_msg(reply_msg, current_timestamp, reply_nonce)
            
            return PlainTextResponse(content=encrypted_reply, media_type="application/xml")
        else:
            # 返回200状态码表示接收成功，但不回复内容
            return PlainTextResponse(content="")
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Message processing failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def handle_message(message_data: dict):
    """
    处理接收到的消息
    
    Args:
        message_data: 解析后的消息数据
    """
    msg_type = message_data.get("MsgType", "")
    content = message_data.get("Content", "")
    from_user = message_data.get("FromUserName", "")
    
    print(f"收到消息类型: {msg_type}")
    print(f"发送者: {from_user}")
    print(f"消息内容: {content}")
    print(f"完整消息: {message_data['raw_xml']}")
    
    # 根据消息类型进行不同处理
    if msg_type == "text":
        print(f"处理文本消息: {content}")
    elif msg_type == "image":
        print("处理图片消息")
    elif msg_type == "voice":
        print("处理语音消息")
    elif msg_type == "video":
        print("处理视频消息")
    elif msg_type == "event":
        print("处理事件消息")
    else:
        print(f"未知消息类型: {msg_type}")


async def generate_reply(message_data: dict) -> Optional[str]:
    """
    生成回复消息
    
    Args:
        message_data: 解析后的消息数据
        
    Returns:
        回复消息内容，如果不需要回复则返回None
    """
    msg_type = message_data.get("MsgType", "")
    content = message_data.get("Content", "")
    from_user = message_data.get("FromUserName", "")
    to_user = message_data.get("ToUserName", "")
    
    # 简单的自动回复逻辑
    if msg_type == "text":
        if "你好" in content or "hello" in content.lower():
            return f"""<xml>
<ToUserName><![CDATA[{from_user}]]></ToUserName>
<FromUserName><![CDATA[{to_user}]]></FromUserName>
<CreateTime>{int(time.time())}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[你好！我是企业微信机器人，很高兴为您服务！]]></Content>
</xml>"""
        elif "帮助" in content or "help" in content.lower():
            return f"""<xml>
<ToUserName><![CDATA[{from_user}]]></ToUserName>
<FromUserName><![CDATA[{to_user}]]></FromUserName>
<CreateTime>{int(time.time())}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[我是企业微信机器人，可以为您提供以下服务：
1. 回复"你好"获取问候
2. 回复"帮助"获取帮助信息
3. 其他功能正在开发中...]]></Content>
</xml>"""
    
    # 默认不回复
    return None


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "timestamp": int(time.time())}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
