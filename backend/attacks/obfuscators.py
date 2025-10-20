"""Attack obfuscation utilities."""


_ROT13_SRC = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
_ROT13_DST = "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm"


def rot13(text: str) -> str:
    """Return a ROT13-transformed version of ``text``."""
    return text.translate(str.maketrans(_ROT13_SRC, _ROT13_DST))
