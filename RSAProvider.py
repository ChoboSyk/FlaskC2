from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import PKCS1_OAEP

class RSAProvider(object):

    def __init__(self, key):
        self.cipher_rsa = PKCS1_OAEP.new(RSA.import_key(key))

    def encrypt(self, message):
        enc_session_key = self.cipher_rsa.encrypt(message)
        return enc_session_key
