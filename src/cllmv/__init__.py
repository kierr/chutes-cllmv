from cllmv.base import ChutesLLMVerifier

_verifier = None


def init():
    global _verifier
    _verifier = ChutesLLMVerifier()


def generate(id: str, created: int, value: str) -> str:
    if _verifier is None:
        init()
    return _verifier.generate(id, created, value)


def get_session_init() -> str:
    if _verifier is None:
        init()
    return _verifier.get_session_init()


def decrypt_session_key(blob_hex: str, x25519_private_key_hex: str) -> str | None:
    if _verifier is None:
        init()
    return _verifier.decrypt_session_key(blob_hex, x25519_private_key_hex)


def validate(
    id: str, created: int, value: str, expected_hash: str, salt: str, model: str, revision: str
) -> bool:
    if _verifier is None:
        init()
    return _verifier.validate(id, created, value, expected_hash, salt, model, revision)


def validate_v2(
    id: str,
    created: int,
    value: str,
    expected_token: str,
    session_key_hex: str,
    sub: str,
    model: str,
    revision: str,
) -> bool:
    if _verifier is None:
        init()
    return _verifier.validate_v2(
        id, created, value, expected_token, session_key_hex, sub, model, revision
    )


def is_v2_session(init_blob: str) -> bool:
    return ChutesLLMVerifier.is_v2_session(init_blob)


__all__ = [
    "ChutesLLMVerifier",
    "generate",
    "get_session_init",
    "decrypt_session_key",
    "validate",
    "validate_v2",
    "is_v2_session",
]
