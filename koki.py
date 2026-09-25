import math
from typing import Union

Number = Union[int, float]


class Angle:
    TAU = 2.0 * math.pi

    def __init__(self, radians: Number = 0.0) -> None:
        self.set_radians(radians)

    # ---------- фабричные методы ----------
    @classmethod
    def from_radians(cls, radians: Number) -> "Angle":
        return cls(radians)

    @classmethod
    def from_degrees(cls, degrees: Number) -> "Angle":
        return cls(math.radians(float(degrees)))

    # ---------- геттеры/сеттеры без @property ----------
    def get_radians(self) -> float:
        return self._radians

    def set_radians(self, radians: Number) -> None:
        if not isinstance(radians, (int, float)):
            raise TypeError("radians must be int or float")
        self._radians = float(radians)

    def get_degrees(self) -> float:
        return math.degrees(self._radians)

    def set_degrees(self, degrees: Number) -> None:
        if not isinstance(degrees, (int, float)):
            raise TypeError("degrees must be int or float")
        self._radians = math.radians(float(degrees))

    # ---------- приведение к каноническому виду [0, 2π) ----------
    def _normalized(self) -> float:
        return self._radians % self.TAU

    def _eq(self, other: "Angle") -> bool:
        diff = (self._radians - other._radians) % self.TAU
        return (
            math.isclose(diff, 0.0, abs_tol=1e-9)
            or math.isclose(diff, self.TAU, abs_tol=1e-9)
        )

    # ---------- сравнение ----------
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Angle):
            return NotImplemented
        return self._eq(other)

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def __lt__(self, other: "Angle") -> bool:
        if not isinstance(other, Angle):
            return NotImplemented
        if self == other:
            return False
        return self._normalized() < other._normalized()

    def __le__(self, other: "Angle") -> bool:
        if not isinstance(other, Angle):
            return NotImplemented
        if self == other:
            return True
        return self._normalized() < other._normalized()

    def __gt__(self, other: "Angle") -> bool:
        if not isinstance(other, Angle):
            return NotImplemented
        if self == other:
            return False
        return self._normalized() > other._normalized()

    def __ge__(self, other: "Angle") -> bool:
        if not isinstance(other, Angle):
            return NotImplemented
        if self == other:
            return True
        return self._normalized() > other._normalized()

    # ---------- преобразование к float и int ----------
    def __float__(self) -> float:
        return self._radians

    def __int__(self) -> int:
        return int(self._radians)

    # ---------- сложение ----------
    def __add__(self, other: Union["Angle", Number]) -> "Angle":
        if isinstance(other, Angle):
            return Angle.from_radians(self._radians + other._radians)
        if isinstance(other, (int, float)):
            return Angle.from_radians(self._radians + other)
        return NotImplemented

    def __radd__(self, other: Number) -> "Angle":
        if isinstance(other, (int, float)):
            return Angle.from_radians(other + self._radians)
        return NotImplemented

    # ---------- вычитание ----------
    def __sub__(self, other: Union["Angle", Number]) -> "Angle":
        if isinstance(other, Angle):
            return Angle.from_radians(self._radians - other._radians)
        if isinstance(other, (int, float)):
            return Angle.from_radians(self._radians - other)
        return NotImplemented

    def __rsub__(self, other: Number) -> "Angle":
        if isinstance(other, (int, float)):
            return Angle.from_radians(other - self._radians)
        return NotImplemented

    # ---------- умножение на число ----------
    def __mul__(self, other: Number) -> "Angle":
        if isinstance(other, (int, float)):
            return Angle.from_radians(self._radians * other)
        return NotImplemented

    def __rmul__(self, other: Number) -> "Angle":
        if isinstance(other, (int, float)):
            return Angle.from_radians(other * self._radians)
        return NotImplemented

    # ---------- деление на число ----------
    def __truediv__(self, other: Number) -> "Angle":
        if isinstance(other, (int, float)):
            return Angle.from_radians(self._radians / other)
        return NotImplemented

    # ---------- дополнительно ----------
    def __neg__(self) -> "Angle":
        return Angle.from_radians(-self._radians)

    def __str__(self) -> str:
        return f"{self.get_degrees():.6g}° ({self._radians:.6g} rad)"

    def __repr__(self) -> str:
        return f"Angle.from_radians({self._radians!r})"


if __name__ == "__main__":
    a = Angle.from_degrees(30)
    b = Angle.from_radians(math.pi / 6)

    print(a)
    print(repr(a))

    print(a == b)                 # True
    print(a.get_degrees())        # 30.0
    print(a.get_radians())        # 0.5235987755982988

    a.set_degrees(90)
    print(a.get_degrees(), a.get_radians())

    print(Angle.from_degrees(370) == Angle.from_degrees(10))  # True
    print(Angle.from_degrees(10) < Angle.from_degrees(20))    # True

    print(a + b)
    print(a - b)
    print(a + 1.0)
    print(1.0 + a)
    print(a - 1.0)
    print(1.0 - a)
    print(a * 2)
    print(2 * a)
    print(a / 2)