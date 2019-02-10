from math import cos, pi, sin
from typing import Any, List, Tuple, NamedTuple, Set, Dict


class Vector(NamedTuple):
    x: int
    y: int
    z: int

    @property
    def f(self) -> int:
        return abs(self.x) + abs(self.y) + abs(self.z)

    def __floordiv__(self, other: Any) -> 'Vector':
        return Vector(
            self.x // other,
            self.y // other,
            self.z // other,
        )

    def __truediv__(self, other: Any) -> 'Vector':
        return Vector(
            self.x / other,
            self.y / other,
            self.z / other,
        )


class Point:

    def __init__(self, x: int, y: int, z: int = 0) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.locked = False
        self.connections: List[Point] = []

    def pos(self) -> Tuple[int, int]:
        return self.x, self.y

    def connect(self, point: 'Point') -> None:
        self.connections.append(point)

    def move(self, vector: Vector) -> None:
        if self.locked:
            return

        self.x += vector.x
        self.y += vector.y
        self.z += vector.z

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return all([
            self.x == other.x,
            self.y == other.y,
            self.z == other.z
        ])

    def __hash__(self) -> int:
        return hash(self.pos())

    def __repr__(self) -> str:
        return '<Point: %d,%d,%d>' % (self.x, self.y, self.z)


class Points(dict):

    def add(self, point: Point) -> None:
        self[point] = point


class Grid:

    def __init__(self, width: int, height: int, density: int) -> None:
        self.__width = width
        self.__height = height
        self.__density = density

        self.__points = Points()

        center = Point(self.width // 2, self.height // 2, 0)
        self.__points.add(center)
        self.__populate(center)

    @property
    def width(self) -> int:
        return self.__width * self.__density

    @property
    def height(self) -> int:
        return self.__height * self.__density

    @property
    def points(self) -> List[Point]:
        return list(self.__points.values())

    def __populate(self, center: Point) -> None:
        centers = [center]
        while centers:
            center = centers.pop(0)
            for point in self.__produce(center):
                if not self.__is_in_grid(point):
                    continue

                if point not in self.__points:
                    self.__points.add(point)
                    centers.append(point)

                center.connect(self.__points.get(point))

    def __is_in_grid(self, point: Point) -> bool:
        if point.x < -self.__density or point.x > self.width + self.__density:
            return False
        if point.y < -self.__density or point.y > self.height + self.__density:
            return False
        return True

    def __produce(self, center: Point) -> List[Point]:
        sides = 6
        angle = 2 * pi / sides

        return [
            Point(
                round(center.x + self.__density * sin(i * angle)),
                round(center.y + self.__density * cos(i * angle))
            )
            for i in range(sides)
        ]

    def drag(self, point: Point, vector: Vector) -> None:
        self.__follow([point], vector, set())

    def __follow(self, points: List[Point], vector: Vector,
                 affected: Set[Point]) -> None:
        if vector.f <= 1:
            return

        for point in points:
            if point not in affected:
                point.move(vector)
                affected.add(point)

        peaking: Dict[Point, Vector] = {}
        for point in points:
            for connection in point.connections:
                peaking[connection] = self.__peak(
                    vector // 2,
                    connection,
                    point
                )

        for point, peak in peaking.items():
            if point not in affected:
                point.move(peak)
                affected.add(point)

        self.__follow(
            [
                connection
                for point in points
                for connection in point.connections
            ],
            vector // 2,
            affected
        )

    def __peak(self, vector: Vector, point: Point, center: Point) -> Vector:
        if point.x == center.x:
            ox = vector.x
            oy = abs(vector.z) * (-1 if point.y > center.y else 1)
        else:
            ox = abs(vector.z) * (-1 if point.x > center.x else 1)
            oy = abs(vector.z // 2) * (-1 if point.y > center.y else 1)

        ox = ox * 100 // self.__density // 2
        oy = oy * 100 // self.__density // 2

        return Vector(
            vector.x + min(ox, self.__density),
            vector.y + min(oy, self.__density),
            vector.z
        )
