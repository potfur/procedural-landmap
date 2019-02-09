from random import randint
from typing import Dict

from grid import Shake, Point, Cell, Vector


class RandomNoise(Shake):

    def __init__(self, max_str: int) -> None:
        self.max_str = max_str

    def apply(self, cells: Dict[Point, Cell]) -> None:
        for cell in cells.values():
            for point in cell.points:
                point.move(
                    Vector(
                        randint(-self.max_str, +self.max_str),
                        randint(-self.max_str, +self.max_str),
                        0
                    )
                )


class RandomDrag(Shake):

    def __init__(self, max_str: int) -> None:
        self.max_str = max_str

    def apply(self, cells: Dict[Point, Cell]) -> None:
        for cell in cells.values():
            cell.drag(
                Vector(
                    randint(-self.max_str, +self.max_str),
                    randint(-self.max_str, +self.max_str),
                    randint(-self.max_str, +self.max_str)
                )
            )
