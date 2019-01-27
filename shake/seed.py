from string import digits
from typing import Generator, Dict

from grid import Shake, Point, Cell


class Seed:
    CHARS = digits

    def __init__(self, seed: str) -> None:
        def iterator(seed) -> Generator:
            offset = 0
            while True:
                yield digits.index(seed[offset])
                offset = offset + 1 if offset + 1 < len(seed) else 0

        self.__iterator = iterator(seed)

    def get(self) -> int:
        return self.__iterator.__next__()


class SeedNoise(Shake):

    def __init__(self, seed: Seed) -> None:
        self.__seed = seed

    def apply(self, cells: Dict[Point, Cell]) -> None:
        for cell in cells.values():
            for point in cell.points:
                point.move(
                    self.__get(),
                    self.__get(),
                    0
                )

    def __get(self) -> int:
        return self.__seed.get() // 2 * (-1 if self.__seed.get() % 2 else 1)


class SeedDrag(Shake):

    def __init__(self, seed: Seed) -> None:
        self.__seed = seed

    def apply(self, cells: Dict[Point, Cell]) -> None:
        for cell in cells.values():
            cell.drag(
                self.__get(),
                self.__get(),
                self.__get(),
            )

    def __get(self) -> int:
        return self.__seed.get() // 2 * (-1 if self.__seed.get() % 2 else 1)
