#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Author : LimerBoy
# github.com/LimerBoy/NukeShell

# Import modules
from hashlib import md5
from binascii import hexlify, unhexlify

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

class RSACipher:
    def __init__(self):
        self.public_key, self.private_key = self._GenerateKeyPair()

    @staticmethod  # Generate private and public RSA keys
    def _GenerateKeyPair() -> tuple:
        keyPair = RSA.generate(1024)
        pub_key = keyPair.publickey()
        public_key = pub_key.exportKey()
        return public_key, keyPair


    @staticmethod  # Encrypt data using RSA public key
    def Encrypt(public_key_pem, data) -> bytes:
        public_key = RSA.importKey(public_key_pem)
        encryptor = PKCS1_OAEP.new(public_key)
        encrypted = encryptor.encrypt(data)
        return hexlify(encrypted)

    # Decrypt data using RSA private key
    def Decrypt(self, data) -> bytes:
        decryptor = PKCS1_OAEP.new(self.private_key)
        decrypted = decryptor.decrypt(unhexlify(data))
        return decrypted

class AESCipher:
    def __init__(self):
        self.key = md5(self._GenerateKey().encode("utf8")).digest()

    @staticmethod
    def _GenerateKey():
        return get_random_bytes(36).decode("utf8", "ignore")

    def Encrypt(self, data: bytes) -> bytes:
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return hexlify(iv + cipher.encrypt(pad(data, AES.block_size)))

    def Decrypt(self, data: bytes) -> bytes:
        raw = unhexlify(data)
        cipher = AES.new(self.key, AES.MODE_CBC, raw[:AES.block_size])
        return unpad(cipher.decrypt(raw[AES.block_size:]), AES.block_size)

