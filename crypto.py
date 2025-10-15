"""
企业微信消息加解密模块
实现企业微信消息的签名验证、加密和解密功能
"""
import base64
import hashlib
import hmac
import random
import string
import struct
from typing import Tuple
from urllib.parse import unquote

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import xml.etree.ElementTree as ET


class WeChatWorkCrypto:
    """企业微信消息加解密类"""
    
    def __init__(self, token: str, encoding_aes_key: str, corp_id: str):
        """
        初始化加解密类
        
        Args:
            token: 企业微信配置的Token
            encoding_aes_key: 企业微信配置的EncodingAESKey
            corp_id: 企业微信的CorpID
        """
        self.token = token
        self.encoding_aes_key = encoding_aes_key
        self.corp_id = corp_id
        
        # 解码AES密钥
        # 添加缺失的填充字符
        if len(encoding_aes_key) == 43:
            aes_key_str = encoding_aes_key + "="
        else:
            aes_key_str = encoding_aes_key
            
        self.aes_key = base64.b64decode(aes_key_str)
        
        # 验证AES密钥长度
        if len(self.aes_key) != 32:
            raise ValueError(f"Invalid AES key length: {len(self.aes_key)}, expected 32")
    
    def _generate_signature(self, timestamp: str, nonce: str, encrypt_msg: str) -> str:
        """
        生成签名
        
        Args:
            timestamp: 时间戳
            nonce: 随机数
            encrypt_msg: 加密消息
            
        Returns:
            签名字符串
        """
        # 按字典序排序
        sorted_list = sorted([self.token, timestamp, nonce, encrypt_msg])
        # 拼接字符串
        signature_str = "".join(sorted_list)
        # SHA1加密
        return hashlib.sha1(signature_str.encode('utf-8')).hexdigest()
    
    def _verify_signature(self, signature: str, timestamp: str, nonce: str, encrypt_msg: str) -> bool:
        """
        验证签名
        
        Args:
            signature: 待验证的签名
            timestamp: 时间戳
            nonce: 随机数
            encrypt_msg: 加密消息
            
        Returns:
            验证结果
        """
        expected_signature = self._generate_signature(timestamp, nonce, encrypt_msg)
        return signature == expected_signature
    
    def _pkcs7_pad(self, data: bytes, block_size: int = 32) -> bytes:
        """
        PKCS#7填充
        
        Args:
            data: 待填充的数据
            block_size: 块大小
            
        Returns:
            填充后的数据
        """
        padding_length = block_size - (len(data) % block_size)
        padding = bytes([padding_length] * padding_length)
        return data + padding
    
    def _pkcs7_unpad(self, data: bytes) -> bytes:
        """
        PKCS#7去填充
        
        Args:
            data: 待去填充的数据
            
        Returns:
            去填充后的数据
        """
        padding_length = data[-1]
        return data[:-padding_length]
    
    def _aes_encrypt(self, data: bytes) -> bytes:
        """
        AES-256-CBC加密
        
        Args:
            data: 待加密的数据
            
        Returns:
            加密后的数据
        """
        # 使用AES密钥的前16字节作为IV
        iv = self.aes_key[:16]
        
        # PKCS#7填充
        padded_data = self._pkcs7_pad(data)
        
        # AES加密
        cipher = Cipher(algorithms.AES(self.aes_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        return encrypted_data
    
    def _aes_decrypt(self, encrypted_data: bytes) -> bytes:
        """
        AES-256-CBC解密
        
        Args:
            encrypted_data: 待解密的数据
            
        Returns:
            解密后的数据
        """
        # 使用AES密钥的前16字节作为IV
        iv = self.aes_key[:16]
        
        # AES解密
        cipher = Cipher(algorithms.AES(self.aes_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # PKCS#7去填充
        return self._pkcs7_unpad(decrypted_data)
    
    def verify_url(self, msg_signature: str, timestamp: str, nonce: str, echostr: str) -> str:
        """
        验证URL有效性
        
        Args:
            msg_signature: 消息签名
            timestamp: 时间戳
            nonce: 随机数
            echostr: 加密的字符串
            
        Returns:
            解密后的明文消息内容
            
        Raises:
            ValueError: 签名验证失败或解密失败
        """
        # 对echostr进行URL解码
        echostr_decoded = unquote(echostr)
        
        # 验证签名
        if not self._verify_signature(msg_signature, timestamp, nonce, echostr_decoded):
            raise ValueError("Signature verification failed")
        
        # Base64解码
        encrypted_data = base64.b64decode(echostr_decoded)
        
        # AES解密
        decrypted_data = self._aes_decrypt(encrypted_data)
        
        # 解析解密后的数据
        # 格式: random(16B) + msg_len(4B) + msg + receiveid
        random_bytes = decrypted_data[:16]
        msg_len = struct.unpack('>I', decrypted_data[16:20])[0]  # 网络字节序
        msg = decrypted_data[20:20+msg_len]
        receiveid = decrypted_data[20+msg_len:]
        
        # 验证receiveid
        if receiveid.decode('utf-8') != self.corp_id:
            raise ValueError(f"Invalid receiveid: {receiveid.decode('utf-8')}, expected: {self.corp_id}")
        
        return msg.decode('utf-8')
    
    def decrypt_msg(self, msg_signature: str, timestamp: str, nonce: str, post_data: str) -> str:
        """
        解密消息
        
        Args:
            msg_signature: 消息签名
            timestamp: 时间戳
            nonce: 随机数
            post_data: POST数据(XML格式)
            
        Returns:
            解密后的消息内容
            
        Raises:
            ValueError: 签名验证失败或解密失败
        """
        # 解析XML数据
        root = ET.fromstring(post_data)
        encrypt_element = root.find('Encrypt')
        if encrypt_element is None:
            raise ValueError("Missing Encrypt element in XML")
        
        encrypt_msg = encrypt_element.text
        if not encrypt_msg:
            raise ValueError("Empty Encrypt content")
        
        # 验证签名
        if not self._verify_signature(msg_signature, timestamp, nonce, encrypt_msg):
            raise ValueError("Signature verification failed")
        
        # Base64解码
        encrypted_data = base64.b64decode(encrypt_msg)
        
        # AES解密
        decrypted_data = self._aes_decrypt(encrypted_data)
        
        # 解析解密后的数据
        # 格式: random(16B) + msg_len(4B) + msg + receiveid
        random_bytes = decrypted_data[:16]
        msg_len = struct.unpack('>I', decrypted_data[16:20])[0]  # 网络字节序
        msg = decrypted_data[20:20+msg_len]
        receiveid = decrypted_data[20+msg_len:]
        
        # 验证receiveid
        if receiveid.decode('utf-8') != self.corp_id:
            raise ValueError(f"Invalid receiveid: {receiveid.decode('utf-8')}, expected: {self.corp_id}")
        
        return msg.decode('utf-8')
    
    def encrypt_msg(self, reply_msg: str, timestamp: str, nonce: str) -> str:
        """
        加密回复消息
        
        Args:
            reply_msg: 回复消息内容
            timestamp: 时间戳
            nonce: 随机数
            
        Returns:
            加密后的XML响应包
        """
        # 生成16字节随机字符串
        random_bytes = ''.join(random.choices(string.ascii_letters + string.digits, k=16)).encode('utf-8')
        
        # 构造明文数据
        msg_bytes = reply_msg.encode('utf-8')
        msg_len = struct.pack('>I', len(msg_bytes))  # 网络字节序
        receiveid_bytes = self.corp_id.encode('utf-8')
        
        plaintext = random_bytes + msg_len + msg_bytes + receiveid_bytes
        
        # AES加密
        encrypted_data = self._aes_encrypt(plaintext)
        
        # Base64编码
        encrypt_msg = base64.b64encode(encrypted_data).decode('utf-8')
        
        # 生成签名
        signature = self._generate_signature(timestamp, nonce, encrypt_msg)
        
        # 构造XML响应
        xml_response = f"""<xml>
<Encrypt><![CDATA[{encrypt_msg}]]></Encrypt>
<MsgSignature><![CDATA[{signature}]]></MsgSignature>
<TimeStamp>{timestamp}</TimeStamp>
<Nonce><![CDATA[{nonce}]]></Nonce>
</xml>"""
        
        return xml_response
