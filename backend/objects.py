import numpy as np
from random import random, choice

MAX_COORDINATE = 16
RADIUS_NOISE = 0.1
COORDINATE_NOISE = 0.2
LINE_WIDTH = 0.1
LINE_WIDTH_NOISE = 0.04
EPS = 1e-10


def set_coordinate_noise(noise):
    global COORDINATE_NOISE
    COORDINATE_NOISE = noise


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
    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return str(self)

    def __ne__(self, other):
        return str(self) != str(other)

    def make_noisy(self):
        assert False
        return self

    def to_command(self, noisy=False):
        assert False
        return ''


#######################################################################################################################


def sample_coordinate():
    return np.random.randint(1, MAX_COORDINATE)

def sample_radius():
    return np.random.randint(1, 6)


class Point(BaseObject):
    @staticmethod
    def sample():
        return Point(sample_coordinate(), sample_coordinate())

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

    def is_valid(self):
        return 1 <= self.x <= MAX_COORDINATE - 1 and 1 <= self.y <= MAX_COORDINATE - 1

    def make_noisy(self):
        return Point(self.x + normal() * COORDINATE_NOISE, self.y + normal() * COORDINATE_NOISE)

    def to_command(self, noisy=False):
        if noisy:
            return str(self.make_noisy())
        return str(self)


#######################################################################################################################


class Line(BaseObject):
    @staticmethod
    def sample():
        return Line(Point.sample(), Point.sample(), random() > 0.5, random() > 0.5)

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
        vector = self.point_to - self.point_from
        return np.sqrt(vector.x**2 + vector.y**2)

    def is_valid(self):
        return self.point_from.is_valid() and self.point_to.is_valid()

    def make_noisy(self):
        old_noise = COORDINATE_NOISE

        # короткие шумят меньше
        if self.length() < 3:
            set_coordinate_noise(old_noise * self.length() / 4 * COORDINATE_NOISE)

        line = Line(self.point_from.make_noisy(), self.point_to.make_noisy(), self.is_arrow, self.is_solid)
        set_coordinate_noise(old_noise)
        return line

    def to_command(self, noisy=False):
        line = self
        if noisy:
            line = self.make_noisy()
        width_attribute = "line width = %.2fcm"
        if noisy:
            attributes = [width_attribute % (LINE_WIDTH + normal(-1, 1) * LINE_WIDTH_NOISE)]
        else:
            attributes = [width_attribute % LINE_WIDTH]
        if line.is_arrow:
            scale = 1.5
            if noisy:
                scale = round(scale - 0.3 * random(), 1)

            styles = ["-{>[scale = %f]}",
                      "-{Stealth[scale = %f]}",
                      "-{Latex[scale = %f]}"]

            style = styles[0]
            if noisy:
                style = choice(styles)

            attributes.append(style % scale)

        if not line.is_solid:
            if noisy:
                attributes += ["dash pattern = on %dpt off %dpt" % (choice(range(2, 7)),
                                                                    choice(range(2, 7)))]
            else:
                attributes += ["dashed"]

        if noisy:
            attributes += ["pencildraw"]

        attributes_str = ", ".join(attributes)
        return "\\draw[%s] %s -- %s;" % (attributes_str, line.point_from, line.point_to)


#######################################################################################################################


class Circle(BaseObject):
    @staticmethod
    def sample():
        while True:
            c = Point.sample()
            r = sample_radius()
            if Point(c.x - r, c.y).is_valid() and\
                    Point(c.x + r, c.y).is_valid() and\
                    Point(c.x, c.y - r).is_valid() and\
                    Point(c.x, c.y + r).is_valid():
                return Circle(c, r)

    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def __add__(self, point):
        return Circle(self.center + point, self.radius)

    def __sub__(self, point):
        return Circle(self.center - point, self.radius)

    def __str__(self):
        return "Circle( %s, %f )" % (self.center, self.radius)

    def make_noisy(self):
        return Circle(self.center.make_noisy(), self.radius + normal(-1, 1) * RADIUS_NOISE)

    def to_command(self, noisy=False):
        noisy_attrib = "pencildraw, " if noisy else ""
        line_width = "line width = %.1fcm" % LINE_WIDTH
        circle = self
        if noisy:
            line_width = "line width = %.2fcm" % (LINE_WIDTH + normal(-1, 1) * LINE_WIDTH_NOISE)
            circle = self.make_noisy()
        return "\\node[draw, %scircle, inner sep=0pt, minimum size = %.2fcm, %s] at %s {};" % (noisy_attrib,
                                                                                               circle.radius * 2,
                                                                                               line_width,
                                                                                               circle.center)


#######################################################################################################################


class Rectangle(BaseObject):
    @staticmethod
    def sample():
        while True:
            p1 = Point.sample()
            p2 = Point.sample()
            if p1.x != p2.x and p1.y != p2.y:
                x1 = (min([p1.x, p2.x]))
                x2 = (max([p1.x, p2.x]))
                y1 = (min([p1.y, p2.y]))
                y2 = (max([p1.y, p2.y]))
                top_left = Point(x1, y1)
                bottom_right = Point(x2, y2)
                return Rectangle(top_left, bottom_right)


    def __init__(self, top_left, bottom_right):
        self.top_left = top_left
        self.bottom_right = bottom_right

    def __add__(self, point):
        return Rectangle(self.top_left + point, self.bottom_right + point)

    def __sub__(self, point):
        return Rectangle(self.top_left - point, self.bottom_right - point)

    def __str__(self):
        return "Rect( %s, %s )" % (self.top_left, self.bottom_right)

    def make_noisy(self):
        height = self.top_left.y - self.bottom_right.y
        widht = self.bottom_right.x - self.top_left.x
        center = (self.top_left + self.bottom_right) * 0.5
        old = COORDINATE_NOISE
        set_coordinate_noise(0.6)
        center = center.make_noisy()
        set_coordinate_noise(0.3)
        top_left = center + Point(-widht / 2, height / 2).make_noisy()
        bottom_right = center + Point(widht / 2, -height / 2).make_noisy()
        set_coordinate_noise(old)
        return Rectangle(top_left, bottom_right)

    def to_command(self, noisy=False):
        rect = self
        if noisy:
            rect = self.make_noisy()
        top_left = rect.top_left
        bottom_right = rect.bottom_right
        top_right = Point(bottom_right.x, top_left.y)
        bottom_left = Point(top_left.x, bottom_right.y)
        if noisy:
            top_right = Point(top_right.x + normal(-1, 0) * 0.15, top_right.y + normal(-1, 0) * 0.15)
            bottom_left = Point(bottom_left.x + normal(0, 1) * 0.15, bottom_right.y + normal(0, 1) * 0.15)

        attributes = ["line width = %.2fcm" % LINE_WIDTH]
        if noisy:
            attributes = ["line width = %.2fcm" % (LINE_WIDTH + normal(-1, 1) * LINE_WIDTH_NOISE)]
            attributes += ["pencildraw"]

        attributes = ",".join(attributes)
        return "\\draw [%s] %s -- %s -- %s -- %s -- cycle;" % (attributes,
                                                               top_left, top_right, bottom_right, bottom_left)



#######################################################################################################################


def sample_object():
    r = np.random.randint(0, 3)
    if r == 0:
        return Line.sample()
    if r == 1:
        return Circle.sample()
    if r == 2:
        return Rectangle.sample()



class Figure(BaseObject):
    @staticmethod
    def sample(max_obj_count):
        return Figure([sample_object() for _ in range(choice(range(1, max_obj_count + 1)))])

    def __init__(self, objects):
        self.objects = list(objects)
        for obj in objects:
            assert isinstance(obj, BaseObject)

    def __str__(self):
        return "\n".join([str(obj) for obj in self.objects])

    def make_noisy(self):
        return Figure([obj.make_noisy() for obj in self.objects])

    def to_command(self, noisy=False):
        return "\n".join([obj.to_command(noisy) for obj in self.objects])



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
    print(Figure.sample(5))

if __name__ == '__main__':
    main()