import numpy as np

MAX_COORDINATE = 16
RADIUS_NOISE = 0.1
COORDINATE_NOISE = 0.2
EPS = 1e-10


#######################################################################################################################

def normal(lower=None, upper=None):
    if lower is None and upper is None:
        return np.random.normal()
    elif lower is None:
        return min(np.random.normal(), upper)
    elif upper is None:
        return max(np.random.normal(), lower)
    else:
        return max(min(np.random.normal(), upper), lower)

class BaseObject:
    """
    Базовый объект, который представляет из себя программу
    """
    def TikZ(self, noisy=False):
        """
        :return: строку-программу в TikZ формате
        """
        return "\n".join(self.to_command(noisy))

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return str(self)

    def __ne__(self, other):
        return str(self) != str(other)

    def to_command(self, noisy=False):
        assert False
        return ''


#######################################################################################################################


class Point(BaseObject):
    @staticmethod
    def sample():
        return np.random.randint(1, MAX_COORDINATE - 1)

    def __init__(self, x, y):
        self.x, self.y = x, y

    def make_divisible_by(self, denominator):
        return Point(round(self.x / denominator) * denominator,
                     round(self.y / denominator) * denominator)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, coeff):
        return Point(self.x * coeff, self.y * coeff)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return "(%s, %s)" % (str(self.x), str(self.y))

    def to_command(self, noisy=False):
        if noisy:
            return str(Point(self.x + normal() * COORDINATE_NOISE, self.y + normal() * COORDINATE_NOISE))
        else:
            return str(self)


class Line(BaseObject):
    def __init__(self, p1, p2, is_arrow=False, is_solid=True):
        self.point_from = p1
        self.point_to = p2
        self.is_arrow = is_arrow
        self.is_solid = is_solid

    def __add__(self, point):
        assert isinstance(point, Point)
        return Line(self.point_from + point, self.point_to + point, self.is_arrow, self.is_solid)

    def __sub__(self, point):
        assert isinstance(point, Point)
        return Line(self.point_from - point, self.point_to - point, self.is_arrow, self.is_solid)

    def __mul__(self, mul):
        return Line(self.point_from * mul, self.point_to * mul, self.is_arrow, self.is_solid)

    def __str__(self):
        return "Line( %s, %s, arrow = %s, solid = %s)" % (self.point_from, self.point_to,
                                                          str(self.is_arrow), str(self.is_solid))

    def length(self):
        return np.sqrt(self.x**2 + self.y**2)

    def to_command(self, noisy=False):
        old_noise = COORDINATE_NOISE



        COORDINATE_NOISE = old_noise

#######################################################################################################################


def main():
    for _ in range(100):
        lower = -0.1
        upper = 0.1
        assert normal(lower=lower) > lower - EPS
        assert normal(upper=upper) < upper + EPS
        assert lower - EPS < normal(lower=lower, upper=upper) < upper + EPS

    p1 = Point(5, 6)
    p2 = Point(3, 4)
    mul = 2
    assert str(p1) == p1.to_command() == '(5, 6)'
    assert p1 == p1
    assert p1 + p2 == Point(8, 10)
    assert p1 - p2 == Point(2, 2)
    assert p1 * mul == Point(10, 12)
    assert p1.make_divisible_by(mul) == Point(4, 6)

    print('All passed')


if __name__ == '__main__':
    main()