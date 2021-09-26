import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto import Random
from Crypto.Util.Padding import pad, unpad

class AESProvider(object):

    def __init__(self, key):
        self.key = key
        self.bs = AES.block_size

    def _unpad(self, s):
        return s[:-ord(s[len(s) - 1:])]

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)


    def encrypt(self, raw):
        raw = pad(raw.encode("utf-8"), AES.block_size, style='pkcs7')
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(raw)
        encryptedb64 = base64.b64encode(iv + encrypted)
        return encryptedb64

    def decrypt(self, message):
        IV = base64.b64decode(message)[0:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, IV)
        data = cipher.decrypt(base64.b64decode(message)[AES.block_size:])
        return unpad(data, AES.block_size, style='pkcs7').decode('utf-8')
