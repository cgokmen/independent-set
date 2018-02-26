import os

from indset.simulate import AlignmentSimulator
from indset.generate import generate_random_alignment_grid
from indset.io import alignment_simulator_grid_saver

grid = generate_random_alignment_grid(300, size=(30, 30), simulator_type=AlignmentSimulator)

in_dir = "input/alignment/generated/"
grid_name = "300particles"
alignment_simulator_grid_saver(os.path.join(in_dir, grid_name + ".txt"), grid)
