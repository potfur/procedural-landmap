from abc import ABC, abstractmethod
from math import cos, pi, sin
from typing import Tuple, List, Any, Dict


class Point:

    def __init__(self, x: int, y: int, z: int = 0) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.locked = False

    def pos(self) -> Tuple[int, int]:
        return self.x, self.y

    def move(self, x: int, y: int, z: int) -> None:
        if self.locked:
            return

        self.x += x
        self.y += y
        self.z += z

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
        return self.pos().__hash__()

    def __repr__(self) -> str:
        return '<Point: %d,%d,%d>' % (self.x, self.y, self.z)


class Cell:

    @classmethod
    def hex(cls, x: int, y: int, r: int) -> 'Cell':
        return cls.poly(x, y, r, 6)

    @classmethod
    def poly(cls, x: int, y: int, r: int, sides: int) -> 'Cell':
        angle = 2 * pi / sides
        return cls(
            Point(x, y),
            [
                Point(
                    round(x + r * sin(i * angle)),
                    round(y + r * cos(i * angle))
                )
                for i in range(sides)
            ]
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

    def drag(self, x: int, y: int, z: int) -> None:
        self.__drag_cell(self, x, y, z, [])

    def __drag_cell(
            self,
            cell: 'Cell',
            x: int,
            y: int,
            z: int,
            affected: List[Point]
    ) -> None:
        if abs(x) <= 1 and abs(y) <= 1:
            return

        cell.center.move(x, y, z)
        affected.append(cell.center)

        for point in cell.points:
            point.move(
                self.__stretch(x, point.x, cell.center.x),
                self.__stretch(y, point.y, cell.center.y),
                self.__stretch(z, point.z, cell.center.y),
            )

        for connection in cell.connections:
            self.__drag_cell(
                connection,
                self.__stretch(x, connection.center.x, cell.center.x),
                self.__stretch(y, connection.center.y, cell.center.y),
                self.__stretch(z, connection.center.z, cell.center.z),
                affected
            )

    def __stretch(self, x: int, point: int, reference: int) -> int:
        if x > 0:
            return x // 4 if point > reference else x // 2
        else:
            return x // 2 if point > reference else x // 4


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
