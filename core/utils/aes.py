import json
from typing import Any, Type, TypeVar, cast
from Crypto.Cipher import AES
from pydantic import BaseModel
from Crypto.Cipher._mode_gcm import GcmMode
import scrypt
import os
from base64 import b64decode, b64encode


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
    format: str = "base64"


T = TypeVar("T")
enc_str = "utf-8"


def encrypt_AES_GCM(
    user: str, msg: dict[str, Any] | str, password: str
) -> KeystoreModel:
    encoded_payload = json.dumps(msg).encode(enc_str)
    bytes_kdf_salt = os.urandom(16)
    dklen = 32
    p = 1
    r = 8
    n = 16384
    secret_key = scrypt.hash(password, bytes_kdf_salt, N=n, r=r, p=p, buflen=dklen)
    aes_cipher = cast(GcmMode, AES.new(secret_key, AES.MODE_GCM))

    cipher_text, auth_tag = aes_cipher.encrypt_and_digest(encoded_payload)

    kdf_params = KDFParams(
        dklen=dklen, salt=b64encode(bytes_kdf_salt).decode(enc_str), n=n, r=r, p=p
    )
    cipher_params = CipherParams(iv=b64encode(aes_cipher.nonce).decode(enc_str))
    crypto_model = CryptoModel(
        ciphertext=b64encode(cipher_text).decode(enc_str),
        cipherparams=cipher_params,
        cipher="",
        kdf="",
        kdfparams=kdf_params,
        mac=b64encode(auth_tag).decode(enc_str),
    )
    return KeystoreModel(version=1, id=user, crypto=crypto_model)


def decrypt_AES_GCM(
    key_store: KeystoreModel, generic_class: Type[T], password: str
) -> T:
    kdf_params = key_store.crypto.kdfparams
    bytes_salt = b64decode(kdf_params.salt)
    secret_key = scrypt.hash(
        password,
        bytes_salt,
        N=kdf_params.n,
        r=kdf_params.r,
        p=kdf_params.p,
        buflen=kdf_params.dklen,
    )
    bytes_iv = b64decode(key_store.crypto.cipherparams.iv)
    bytes_cipher_text = b64decode(key_store.crypto.ciphertext)
    bytes_mac = b64decode(key_store.crypto.mac)
    aes_cipher = cast(GcmMode, AES.new(secret_key, AES.MODE_GCM, bytes_iv))
    dec_data = aes_cipher.decrypt_and_verify(bytes_cipher_text, bytes_mac)
    return generic_class(**json.loads(dec_data))
