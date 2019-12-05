import numpy as np
from random import random, choice, shuffle
import math
import itertools

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

    def support_coordinate_x(self):
        assert False
        return []

    def support_coordinate_y(self):
        assert False
        return []

    def connection_points(self):
        assert False
        return []

    def intersects(self, other):
        assert False



#######################################################################################################################


def sample_coordinate():
    return np.random.randint(1, MAX_COORDINATE)


def sample_radius():
    return np.random.randint(1, 6)


class Point(BaseObject):
    @staticmethod
    def sample(existing_objects):
        line_points = []
        for obj in existing_objects:
            if isinstance(obj, Line):
                line_points.extend([obj.point_from, obj.point_to])

        # семплируем из концов существующих линий
        if len(line_points) != 0 and random() < 0.1:
            return choice(line_points)

        support_x = [x for obj in existing_objects for x in obj.support_coordinate_x()]
        support_y = [y for obj in existing_objects for y in obj.support_coordinate_y()]
        sample_way = choice(range(3))
        if sample_way == 0 and len(support_y) > 0:
            return Point(sample_coordinate(), choice(support_y))
        elif sample_way == 1 and len(support_y) > 0:
            return Point(choice(support_x), sample_coordinate())
        else:
            return Point(sample_coordinate(), sample_coordinate())

    @staticmethod
    def distance(p1, p2):
        return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

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

    def __hash__(self):
        return hash((self.x, self.y))

    def is_valid(self):
        return 1 <= self.x <= MAX_COORDINATE - 1 and 1 <= self.y <= MAX_COORDINATE - 1

    def make_noisy(self):
        return Point(self.x + normal() * COORDINATE_NOISE, self.y + normal() * COORDINATE_NOISE)

    def to_command(self, noisy=False):
        if noisy:
            return str(self.make_noisy())
        return str(self)

    def support_coordinate_x(self):
        return [self.x]

    def support_coordinate_y(self):
        return [self.y]

    def connection_points(self):
        return Point(self.x, self.y)

#######################################################################################################################


class Line(BaseObject):
    @staticmethod
    def _sample_connected(existing_objects):
        connection_points_for_obj = [obj.connection_points() for obj in filter(lambda x: not(isinstance(x, Line)), existing_objects)]

        vert_and_hor_lines = []
        other_lines = []
        for (points_set1, points_set2) in itertools.combinations(connection_points_for_obj, r=2):
            for point1, point2 in itertools.product(points_set1, points_set2):
                good_line = False
                if point1.x == point2.x and point1.y != point2.y:
                    point_from = Point(point1.x, min(point1.y, point2.y))
                    point_to = Point(point2.x, max(point1.y, point2.y))
                    good_line = True
                elif point1.x != point2.x and point1.y == point2.y:
                    point_from = Point(min(point1.x, point2.x), point1.y)
                    point_to = Point(max(point1.x, point2.x), point2.y)
                    good_line = True
                else:
                    point_from = point1
                    point_to = point2
                    good_line = False

                line_to_add = Line(point_from, point_to)
                if good_line:
                    vert_and_hor_lines.append(line_to_add)
                else:
                    other_lines.append(line_to_add)

        if len(other_lines) != 0:
            shuffle(other_lines)
            other_lines = other_lines[:min(len(other_lines), max(1000, len(vert_and_hor_lines)))]
        return vert_and_hor_lines + other_lines

    @staticmethod
    def sample(existing_objects):
        connection_lines = Line._sample_connected(existing_objects) if len(existing_objects) else []
        if len(connection_lines) != 0 and random() < 0.8:
            rand_line = choice(connection_lines)
            return Line(rand_line.point_from, rand_line.point_to, random() < 0.5, random() < 0.5)

        point_from = Point.sample(existing_objects)

        x = point_from.x
        y = point_from.y
        if random() < 0.5:
            while abs(point_from.y - y) < 2:
                y = sample_coordinate()
        else:
            while abs(point_from.x - x) < 2:
                x = sample_coordinate()
        point_to = Point(x, y)
        return Line(point_from, point_to, random() < 0.5, random() < 0.5)



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

    def support_coordinate_x(self):
        return [self.point_from.x, self.point_to.x]

    def support_coordinate_y(self):
        return [self.point_from.y, self.point_to.y]

    def connection_points(self):
        # с линиями не соединяемся, это они присоединяются
        return []

    def intersects(self, other):
        if isinstance(other, Line):
            def orientation(p, q, r):
                val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
                if val == 0: return 0  # colinear
                if val > 0: return 1
                return 2

            o1 = orientation(self.point_from, self.point_to, other.point_from)
            o2 = orientation(self.point_from, self.point_to, other.point_to)
            o3 = orientation(other.point_from, other.point_to, self.point_from)
            o4 = orientation(other.point_from, other.point_to, self.point_to)

            if o1 != o2 and o3 != o4:
                return True

            return False

        if isinstance(other, Rectangle):
            points = [other.top_left, other.top_right, other.bottom_right, other.bottom_left]
            for i in range(1, len(points)):
                line = Line(points[i - 1], points[i])
                if self.intersects(line):
                    return True
            return False

        if isinstance(other, Circle):
            steps = 50
            for alpha in range(steps + 1):
                alpha = float(alpha) / steps
                x = self.point_from.x * alpha + self.point_to.x * (1 - alpha)
                y = self.point_from.y * alpha + self.point_to.y * (1 - alpha)
                dist = (x - other.center.x)**2 + (y - other.center.y)**2
                # точка внутри круга
                if dist < other.radius**2:
                    return True
            return False




#######################################################################################################################


class Circle(BaseObject):
    @staticmethod
    def sample(existing_objects):
        existing_radius = [circle.radius for circle in filter(lambda obj: isinstance(obj, Circle), existing_objects)]
        reuse_radius_prob = 0.5
        while True:
            if len(existing_radius) > 0 and random() < reuse_radius_prob:
                radius = choice(existing_radius)
            else:
                radius = sample_radius()
            center = Point.sample(existing_objects)
            circ = Circle(center, radius)
            if circ.is_valid():
                return circ

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

    def is_valid(self):
        c = self.center
        r = self.radius
        return Point(c.x - r, c.y).is_valid() and\
               Point(c.x + r, c.y).is_valid() and\
               Point(c.x, c.y - r).is_valid() and\
               Point(c.x, c.y + r).is_valid()

    def support_coordinate_x(self):
        return [self.center.x - self.radius, self.center.x, self.center.x + self.radius]

    def support_coordinate_y(self):
        return [self.center.y - self.radius, self.center.y, self.center.y + self.radius]

    def connection_points(self):
        return [Point(x, y) for (x, y) in zip(self.support_coordinate_x(), self.support_coordinate_y())]

    def intersects(self, other):
        if isinstance(other, Line) or isinstance(other, Rectangle):
            return other.intersects(self)
        if isinstance(other, Circle):
            x1, y1, r1 = self.center.x,self.center.y,self.radius
            x2, y2, r2 = other.center.x, other.center.y, other.radius
            return (x1 - x2)**2 + (y1 - y2)**2 < (r1 + r2)**2


#######################################################################################################################


class Rectangle(BaseObject):
    @staticmethod
    def sample(existing_objects):
        while True:
            p1 = Point.sample(existing_objects)
            p2 = Point.sample(existing_objects)
            x1 = (min([p1.x, p2.x]))
            x2 = (max([p1.x, p2.x]))
            y1 = (min([p1.y, p2.y]))
            y2 = (max([p1.y, p2.y]))
            top_left = Point(x1, y1)
            bottom_right = Point(x2, y2)
            diff = top_left - bottom_right
            if abs(diff.x) > 0.5 and abs(diff.y) > 0.5:
                return Rectangle(top_left=top_left, bottom_right=bottom_right)

    def __init__(self, top_left=None, top_right=None, bottom_right=None, bottom_left=None):
        assert top_left is not None and bottom_right is not None

        self.top_left = top_left
        self.bottom_right = bottom_right
        if top_right is None:
            self.top_right = Point(self.bottom_right.x, self.top_left.y)
        else:
            self.top_right = top_right
        if bottom_left is None:
            self.bottom_left = Point(self.top_left.x, self.bottom_right.y)
        else:
            self.bottom_left = bottom_left

    def __add__(self, point):
        return Rectangle(self.top_left + point, self.top_right + point,
                         self.bottom_right + point, self.bottom_left + point)

    def __sub__(self, point):
        return Rectangle(self.top_left - point, self.top_right - point,
                         self.bottom_right - point, self.bottom_left - point)

    def __str__(self):
        return "Rect( %s, %s, %s, %s )" % (self.top_left, self.top_right, self.bottom_right, self.bottom_left)

    def make_noisy(self):
        height = self.top_left.y - self.bottom_right.y
        width = self.bottom_right.x - self.top_left.x
        center = (self.top_left + self.bottom_right) * 0.5
        old = COORDINATE_NOISE
        set_coordinate_noise(0.7 * old)
        center = center.make_noisy()
        set_coordinate_noise(0.3 * old)
        top_left = center + Point(-width / 2, height / 2).make_noisy()
        top_right = center + Point(width / 2, height / 2).make_noisy()
        bottom_right = center + Point(width / 2, -height / 2).make_noisy()
        bottom_left = center + Point(-width / 2, -height / 2).make_noisy()
        set_coordinate_noise(old)
        return Rectangle(top_left, top_right, bottom_right, bottom_left)

    def to_command(self, noisy=False):
        rect = self
        if noisy:
            rect = self.make_noisy()
        top_left = rect.top_left
        top_right = rect.top_right
        bottom_right = rect.bottom_right
        bottom_left = rect.bottom_left

        attributes = ["line width = %.2fcm" % LINE_WIDTH]
        if noisy:
            attributes = ["line width = %.2fcm" % (LINE_WIDTH + normal(-1, 1) * LINE_WIDTH_NOISE)]
            attributes += ["pencildraw"]

        attributes = ",".join(attributes)
        return "\\draw [%s] %s -- %s -- %s -- %s -- cycle;" % (attributes,
                                                               top_left, top_right, bottom_right, bottom_left)

    def support_coordinate_x(self):
        return [self.top_left.x, self.top_right.x, self.bottom_right.x, self.bottom_left.x]

    def support_coordinate_y(self):
        return [self.top_left.y, self.top_right.y, self.bottom_right.y, self.bottom_left.y]

    def connection_points(self):
        return list(Point(x, y) for (x, y) in zip(self.support_coordinate_x(), self.support_coordinate_y()))

    def intersects(self, other):
        if isinstance(other, Line):
            return other.intersects(self)
        points = [self.top_left, self.top_right, self.bottom_right, self.bottom_left]
        if isinstance(other, Circle):
            for i in range(1, len(points)):
                line = Line(points[i - 1], points[i])
                if line.intersects(other):
                    return True
            return False

        if isinstance(other, Rectangle):
            points_other = [other.top_left, other.top_right, other.bottom_right, other.bottom_left]
            lines1 = [Line(points[i - 1], points[i]) for i in range(1, len(points))]
            lines2 = [Line(points_other[i - 1], points_other[i]) for i in range(1, len(points_other))]
            for (line1, line2) in itertools.product(lines1, lines2):
                if line1.intersects(line2):
                    return True
            return False

#######################################################################################################################


def sample_object(existing_objects):
    r = np.random.randint(0, 3)
    if r == 0:
        return Line.sample(existing_objects)
    elif r == 1:
        return Circle.sample(existing_objects)
    elif r == 2:
        return Rectangle.sample(existing_objects)
    else:
        assert False

def sample_without_intersection(existing_objects):
    max_iter = 10**5
    obj = choice([Line, Circle, Rectangle])

    for i in range(max_iter):
        sampled_obj = obj.sample(existing_objects)
        if not any([obj.intersects(sampled_obj) for obj in existing_objects]):
            return sampled_obj
    print('MAX_ITERS while generation without intersection')
    return obj.sample(existing_objects)


class Figure(BaseObject):
    @staticmethod
    def sample(max_obj_count):
        exitsting_objects = []
        objects_to_sample = max(5, choice(range(max_obj_count)) + 1)
        for _ in range(objects_to_sample):
            exitsting_objects.append(sample_without_intersection(exitsting_objects))
            print('Sampled')
        return Figure(exitsting_objects)

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

    def support_coordinate_x(self):
        return [obj_x for obj in self.objects for obj_x in obj.support_coordinate_x()]

    def support_coordinate_y(self):
        return [obj_y for obj in self.objects for obj_y in obj.support_coordinate_y()]

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