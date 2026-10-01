import math


# =====================================================================
#                            КЛАСС ANGLE
# =====================================================================
class Angle:
    """Угол. Внутреннее состояние — радианы."""
    TAU = 2.0 * math.pi

    def __init__(self, radians=0.0):
        self.set_radians(radians)

    # ---------- фабричные методы ----------
    @classmethod
    def from_radians(cls, radians):
        return cls(radians)

    @classmethod
    def from_degrees(cls, degrees):
        return cls(math.radians(float(degrees)))

    # ---------- геттеры и сеттеры ----------
    def get_radians(self):
        return self._radians

    def set_radians(self, radians):
        if not isinstance(radians, (int, float)):
            raise TypeError("radians must be int or float")
        self._radians = float(radians)

    def get_degrees(self):
        return math.degrees(self._radians)

    def set_degrees(self, degrees):
        if not isinstance(degrees, (int, float)):
            raise TypeError("degrees must be int or float")
        self._radians = math.radians(float(degrees))

    # ---------- нормализация ----------
    def _normalized(self):
        return self._radians % self.TAU

    # ---------- сравнение ----------
    def _eq(self, other):
        diff = (self._radians - other._radians) % self.TAU
        return (math.isclose(diff, 0.0, abs_tol=1e-9) or
                math.isclose(diff, self.TAU, abs_tol=1e-9))

    def __eq__(self, other):
        if not isinstance(other, Angle):
            return NotImplemented
        return self._eq(other)

    def __ne__(self, other):
        r = self.__eq__(other)
        return r if r is NotImplemented else not r

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

    # ---------- float / int ----------
    def __float__(self):
        return self._radians

    def __int__(self):
        return int(self._radians)

    # ---------- сложение ----------
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

    # ---------- вычитание ----------
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

    # ---------- умножение ----------
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Angle.from_radians(self._radians * other)
        return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return Angle.from_radians(other * self._radians)
        return NotImplemented

    # ---------- деление ----------
    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Angle.from_radians(self._radians / other)
        return NotImplemented

    # ---------- унарный минус ----------
    def __neg__(self):
        return Angle.from_radians(-self._radians)

    # ---------- строки ----------
    def __str__(self):
        return f"{self.get_degrees():.6g}° ({self._radians:.6g} rad)"

    def __repr__(self):
        return f"Angle.from_radians({self._radians!r})"


# =====================================================================
#                          КЛАСС ANGLERANGE
# =====================================================================
class AngleRange:
    """
    Промежуток углов. Хранит начало и конец как Angle.
    Флаги start_inclusive / end_inclusive: включать ли границы.
    Если start > end после нормализации — промежуток «через 0».
    """

    def __init__(self, start, end,
                 start_inclusive=True, end_inclusive=True):
        self._start = self._to_angle(start)
        self._end = self._to_angle(end)
        self._start_inclusive = bool(start_inclusive)
        self._end_inclusive = bool(end_inclusive)

    # ---------- создание ----------
    @staticmethod
    def _to_angle(value):
        if isinstance(value, Angle):
            return value
        if isinstance(value, (int, float)):
            return Angle.from_radians(value)
        raise TypeError("start/end must be Angle, int or float")

    @classmethod
    def from_degrees(cls, start_deg, end_deg,
                     start_inclusive=True, end_inclusive=True):
        return cls(Angle.from_degrees(start_deg),
                   Angle.from_degrees(end_deg),
                   start_inclusive, end_inclusive)

    # ---------- геттеры ----------
    def get_start(self):
        return self._start

    def get_end(self):
        return self._end

    def is_start_inclusive(self):
        return self._start_inclusive

    def is_end_inclusive(self):
        return self._end_inclusive

    # ---------- длина ----------
    def length(self):
        diff = (self._end.get_radians() -
                self._start.get_radians()) % Angle.TAU
        return diff

    def __abs__(self):
        return self.length()

    # ---------- вхождение ----------
    def contains(self, item):
        if isinstance(item, AngleRange):
            return self._contains_range(item)
        if isinstance(item, Angle):
            return self._contains_angle(item)
        if isinstance(item, (int, float)):
            return self._contains_angle(Angle.from_radians(item))
        raise TypeError("item must be AngleRange, Angle, int or float")

    def _contains_angle(self, angle):
        length = self.length()
        if math.isclose(length, 0.0, abs_tol=1e-9):
            return False                     # пустой
        if math.isclose(length, Angle.TAU, abs_tol=1e-9):
            return True                      # полный круг

        s = self._start.get_radians() % Angle.TAU
        e = self._end.get_radians() % Angle.TAU
        x = angle.get_radians() % Angle.TAU

        on_start = math.isclose(x, s, abs_tol=1e-9)
        on_end = math.isclose(x, e, abs_tol=1e-9)
        if on_start:
            return self._start_inclusive
        if on_end:
            return self._end_inclusive

        if s < e:
            return s < x < e
        else:                                # перешли через 0
            return x > s or x < e

    def _contains_range(self, other):
        return (self._contains_angle(other._start) and
                self._contains_angle(other._end))

    def __contains__(self, item):
        return self.contains(item)

    # ---------- эквивалентность ----------
    def __eq__(self, other):
        if not isinstance(other, AngleRange):
            return NotImplemented
        return (self._start == other._start and
                self._end == other._end and
                self._start_inclusive == other._start_inclusive and
                self._end_inclusive == other._end_inclusive)

    def __ne__(self, other):
        r = self.__eq__(other)
        return r if r is NotImplemented else not r

    # ---------- сравнение промежутков ----------
    def __lt__(self, other):
        if not isinstance(other, AngleRange):
            return NotImplemented
        if self._start == other._start:
            return self.length() < other.length()
        return self._start < other._start

    def __le__(self, other):
        if not isinstance(other, AngleRange):
            return NotImplemented
        return self < other or self == other

    def __gt__(self, other):
        if not isinstance(other, AngleRange):
            return NotImplemented
        return not self <= other

    def __ge__(self, other):
        if not isinstance(other, AngleRange):
            return NotImplemented
        return not self < other

    # ---------- вспомогательное ----------
    def _overlaps(self, other):
        return (self._contains_angle(other._start) or
                self._contains_angle(other._end) or
                other._contains_angle(self._start) or
                other._contains_angle(self._end))

    def _merge(self, other):
        """Объединить два пересекающихся промежутка (без wrap-around)."""
        s1, e1 = self._start, self._end
        s2, e2 = other._start, other._end

        if s1 < s2:
            new_start, new_si = s1, self._start_inclusive
        elif s2 < s1:
            new_start, new_si = s2, other._start_inclusive
        else:
            new_start = s1
            new_si = self._start_inclusive or other._start_inclusive

        if e1 < e2:
            new_end, new_ei = e2, other._end_inclusive
        elif e2 < e1:
            new_end, new_ei = e1, self._end_inclusive
        else:
            new_end = e1
            new_ei = self._end_inclusive or other._end_inclusive

        return AngleRange(new_start, new_end, new_si, new_ei)

    # ---------- сложение ----------
    def __add__(self, other):
        if isinstance(other, Angle):
            return AngleRange(self._start + other, self._end + other,
                              self._start_inclusive, self._end_inclusive)
        if isinstance(other, (int, float)):
            shift = Angle.from_radians(other)
            return AngleRange(self._start + shift, self._end + shift,
                              self._start_inclusive, self._end_inclusive)
        if isinstance(other, AngleRange):
            if self._overlaps(other):
                return [self._merge(other)]
            return [self, other]
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, (int, float)):
            shift = Angle.from_radians(other)
            return AngleRange(self._start + shift, self._end + shift,
                              self._start_inclusive, self._end_inclusive)
        return NotImplemented

    # ---------- вычитание ----------
    def __sub__(self, other):
        if isinstance(other, Angle):
            return AngleRange(self._start - other, self._end - other,
                              self._start_inclusive, self._end_inclusive)
        if isinstance(other, (int, float)):
            shift = Angle.from_radians(other)
            return AngleRange(self._start - shift, self._end - shift,
                              self._start_inclusive, self._end_inclusive)
        if isinstance(other, AngleRange):
            return self._subtract_range(other)
        return NotImplemented

    def _subtract_range(self, other):
        if (other._contains_angle(self._start) and
                other._contains_angle(self._end)):
            if other.length() >= self.length():
                return []

        if not self._overlaps(other):
            return [self]

        result = []

        if (not other._contains_angle(self._start) and
                self._contains_angle(other._start)):
            left = AngleRange(self._start, other._start,
                              self._start_inclusive,
                              not other._start_inclusive)
            if left.length() > 1e-9:
                result.append(left)

        if (not other._contains_angle(self._end) and
                self._contains_angle(other._end)):
            right = AngleRange(other._end, self._end,
                               not other._end_inclusive,
                               self._end_inclusive)
            if right.length() > 1e-9:
                result.append(right)

        return result if result else [self]

    # ---------- строки ----------
    def __str__(self):
        left = "[" if self._start_inclusive else "("
        right = "]" if self._end_inclusive else ")"
        return f"{left}{self._start} .. {self._end}{right}"

    def __repr__(self):
        return (f"AngleRange(start={self._start!r}, end={self._end!r}, "
                f"start_inclusive={self._start_inclusive}, "
                f"end_inclusive={self._end_inclusive})")


# =====================================================================
#                          ДЕМОНСТРАЦИЯ
# =====================================================================
print("=" * 65)
print(" Angle")
print("=" * 65)

a = Angle.from_degrees(30)
b = Angle.from_radians(math.pi / 6)

print("a          =", a)
print("b          =", b)
print("repr(a)    =", repr(a))
print("a == b     =", a == b)
print("a.degrees  =", a.get_degrees())
print("a.radians  =", a.get_radians())

a.set_degrees(90)
print("после set_degrees(90):", a.get_degrees(), "|", a.get_radians())

print("370° == 10°:", Angle.from_degrees(370) == Angle.from_degrees(10))
print("10° < 20°  :", Angle.from_degrees(10) < Angle.from_degrees(20))
print("20° > 10°  :", Angle.from_degrees(20) > Angle.from_degrees(10))
print("10° != 20° :", Angle.from_degrees(10) != Angle.from_degrees(20))

print("a + b      =", a + b)
print("a - b      =", a - b)
print("a + 1.0    =", a + 1.0)
print("1.0 + a    =", 1.0 + a)
print("a - 1.0    =", a - 1.0)
print("1.0 - a    =", 1.0 - a)
print("a * 2      =", a * 2)
print("2 * a      =", 2 * a)
print("a / 2      =", a / 2)
print("-a         =", -a)
print("float(a)   =", float(a))
print("int(a)     =", int(a))

print()
print("=" * 65)
print(" AngleRange")
print("=" * 65)

r1 = AngleRange.from_degrees(0, 90)
r2 = AngleRange.from_degrees(45, 180)
r3 = AngleRange.from_degrees(90, 0,
                             start_inclusive=False,
                             end_inclusive=False)
r4 = AngleRange.from_degrees(10, 20)

print("r1 =", r1)
print("r2 =", r2)
print("r3 =", r3)
print("repr(r1) =", repr(r1))

print("abs(r1)    =", abs(r1), "rad")
print("r1.length()=", r1.length(), "rad")

print("45° in r1  :", Angle.from_degrees(45) in r1)     # True
print("120° in r1 :", Angle.from_degrees(120) in r1)    # False
print("10..20 in r1:", r4 in r1)                         # True
print("r2 in r1   :", r2 in r1)                          # False

print("r1 == from(0,90):",
      r1 == AngleRange.from_degrees(0, 90))              # True
print("r1 < r2    :", r1 < r2)                           # True
print("r1 <= r2   :", r1 <= r2)                          # True

shifted = r1 + Angle.from_degrees(10)
print("r1 + 10°   =", shifted)

shifted_back = r1 - Angle.from_degrees(10)
print("r1 - 10°   =", shifted_back)

print("r1 + r2    =", r1 + r2)                           # объединение → список
print("r1 - r4    =", r1 - r4)                           # вырезание → список
print("r1 - r2    =", r1 - r2)