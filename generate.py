from grid import Grid
from shake.random import RandomDrag, RandomNoise
from shake.seed import Seed, SeedDrag, SeedNoise
from view import View

grid = Grid(50, 50, 10)
# grid.apply(RandomNoise(5))
# grid.apply(RandomDrag(5))

# seed = Seed('1357943016922984648920275620')
# grid.apply(SeedNoise(seed))
# grid.apply(SeedDrag(seed))

view = View(grid.width, grid.height)
for cell in grid.cells:
    view.cell(cell)
view.save('tmp.png')
