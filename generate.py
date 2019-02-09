from grid import Grid, Vector
from shake.random import RandomDrag, RandomNoise
from shake.seed import Seed, SeedDrag, SeedNoise
from view import View

grid = Grid(5, 10, 40)
grid.cells[22].drag(Vector(0, 0, +50))

# grid.apply(RandomNoise(5))
# grid.apply(RandomDrag(5))

# seed = Seed('1357943016922984648920275620')
# grid.apply(SeedNoise(seed))
# grid.apply(SeedDrag(seed))

view = View(grid.width, grid.height)
for cell in grid.cells:
    view.cell(cell)

for cell in grid.cells:
    view.text(cell.center, str(cell.center.z))
    for point in cell.points:
        view.text(point, str(point.z))

view.save('tmp.png')
