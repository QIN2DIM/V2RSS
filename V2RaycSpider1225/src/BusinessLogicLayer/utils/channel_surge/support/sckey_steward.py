__all__ = ['api']

import base64
import hashlib
import os

from Crypto.Cipher import AES


class _SecretSteward(object):
    """
    > 接收用户输入
        - 校验数据 if 正确 -> 缓存数据 data:服务器敏感数据
        - else -> 丢弃
    > 接收用户确认信息
        - 是否存储 data if YES -> 启动密钥管理模块
        - else -> 丢弃缓存
    > 密钥管理模块
        - 接收用户输入 pem-password -> md5(md5($salt,$password)) ->sckey of AES ECB
        - 输入校验模块
    > 输入校验模块
        - if run in win -> use easygui
        - else -> Terminal/shell
    """

    def __init__(self, sckey: str):

        self.base_pem = '_sckeyStream.v2raycs'

        if sckey.__len__() > 32:
            sckey = sckey[:32]
        self.sckey = self._complete_stream(sckey=sckey)

    @staticmethod
    def _complete_stream(sckey: str):
        sckey = bytes(sckey, encoding='utf-8')
        while sckey.__len__() % 16 != 0:
            sckey += b'\0'
        return sckey

    def encrypt(self, message: str):
        return str(
            base64.encodebytes(AES.new(key=self.sckey, mode=AES.MODE_ECB).encrypt(self._complete_stream(message))),
            encoding='utf-8'.replace('\n', ''))

    def decrypt(self, cipher_text: str):
        return str(AES.new(key=self.sckey, mode=AES.MODE_ECB).decrypt(
            base64.decodebytes(bytes(cipher_text, encoding='utf-8'))).rstrip(
            b'\0').decode('utf-8'))

    def capture_stream(self, stream, path: str = None, ):
        if not stream:
            stream = self.base_pem
        with open(path, 'w') as f:
            f.write(stream)


class _Interface(object):

    def __init__(self, password: str, cache_path: str = None):
        _sckey: str = self._change_format_of_sckey(weak_password=password)
        self.ss = _SecretSteward(sckey=_sckey)

        if cache_path is None or cache_path == '':
            self.cache_path = self.ss.base_pem

    @staticmethod
    def _change_format_of_sckey(weak_password: str) -> str:
        if not isinstance(weak_password, bytes):
            weak_password = bytes(weak_password, 'utf-8')
        m = hashlib.md5()
        m.update(weak_password)
        m.update(m.digest())
        m.update(bytes(str(base64.encodebytes(m.digest()), encoding='utf-8').replace('\n', ''), 'utf-8'))
        return m.hexdigest()

    def encrypt(self, message: str = None):

        if message is None or message == '':
            print(">>> Message is None. Please pass in the plaintext that needs to be encrypted.")
            return None
        cipher_text: str = self.ss.encrypt(message=message)
        self.ss.capture_stream(stream=cipher_text, path=self.cache_path)
        print(f">>> Data encryption succeeded! SCKEY file storage path:{self.cache_path}")

    def decrypt(self, message: str = None):

        if message:
            return self.ss.decrypt(cipher_text=message)
        else:
            if not os.path.exists(self.cache_path):
                print(">>> Message is None. Please pass in the data to be decrypted.")
                print(f">>> The path of the file to be decrypted cannot be found({self.cache_path}).")
                return None
            with open(self.cache_path, 'r', encoding='utf-8') as f:
                message = f.read()
            try:
                result = self.ss.decrypt(message)
                print(">>> Decrypt success!")
                return result
            except UnicodeDecodeError:
                print(">>> Password Error！Please try again.")


api = _Interface
