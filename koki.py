import math


class Angle:
    TAU = 2.0 * math.pi

    def __init__(self, radians=0.0):
        self.set_radians(radians)

    @classmethod
    def from_radians(cls, radians):
        return cls(radians)
    @classmethod
    def from_degrees(cls, degrees):
        return cls(math.radians(float(degrees)))

    def get_radians(self):
        return self._radians
    def set_radians(self, radians):
        if not isinstance(radians, (int, float)):
            raise TypeError("!!")
        self._radians = float(radians)

    def get_degrees(self):
        return math.degrees(self._radians)
    def set_degrees(self, degrees):
        if not isinstance(degrees, (int, float)):
            raise TypeError("!!")
        self._radians = math.radians(float(degrees))

    def _normalized(self):
        return self._radians % self.TAU

    def __eq__(self, other):
        if not isinstance(other, Angle):
            return NotImplemented
        diff = (self._radians - other._radians) % self.TAU
        return (
            math.isclose(diff, 0.0, abs_tol=1e-9)
            or math.isclose(diff, self.TAU, abs_tol=1e-9)
    )

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def __lt__(self, other):
        if not isinstance(other, Angle):
            return NotImplemented
        if self == other:
            return False
        return self._normalized() < other._normalized()

    def __le__(self, other):
        if not isinstance(other, Angle):
            return NotImplemented
        if self == other:
            return True
        return self._normalized() < other._normalized()

    def __gt__(self, other):
        if not isinstance(other, Angle):
            return NotImplemented
        if self == other:
            return False
        return self._normalized() > other._normalized()

    def __ge__(self, other):
        if not isinstance(other, Angle):
            return NotImplemented
        if self == other:
            return True
        return self._normalized() > other._normalized()

    def __float__(self):
        return self._radians

    def __int__(self):
        return int(self._radians)

    def __add__(self, other):
        if isinstance(other, Angle):
            return Angle.from_radians(self._radians + other._radians)
        if isinstance(other, (int, float)):
            return Angle.from_radians(self._radians + other)
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, (int, float)):
            return Angle.from_radians(other + self._radians)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Angle):
            return Angle.from_radians(self._radians - other._radians)
        if isinstance(other, (int, float)):
            return Angle.from_radians(self._radians - other)
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            return Angle.from_radians(other - self._radians)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Angle.from_radians(self._radians * other)
        return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return Angle.from_radians(other * self._radians)
        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Angle.from_radians(self._radians / other)
        return NotImplemented

    # ---------- прочее ----------
    def __neg__(self):
        return Angle.from_radians(-self._radians)

    def __str__(self):
        return f"{self.get_degrees():.6g}° ({self._radians:.6g} rad)"

    def __repr__(self):
        return f"Angle.from_radians({self._radians!r})"


if __name__ == "__main__":
    a = Angle.from_degrees(30)
    b = Angle.from_radians(math.pi / 6)

    print(a)
    print(repr(a))
    print(a == b)
    print(a.get_degrees())
    print(a.get_radians())

    a.set_degrees(90)
    print(a.get_degrees(), a.get_radians())

    print(Angle.from_degrees(370) == Angle.from_degrees(10))
    print(Angle.from_degrees(10) < Angle.from_degrees(20))

    print(a + b)
    print(a - b)
    print(a + 1.0)
    print(1.0 + a)
    print(a - 1.0)
    print(1.0 - a)
    print(a * 2)
    print(2 * a)
    print(a / 2)
    print(-a)
    print(float(a), int(a))