from abc import ABC, abstractmethod
from math import cos, pi, sin
from typing import Any, Dict, List, NamedTuple, Tuple


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

    def pos(self) -> Tuple[int, int]:
        return self.x, self.y

    def move(self, vector: Vector) -> None:
        if self.locked:
            return

        self.x += vector.x
        self.y += vector.y
        self.z += vector.z

    def lock(self) -> None:
        self.locked = True

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


class Cell:

    @classmethod
    def hex(cls, x: int, y: int, r: int) -> 'Cell':
        sides = 6
        angle = 2 * pi / sides
        edges = [
            Point(
                round(x + r * sin(i * angle)),
                round(y + r * cos(i * angle))
            )
            for i in range(sides)
        ]

        return cls(
            Point(x, y),
            edges
        )

    def __init__(self, center: Point, points: List[Point]) -> None:
        self.center = center
        self.points = points
        self.connections: List[Cell] = []

    def __repr__(self) -> str:
        return '<Cell: %s>' % ",".join([
            str(point.pos())
            for point in self.points
        ])

    @property
    def width(self) -> int:
        x = [point.x for point in self.points]
        return max(x) - min(x)

    @property
    def height(self) -> int:
        y = [point.y for point in self.points]
        return max(y) - min(y)

    def connect(self, cell: 'Cell') -> None:
        self.connections.append(cell)

    def copy(self, x, y) -> 'Cell':
        return Cell(
            Point(x, y),
            [
                Point(point.x + x, point.y + y)
                for point in self.points
            ]
        )

    def drag(self, vector: Vector) -> None:
        self.__drag_cell(self, vector, [], 0)

    def __drag_cell(
            self,
            cell: 'Cell',
            vector: Vector,
            affected: List[int],
            depth: int
    ) -> None:
        if vector.f <= 1:
            return

        drags: List[Vector] = []
        for point in cell.points:
            drag = self.__peak(vector, point, cell.center)
            drag = self.__stretch(drag, point, cell.center)
            drags.append(drag)

        for i, point in enumerate(cell.points):
            if point in affected:
                continue

            point.move(drags[i])

        cell.center.move(vector)

        for point in [cell.center] + cell.points:
            affected.append(point)

        if depth > 1:
            return

        # TODO first neighbors and then deep
        for connection in cell.connections:
            if connection.center in affected:
                continue

            self.__drag_cell(
                connection,
                vector // 2,
                affected,
                depth + 1
            )

    def __stretch(self, vector: Vector, point: Point, center: Point) -> Vector:
        def calc(vector: int, point: int, center: int) -> int:
            if point < center:
                return round(vector * 0.5)
            if point == center:
                return round(vector * 0.8)
            return vector

        return Vector(
            calc(vector.x, point.x, center.x),
            calc(vector.y, point.y, center.y),
            vector.z
        )

    def __peak(self, vector: Vector, point: Point, center: Point) -> Vector:
        if point.x == center.x:
            ox = vector.x
            oy = abs(vector.z) * (-1 if point.y > center.y else 1)
        else:
            ox = abs(vector.z) * (-1 if point.x > center.x else 1)
            oy = abs(vector.z // 2) * (-1 if point.y > center.y else 1)

        if ox > self.width:
            ox = 0
        if oy > self.height:
            oy = 0

        return Vector(
            vector.x + ox,  # TODO - make it proportional
            vector.y + oy,  # TODO - make it proportional
            vector.z
        )


class Shake(ABC):

    @abstractmethod
    def apply(self, cells: Dict[Point, Cell]) -> None:
        ...


class Grid:

    def __init__(self, width: int, height: int, density: int) -> None:
        self.__width = width
        self.__height = height
        self.__density = density

        self.__cells: Dict[Point, Cell] = {}

        self.__cell: Cell = Cell.hex(0, 0, self.__density)
        self.__populate()
        self.__lock()
        self.__connect()

    @property
    def width(self) -> int:
        return self.__width * self.__cell.width - self.__cell.width // 2

    @property
    def height(self) -> int:
        return self.__height * round(self.__cell.height * 0.6)

    @property
    def cells(self) -> List[Cell]:
        return list(self.__cells.values())

    def __populate(self) -> None:
        points: Dict[Point, Point] = {}
        x = 0
        y = 0
        offset = False

        for j in range(self.__height):
            for i in range(self.__width):
                cell = self.__cell.copy(x, y)
                self.__append(cell, points)
                x += cell.width

            offset = not offset
            y += self.__cell.height * 0.75
            x = self.__cell.width // 2 if offset else 0

    def __append(self, cell: Cell, points: Dict[Point, Point]) -> None:
        for i, point in enumerate(cell.points):
            try:
                cell.points[i] = points[point]
            except KeyError:
                points[point] = point

        self.__cells[cell.center] = cell

    def __lock(self) -> None:
        for cell in self.__cells.values():
            for point in cell.points:
                if any([
                    point.x <= 0,
                    point.x >= self.width,
                    point.y <= 0,
                    point.y >= self.width
                ]):
                    point.lock()

    def __connect(self) -> None:
        for center, cell in self.__cells.items():
            points = [
                Point(
                    center.x - cell.width,
                    center.y
                ),
                Point(
                    center.x + cell.width,
                    center.y
                ),
                Point(
                    center.x - cell.width // 2,
                    center.y - round(cell.height * 0.75)
                ),
                Point(
                    center.x - cell.width // 2,
                    center.y + round(cell.height * 0.75)
                ),
                Point(
                    center.x + cell.width // 2,
                    center.y - round(cell.height * 0.75)
                ),
                Point(
                    center.x + cell.width // 2,
                    center.y + round(cell.height * 0.75)
                ),
            ]
            for point in points:
                connection = self.__cells.get(point)
                if connection:
                    cell.connect(connection)

    def apply(self, shake: Shake) -> None:
        shake.apply(self.__cells)
