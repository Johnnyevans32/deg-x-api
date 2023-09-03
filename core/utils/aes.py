import json
import os
from typing import Any, Type, TypeVar
import asyncio

import scrypt
from Crypto.Cipher import AES
from pydantic import BaseModel

from core.config import settings


class KDFParams(BaseModel):
    dklen: int
    salt: str
    n: int
    r: int
    p: int


class CipherParams(BaseModel):
    iv: str


class CryptoModel(BaseModel):
    kdfparams: KDFParams
    cipherparams: CipherParams
    cipher: str
    kdf: str
    ciphertext: str
    mac: str


class KeystoreModel(BaseModel):
    crypto: CryptoModel
    version: int
    id: str
    format: str = "hex"


T = TypeVar("T")
enc_str = "utf-8"


class EncryptedDTO(BaseModel):
    ciphertext: str
    nonce: str
    mac: str


class AesEncryptionService:
    def __init__(self, password: str = "DEFAULT_PASSWORD") -> None:
        self.password = password

    async def encrypt_AES_GCM(self, msg: Any) -> EncryptedDTO:
        loop = asyncio.get_event_loop()
        encoded_payload = json.dumps(msg).encode(enc_str)
        aes_cipher = AES.new(bytes.fromhex(settings.SECRET_KEY), AES.MODE_GCM)

        ciphertext, auth_tag = await loop.run_in_executor(
            None, aes_cipher.encrypt_and_digest, encoded_payload
        )
        return EncryptedDTO(
            ciphertext=ciphertext.hex(),
            nonce=aes_cipher.nonce.hex(),
            mac=auth_tag.hex(),
        )

    async def decrypt_AES_GCM(
        self,
        encrypted_payload: EncryptedDTO,
    ) -> Any:
        loop = asyncio.get_event_loop()
        ciphertext = bytes.fromhex(encrypted_payload.ciphertext)
        nonce = bytes.fromhex(encrypted_payload.nonce)
        mac = bytes.fromhex(encrypted_payload.mac)
        aes_cipher = AES.new(bytes.fromhex(settings.SECRET_KEY), AES.MODE_GCM, nonce)

        dec_data = await loop.run_in_executor(
            None, aes_cipher.decrypt_and_verify, ciphertext, mac
        )
        return json.loads(dec_data)

    async def encrypt_mnemonic(
        self, user: str, msg: dict[str, Any] | str, _password: str = None
    ) -> KeystoreModel:
        loop = asyncio.get_event_loop()
        encoded_payload = json.dumps(msg).encode(enc_str)
        bytes_kdf_salt = os.urandom(16)
        dklen = 32
        p = 1
        r = 8
        n = 16384
        secret_key = await loop.run_in_executor(
            None,
            scrypt.hash,
            _password or self.password,
            bytes_kdf_salt,
            n,
            r,
            p,
            dklen,
        )

        aes_cipher = AES.new(secret_key, AES.MODE_GCM)

        cipher_text, auth_tag = await loop.run_in_executor(
            None, aes_cipher.encrypt_and_digest, encoded_payload
        )
        kdf_params = KDFParams(dklen=dklen, salt=bytes_kdf_salt.hex(), n=n, r=r, p=p)
        cipher_params = CipherParams(iv=aes_cipher.nonce.hex())
        crypto_model = CryptoModel(
            ciphertext=cipher_text.hex(),
            cipherparams=cipher_params,
            cipher="AES-GCM",
            kdf="scrypt",
            kdfparams=kdf_params,
            mac=auth_tag.hex(),
        )
        return KeystoreModel(version=1, id=user, crypto=crypto_model)

    async def decrypt_mnemonic(
        self, key_store: KeystoreModel, generic_class: Type[T], _password: str = None
    ) -> T:
        loop = asyncio.get_event_loop()
        kdf_params = key_store.crypto.kdfparams
        bytes_salt = bytes.fromhex(kdf_params.salt)
        secret_key = scrypt.hash(
            _password or self.password,
            bytes_salt,
            N=kdf_params.n,
            r=kdf_params.r,
            p=kdf_params.p,
            buflen=kdf_params.dklen,
        )
        bytes_iv = bytes.fromhex(key_store.crypto.cipherparams.iv)
        bytes_cipher_text = bytes.fromhex(key_store.crypto.ciphertext)
        bytes_mac = bytes.fromhex(key_store.crypto.mac)
        aes_cipher = AES.new(secret_key, AES.MODE_GCM, bytes_iv)
        dec_data = await loop.run_in_executor(
            None, aes_cipher.decrypt_and_verify, bytes_cipher_text, bytes_mac
        )
        return json.loads(dec_data)
