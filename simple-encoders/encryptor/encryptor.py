import logging_config
logger = logging_config.get_logger(__name__)
logger.debug(f"start::{__name__}")
from zipfile import ZipFile, ZIP_DEFLATED
from datetime import datetime
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class Encryptor:
    def __init__(self):
        pass

    def archiving(self, dir_path:str, arc_path:str):
        def walk():
            for path, _, files in os.walk(dir_path):
                for name in files:
                    yield os.path.relpath(os.path.join(path, name), start=dir_path)
        with ZipFile(arc_path, "w", compression=ZIP_DEFLATED, compresslevel=3) as zf:
            for fn in walk():
                zf.write(os.path.join(dir_path,fn), fn)
            ok = zf.testzip()
            if ok is not None:
                logger.error(f"arc.testzip='{zf.testzip()}'")
        logger.info(f"ARC::{dir_path}::{arc_path}")

    def unarchiving(self, dir_path:str, arc_path:str):
        if os.path.exists(dir_path):
            dir_path += f" @{datetime.now().timestamp()}"
        with ZipFile(arc_path, "r") as zf:
            zf.extractall(dir_path)
        logger.info(f"UNR::'{dir_path}'::'{arc_path}'")

    def hash_md5(self, msg:str | bytes) -> int:
        from hashlib import md5
        msg = msg.encode() if type(msg) is str else msg
        return int(md5(msg).hexdigest(), 16)

    def hash_sha512(self, ps:str | bytes, salt:str | bytes = b'') -> bytes:
        ps = ps.encode() if type(ps) is str else ps
        salt = salt.encode() if type(salt) is str else salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA512(),
            length=32,
            salt=salt,
            iterations=100_000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(ps))

    def get_key(self, pass_path:str='.password') -> bytes:
        with open(pass_path, 'r') as f:
            password = f.read().strip()
            logger.debug(f"password::{self.hash_md5(password)}")
        return self.hash_sha512(password)

    def encrypt_file(self, arc_path:str, sec_path:str):
        key = self.get_key()
        enc = Fernet(key)
        with open(arc_path, "rb") as f:
            encrypted_data = enc.encrypt(f.read())
        with open(sec_path, "wb") as f:
            f.write(encrypted_data)
        logger.info(f"ENC::'{arc_path}'::'{sec_path}'")

    def decrypt_file(self, dec_path:str, sec_path:str):
        key = self.get_key()
        enc = Fernet(key)
        with open(sec_path, 'rb') as f:
            decrypted_data = enc.decrypt(f.read())
        with open(dec_path, 'wb') as f:
            f.write(decrypted_data)
        logger.info(f"DEC::'{dec_path}'::'{sec_path}'")

    def encrypt_folder(self, dir_path:str, sec_path:str, arc_path:str = None):
        cleanup = False if arc_path else True
        arc_path = arc_path or ".temp"
        self.archiving(dir_path, arc_path)
        self.encrypt_file(arc_path, sec_path)
        if cleanup:
            os.remove(arc_path)

    def decrypt_folder(self, dir_path:str, sec_path:str, arc_path:str = None):
        cleanup = False if arc_path else True
        arc_path = arc_path or ".temp"
        self.decrypt_file(arc_path, sec_path)
        self.unarchiving(dir_path, arc_path)
        if cleanup:
            os.remove(arc_path)

    def compare(self, left, rght):
        import filecmp
        if os.path.isdir(left) and os.path.isdir(rght):
            if filecmp.dircmp(left, rght):
                return True
            logger.error(f"cmp::'{left}' != '{rght}'")
            return False
        if os.path.isfile(left) and os.path.isfile(rght):
            if filecmp.cmp(left, rght):
                return True
            logger.error(f"cmp::'{left}' != '{rght}'")
            return False
        logger.error(f"cmp::invalid_formats")
        return False




