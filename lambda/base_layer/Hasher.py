import hashlib
import binascii
import os


class Hasher:

    @staticmethod
    def hash_password(password: str) -> str:
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha512',
            password.encode('utf-8'),
            salt,
            100000
        )
        pwd_hash = binascii.hexlify(pwd_hash)
        return (salt + pwd_hash).decode('ascii')

    @staticmethod
    def verify_password(stored_password, provided_password):
        salt = stored_password[:64]
        stored_password = stored_password[64:]
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha512',
            provided_password.encode('utf-8'),
            salt.encode('ascii'),
            100000
        )
        pwd_hash = binascii.hexlify(pwd_hash).decode('ascii')
        return pwd_hash == stored_password
