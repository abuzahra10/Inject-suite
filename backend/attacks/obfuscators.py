"""Attack obfuscation utilities."""

import base64

_ROT13_SRC = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
_ROT13_DST = "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm"


def rot13(text: str) -> str:
    """Return a ROT13-transformed version of ``text``."""
    return text.translate(str.maketrans(_ROT13_SRC, _ROT13_DST))


def base64_encode(text: str) -> str:
    """Return a Base64-encoded version of ``text``."""
    return base64.b64encode(text.encode()).decode()


def base64_decode(encoded: str) -> str:
    """Decode a Base64-encoded string back to plaintext."""
    return base64.b64decode(encoded.encode()).decode()
