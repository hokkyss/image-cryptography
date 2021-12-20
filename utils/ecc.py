"""
CONTAINS 
ᴬᴮᶜᴰᴱᶠᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾᴿˢᵀᵁᵂˣʸᶻᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏˡᵐⁿᵒᵖ۹ʳˢᵗᵘᵛʷˣʸᶻ⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾
"""

from __future__ import annotations
from json import dumps
import random
from typing import Dict, Final, List

random.seed("ECRSA by hokkyss")


class EllipticCurvePoint:
    def __init__(
        self,
        curve: EllipticCurve = None,
        x: int = None,
        y: int = None,
        inf: bool = False,
        copy: EllipticCurvePoint = None,
    ) -> None:
        if copy:
            self.__curve = copy.curve
            self.__x = copy.x
            self.__y = copy.y
            self.__inf = copy.inf
        else:
            self.__curve = curve
            self.__x = x
            self.__y = y
            self.__inf = inf

    @property
    def curve(self) -> EllipticCurve:
        return self.__curve

    @property
    def inf(self) -> bool:
        return self.__inf

    @property
    def x(self) -> int:
        return self.__x

    @property
    def y(self) -> int:
        return self.__y

    def __str__(self) -> str:
        if self.inf:
            return "INFINITY"
        return f"({self.x}, {self.y}) on y² = x³ + {self.curve.a if self.curve.a > 1 else ''}x + {self.curve.b} (mod {self.curve.p})"

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, EllipticCurvePoint):
            return False

        return (self.inf and o.inf) or (
            self.x == o.x and self.y == o.y and self.curve == o.curve
        )

    def __add__(self, other) -> EllipticCurvePoint:
        assert isinstance(other, EllipticCurvePoint)
        if self.inf:
            return EllipticCurvePoint(copy=other)
        if other.inf:
            return EllipticCurvePoint(copy=self)

        assert self.curve == other.curve

        p = self.curve.p
        a = self.curve.a
        if self.x == other.x and (self.y != other.y or self.y + other.y == 0):
            return EllipticCurvePoint(inf=True)

        if self.x == other.x and self.y == other.y:
            m = (pow(2 * self.y, -1, p) * ((3 * pow(self.x, 2, p)) + a)) % p
        else:
            m = ((self.y - other.y) * pow(self.x - other.x, -1, p)) % p

        x = (pow(m, 2, self.curve.p) - self.x - other.x) % p
        y = ((m * (self.x - x)) - self.y) % p

        return EllipticCurvePoint(curve=self.curve, x=x, y=y)

    def __sub__(self, other) -> EllipticCurvePoint:
        assert isinstance(other, EllipticCurvePoint)

        return self + (other * -1)

    def __mul__(self, other) -> EllipticCurvePoint:
        assert isinstance(other, int)

        if self.__inf or other == 0:
            return EllipticCurvePoint(inf=True)
        if other < 0:
            return (
                EllipticCurvePoint(
                    curve=self.curve, x=self.x, y=(-self.y) % self.curve.p
                )
                * -other
            )
        if other == 1:
            return EllipticCurvePoint(copy=self)

        multiplier = other // 2
        remainder = other % 2

        temp = self * multiplier
        if remainder == 0:
            return temp + temp
        else:
            return temp + temp + self

    def __rmul__(self, other) -> EllipticCurvePoint:
        return self * other


class EllipticCurve:
    def __init__(self, a: int = 1, b: int = 4, p: int = 233) -> None:
        """
        Default parameters have 257 points, including point at infinity
        """
        assert a > 0
        assert b > 0
        assert p > 0
        """
        Use the route in app to look for parameters resulting in 256 points
        """
        self.a: int = a
        self.b: int = b
        self.p: int = p
        # self.__table is the value of y^2 % p
        self.__table: List[int] = [pow(i, 2, self.p) for i in range(self.p)]
        self.points: List[EllipticCurvePoint] = []
        self.__generate()

    def __get_y(self, i: int) -> List[int]:
        result: List[int] = []
        value = (pow(i, 3, self.p) + (self.a * i) + self.b) % self.p

        for i in range(self.p):
            if self.__table[i] == value:
                result.append(i)
        return result

    def __generate(self):
        if len(self.points) > 0:
            return

        for i in range(self.p):
            y_s_at_x = self.__get_y(i)
            for y in y_s_at_x:
                self.points.append(EllipticCurvePoint(curve=self, x=i, y=y))
        self.points.append(EllipticCurvePoint(inf=True))

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, EllipticCurve):
            return False
        return self.a == o.a and self.b == o.b and self.p == o.p

    def __str__(self) -> str:
        result: Dict[int, str] = {}
        for (i, p) in enumerate(self.points):
            result[i] = str(p)
        return dumps(result, indent=2)


ELLIPTIC_CURVE = EllipticCurve(a=1, b=1, p=277)


class EncoderClass:
    def __init__(self, ecc: EllipticCurve) -> None:
        self.encoding_table: List[EllipticCurvePoint] = ecc.points[:]
        random.shuffle(self.encoding_table)

    def encode(self, x: int) -> EllipticCurvePoint:
        return self.encoding_table[x]

    def decode(self, P: EllipticCurvePoint) -> int:
        for (i, points) in enumerate(self.encoding_table):
            if points == P:
                return i
        return -1

    def __str__(self) -> str:
        result: Dict[int, str] = {}
        for (i, p) in enumerate(self.encoding_table):
            result[i] = str(p)
        return dumps(result, indent=2)


ENCODER = EncoderClass(ecc=ELLIPTIC_CURVE)
