from PIL import Image, ImageDraw

from grid import Point


class View:
    __BACKGROUND = (128, 128, 128, 255)
    __POINT = (255, 128, 128)
    __CONNECTION = (160, 160, 160)
    __DEBUG = (0, 0, 255)

    def __init__(self, width: int, height: int) -> None:
        self.__image = Image.new('RGBA', (width, height), self.__BACKGROUND)
        self.__draw = ImageDraw.Draw(self.__image)

    def point(self, point: Point, radius: int = 0) -> None:
        pos = point.pos()

        self.__draw.ellipse(
            (
                pos[0] - radius,
                pos[1] - radius,
                pos[0] + radius,
                pos[1] + radius
            ),
            fill=self.__POINT
        )

    def connect(self, point: Point) -> None:
        for connection in point.connections:
            self.__draw.line(
                [point.pos(), connection.pos()],
                fill=self.__CONNECTION,
                width=1
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
