import os
import hashlib

_SALT = os.getenv("ANON_SALT", "demo_salt")

def hash_id(val: str) -> str:
    h = hashlib.sha256()
    h.update((_SALT + str(val)).encode("utf-8"))
    return h.hexdigest()
