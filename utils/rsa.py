from typing import Tuple

from .ecc import ENCODER, EncoderClass


class RSA:
    def __init__(self, encoder: EncoderClass) -> None:
        self.encoder = encoder

    def encrypt(self, key: Tuple[int, int], p: int) -> int:
        assert isinstance(p, int)
        assert 0 <= p and p < 256

        (e, _) = key
        result = self.encoder.decode(self.encoder.encode(p) * e)
        assert result != -1

        return result

    def decrypt(self, key: Tuple[int, int], c: int) -> int:
        assert isinstance(c, int)
        assert 0 <= c and c < 256

        (_, d) = key
        result = self.encoder.decode(self.encoder.encode(c) * d)
        assert result != -1

        return result


ECRSA = RSA(ENCODER)
