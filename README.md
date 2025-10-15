# 企业微信消息接收接口

这是一个基于FastAPI的企业微信消息接收接口，实现了企业微信的URL验证和消息接收功能。

## 功能特性

- ✅ URL验证：支持企业微信的URL有效性验证
- ✅ 消息解密：支持企业微信消息的AES解密
- ✅ 消息加密：支持被动回复消息的AES加密
- ✅ 签名验证：支持企业微信消息签名验证
- ✅ 自动回复：支持简单的自动回复功能
- ✅ 健康检查：提供服务健康状态检查

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `env.example` 文件为 `.env` 并填入你的企业微信配置：

```bash
cp env.example .env
```

编辑 `.env` 文件，填入你的企业微信配置信息：

```env
WECHAT_WORK_TOKEN=your_token_here
WECHAT_WORK_ENCODING_AES_KEY=your_encoding_aes_key_here
WECHAT_WORK_CORP_ID=your_corp_id_here
```

### 3. 运行服务

```bash
python main.py
```

或者使用uvicorn直接运行：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

服务将在 `http://localhost:8000` 启动。

## API接口

### 1. URL验证接口 (GET /)

企业微信会发送GET请求到这个接口进行URL验证。

**请求参数：**
- `msg_signature`: 企业微信加密签名
- `timestamp`: 时间戳
- `nonce`: 随机数
- `echostr`: 加密的字符串

**响应：**
- 成功：返回解密后的明文消息内容
- 失败：返回400错误

### 2. 消息接收接口 (POST /)

企业微信会发送POST请求到这个接口推送消息。

**请求参数：**
- `msg_signature`: 企业微信加密签名
- `timestamp`: 时间戳
- `nonce`: 随机数

**请求体：**
XML格式的加密消息

**响应：**
- 成功：返回加密的回复消息或空字符串
- 失败：返回400/500错误

### 3. 健康检查接口 (GET /health)

检查服务运行状态。

**响应：**
```json
{
    "status": "healthy",
    "timestamp": 1234567890
}
```

## 配置说明

### 获取企业微信配置信息

1. 登录企业微信管理后台
2. 进入需要设置接收消息的应用
3. 点击"接收消息"的"设置API接收"按钮
4. 获取以下配置信息：
   - **URL**: 填写你的服务器地址，如 `http://your-domain.com/`
   - **Token**: 可由企业任意填写，用于生成签名
   - **EncodingAESKey**: 用于消息体的加密，是AES密钥的Base64编码

### 环境变量说明

- `WECHAT_WORK_TOKEN`: 企业微信配置的Token
- `WECHAT_WORK_ENCODING_AES_KEY`: 企业微信配置的EncodingAESKey
- `WECHAT_WORK_CORP_ID`: 企业微信的CorpID

## 消息处理

当前实现了基本的消息处理逻辑：

1. **文本消息**: 支持简单的关键词回复
   - 发送"你好"或"hello"会收到问候回复
   - 发送"帮助"或"help"会收到帮助信息

2. **其他消息类型**: 目前只记录日志，可以根据需要扩展

## 扩展开发

### 添加新的消息处理逻辑

在 `main.py` 中的 `handle_message` 函数中添加你的业务逻辑：

```python
async def handle_message(message_data: dict):
    msg_type = message_data.get("MsgType", "")
    content = message_data.get("Content", "")
    from_user = message_data.get("FromUserName", "")
    
    if msg_type == "text":
        # 处理文本消息
        if "你的关键词" in content:
            # 执行你的业务逻辑
            pass
```

### 添加新的自动回复

在 `generate_reply` 函数中添加你的回复逻辑：

```python
async def generate_reply(message_data: dict) -> Optional[str]:
    msg_type = message_data.get("MsgType", "")
    content = message_data.get("Content", "")
    
    if msg_type == "text":
        if "特定关键词" in content:
            return f"""<xml>
<ToUserName><![CDATA[{from_user}]]></ToUserName>
<FromUserName><![CDATA[{to_user}]]></FromUserName>
<CreateTime>{int(time.time())}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[你的回复内容]]></Content>
</xml>"""
```

## 注意事项

1. **安全性**: 确保你的服务器支持HTTPS，企业微信推荐使用HTTPS
2. **超时处理**: 企业微信服务器在5秒内收不到响应会重试，请确保处理逻辑在5秒内完成
3. **消息排重**: 建议使用msgid进行消息排重，避免重复处理
4. **错误处理**: 代码遵循fail-fast原则，遇到错误会立即抛出异常

## 故障排除

1. **URL验证失败**: 检查Token、EncodingAESKey、CorpID是否正确
2. **消息解密失败**: 确认EncodingAESKey格式正确（43个字符的Base64编码）
3. **签名验证失败**: 检查Token是否与企业微信后台配置一致

## 许可证

MIT License
