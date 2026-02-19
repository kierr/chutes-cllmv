import ctypes
import logging
import os

logger = logging.getLogger(__name__)


class ChutesLLMVerifier:
    def __init__(self, lib_path: str | None = None):
        resolved = lib_path or "/usr/local/lib/chutes-aegis.so"
        if not resolved or not os.path.exists(resolved):
            logger.warning("chutes-aegis.so not found; cllmv running in stub mode")
            self.lib = None
            return

        self.lib = ctypes.CDLL(resolved)

        # generate(id, created, value) -> 32-hex token
        self.lib.generate.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p]
        self.lib.generate.restype = ctypes.c_char_p

        # validate(id, created, value, expected_hash, sub, model, revision) -> int
        self.lib.validate.argtypes = [
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]
        self.lib.validate.restype = ctypes.c_int

        # get_session_init() -> 312-hex init blob
        self.lib.get_session_init.argtypes = []
        self.lib.get_session_init.restype = ctypes.c_char_p

        # decrypt_session_key(blob_hex, x25519_priv_hex, out, out_len) -> int
        self.lib.decrypt_session_key.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        self.lib.decrypt_session_key.restype = ctypes.c_int

        # validate_v2(id, created, value, token, session_key_hex, sub, model, revision) -> int
        self.lib.validate_v2.argtypes = [
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]
        self.lib.validate_v2.restype = ctypes.c_int

    def generate(self, id: str, created: int, value: str) -> str:
        if self.lib is None:
            return ""
        result = self.lib.generate(
            id.encode("utf-8"),
            created,
            value.encode("utf-8") if value else None,
        )
        return result.decode("utf-8") if result else ""

    def get_session_init(self) -> str:
        """Get the hex-encoded session init blob (312 hex chars on miner, empty on validator)."""
        if self.lib is None:
            return ""
        result = self.lib.get_session_init()
        return result.decode("utf-8") if result else ""

    def decrypt_session_key(self, blob_hex: str, x25519_private_key_hex: str) -> str | None:
        """Decrypt the miner's ephemeral HMAC key from the init blob.

        Returns the 64-hex session key on success, None on failure.
        """
        if self.lib is None:
            return None
        key_buf = ctypes.create_string_buffer(65)
        ret = self.lib.decrypt_session_key(
            blob_hex.encode("utf-8"),
            x25519_private_key_hex.encode("utf-8"),
            key_buf,
            65,
        )
        if ret != 0:
            return None
        return key_buf.value.decode("utf-8")

    def validate(
        self,
        id: str,
        created: int,
        value: str,
        expected_hash: str,
        salt: str,
        model: str,
        revision: str,
    ) -> bool:
        """Validate a V1 token (32-hex MD5 interleaving hash)."""
        if self.lib is None:
            return False
        result = self.lib.validate(
            id.encode("utf-8"),
            created,
            value.encode("utf-8") if value else None,
            expected_hash.encode("utf-8"),
            salt.encode("utf-8"),
            model.encode("utf-8"),
            revision.encode("utf-8"),
        )
        return bool(result)

    def validate_v2(
        self,
        id: str,
        created: int,
        value: str,
        expected_token: str,
        session_key_hex: str,
        sub: str,
        model: str,
        revision: str,
    ) -> bool:
        """Validate a V2 token (32-hex HMAC-SHA256) using the decrypted session key."""
        if self.lib is None:
            return False
        result = self.lib.validate_v2(
            id.encode("utf-8"),
            created,
            value.encode("utf-8") if value else None,
            expected_token.encode("utf-8"),
            session_key_hex.encode("utf-8"),
            sub.encode("utf-8"),
            model.encode("utf-8"),
            revision.encode("utf-8"),
        )
        return bool(result)

    @staticmethod
    def is_v2_session(init_blob: str) -> bool:
        """Check if an init blob is a valid V2 session init (312-hex chars)."""
        return len(init_blob) == 312
