"""Small secrets (OAuth token, OAuth client) stored locally, encrypted for this Windows user.

On Windows the bytes are protected with DPAPI (CryptProtectData): only the same
Windows account on this PC can decrypt them. Elsewhere the file is written
with owner-only permissions. Secrets never go to the browser or the logs.
"""

from __future__ import annotations

import ctypes
import os
import sys
from pathlib import Path

_MAGIC = b"LMSDPAPI1\n"


class _Blob(ctypes.Structure):
    _fields_ = [("cbData", ctypes.c_uint32), ("pbData", ctypes.POINTER(ctypes.c_char))]


def _dpapi(data: bytes, protect: bool) -> bytes:
    crypt32, kernel32 = ctypes.windll.crypt32, ctypes.windll.kernel32
    buffer = ctypes.create_string_buffer(data, len(data))
    blob_in = _Blob(len(data), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_char)))
    blob_out = _Blob()
    fn = crypt32.CryptProtectData if protect else crypt32.CryptUnprotectData
    if not fn(ctypes.byref(blob_in), None, None, None, None, 0x1, ctypes.byref(blob_out)):   # 0x1: no UI
        raise OSError("Windows could not " + ("encrypt" if protect else "decrypt") + " the stored credentials.")
    try:
        return ctypes.string_at(blob_out.pbData, blob_out.cbData)
    finally:
        kernel32.LocalFree(blob_out.pbData)


def write_secret(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = _MAGIC + _dpapi(data, True) if sys.platform == "win32" else data
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(payload)
    if sys.platform != "win32":
        os.chmod(tmp, 0o600)
    os.replace(tmp, path)


def read_secret(path: Path) -> bytes | None:
    if not path.exists():
        return None
    payload = path.read_bytes()
    if payload.startswith(_MAGIC):
        return _dpapi(payload[len(_MAGIC):], False)
    return payload


def delete_secret(path: Path) -> None:
    path.unlink(missing_ok=True)
