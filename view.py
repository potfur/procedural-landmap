from PIL import Image, ImageDraw

from grid import Cell


class View:
    __BACKGROUND = (0, 0, 0, 0)
    __CENTER = (255, 128, 128)
    __POLYGON = (160, 160, 160)
    __OUTLINE = (128, 0, 0)

    def __init__(self, width: int, height: int) -> None:
        self.__image = Image.new('RGBA', (width, height), self.__BACKGROUND)
        self.__draw = ImageDraw.Draw(self.__image)

    def cell(self, cell: Cell) -> None:
        self.__draw.polygon(
            [point.pos() for point in cell.points],
            fill=tuple([c + (cell.center.z * 2) for c in self.__POLYGON]),
            outline=self.__OUTLINE
        )
        self.__draw.point(
            cell.center.pos(),
            fill=self.__CENTER
        )

        for connection in cell.connections:
            self.__draw.line(
                [cell.center.pos(), connection.center.pos()],
                fill=self.__CENTER,
                width=1
            )

    def save(self, name: str) -> None:
        with open(name, 'w') as f:
            self.__image.save(name, 'PNG')
