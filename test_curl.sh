#!/bin/bash

# 企业微信接口测试脚本
# 使用文档中的示例数据进行测试

echo "=== 企业微信接口测试 ==="
echo

# 服务器地址
SERVER_URL="http://localhost:8000"

# 测试参数（来自企业微信官方文档示例）
MSG_SIGNATURE="477715d11cdb4164915debcba66cb864d751f3e6"
TIMESTAMP="1409659813"
NONCE="1372623149"
ECHOSTR="RypEvHKD8QQKFhvQ6QleEB4J58tiPdvo%2BrtK1I9qca6aM%2FwvqnLSV5zEPeusUiX5L5X%2F0lWfrf0QADHHhGd3QczcdCUpj911L3vg3W%2FsYYvuJTs3TUUkSUXxaccAS0qhxchrRYt66wiSpGLYL42aM6A8dTT%2B6k4aSknmPj48kzJs8qLjvd4Xgpue06DOdnLxAUHzM6%2BkDZ%2BHMZfJYuR%2BLtwGc2hgf5gsijff0ekUNXZiqATP7PF5mZxZ3Izoun1s4zG4LUMnvw2r%2BKqCKIw%2B3IQH03v%2BBCA9nMELNqbSf6tiWSrXJB3LAVGUcallcrw8V2t9EL4EhzJWrQUax5wLVMNS0%2BrUPA3k22Ncx4XXZS9o0MBH27Bo6BpNelZpS%2B%2Fuh9KsNlY6bHCmJU9p8g7m3fVKn28H3KDYA5Pl%2FT8Z1ptDAVe0lXdQ2YoyyH2uyPIGHBZZIs2pDBS8R07%2BqN%2BE7Q%3D%3D"

echo "1. 测试健康检查接口"
echo "GET $SERVER_URL/health"
curl -X GET "$SERVER_URL/health" -H "Content-Type: application/json"
echo
echo

echo "2. 测试URL验证接口"
echo "GET $SERVER_URL/?msg_signature=$MSG_SIGNATURE&timestamp=$TIMESTAMP&nonce=$NONCE&echostr=$ECHOSTR"
curl -X GET "$SERVER_URL/?msg_signature=$MSG_SIGNATURE&timestamp=$TIMESTAMP&nonce=$NONCE&echostr=$ECHOSTR" \
  -H "Content-Type: application/json" \
  -v
echo
echo

echo "3. 测试消息接收接口"
POST_XML='<xml>
<ToUserName><![CDATA[wx5823bf96d3bd56c7]]></ToUserName>
<Encrypt><![CDATA[RypEvHKD8QQKFhvQ6QleEB4J58tiPdvo+rtK1I9qca6aM/wvqnLSV5zEPeusUiX5L5X/0lWfrf0QADHHhGd3QczcdCUpj911L3vg3W/sYYvuJTs3TUUkSUXxaccAS0qhxchrRYt66wiSpGLYL42aM6A8dTT+6k4aSknmPj48kzJs8qLjvd4Xgpue06DOdnLxAUHzM6+kDZ+HMZfJYuR+LtwGc2hgf5gsijff0ekUNXZiqATP7PF5mZxZ3Izoun1s4zG4LUMnvw2r+KqCKIw+3IQH03v+BCA9nMELNqbSf6tiWSrXJB3LAVGUcallcrw8V2t9EL4EhzJWrQUax5wLVMNS0+rUPA3k22Ncx4XXZS9o0MBH27Bo6BpNelZpS+/uh9KsNlY6bHCmJU9p8g7m3fVKn28H3KDYA5Pl/T8Z1ptDAVe0lXdQ2YoyyH2uyPIGHBZZIs2pDBS8R07+qN+E7Q==]]></Encrypt>
<AgentID><![CDATA[218]]></AgentID>
</xml>'

echo "POST $SERVER_URL/?msg_signature=$MSG_SIGNATURE&timestamp=$TIMESTAMP&nonce=$NONCE"
curl -X POST "$SERVER_URL/?msg_signature=$MSG_SIGNATURE&timestamp=$TIMESTAMP&nonce=$NONCE" \
  -H "Content-Type: application/xml" \
  -d "$POST_XML" \
  -v
echo
echo

echo "=== 测试完成 ==="
