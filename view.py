from PIL import Image, ImageDraw

from grid import Cell, Point


class View:
    __BACKGROUND = (0, 0, 0, 0)
    __CENTER = (255, 128, 128)
    __POLYGON = (160, 160, 160)
    __OUTLINE = (128, 0, 0)
    __DEBUG = (0, 0, 255)

    def __init__(self, width: int, height: int) -> None:
        self.__image = Image.new('RGBA', (width, height), self.__BACKGROUND)
        self.__draw = ImageDraw.Draw(self.__image)

    def cell(self, cell: Cell) -> None:
        self.__draw.polygon(
            [point.pos() for point in cell.points],
            fill=tuple([c + cell.center.z for c in self.__POLYGON]),
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

    def point(self, point: Point, radius: int = 1) -> None:
        pos = point.pos()
        self.__draw.ellipse(
            (
                pos[0] - radius,
                pos[1] - radius,
                pos[0] + radius,
                pos[1] + radius
            ),
            fill=self.__DEBUG
        )

    def text(self, point: Point, text: str) -> None:
        self.__draw.text(
            point.pos(),
            text,
            fill=self.__DEBUG
        )

    def save(self, name: str) -> None:
        with open(name, 'w') as f:
            self.__image.save(name, 'PNG')
