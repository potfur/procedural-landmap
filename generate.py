from random import randint

from grid import Grid, Vector
from view import View

grid = Grid(5, 5, 40)

grid.drag(
    grid.points[1],
    Vector(
        randint(-10, 10),
        randint(-10, 10),
        randint(-10, 10),
    )
)

view = View(grid.width, grid.height)
for point in grid.points:
    view.connect(point)

for point in grid.points:
    view.point(point, 1)
    view.text(point, str(point.z))

view.save('tmp.png')
