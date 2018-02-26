# coding=utf-8
import numpy as np
import random
import itertools

from indset.simulate import Grid, Particle, AlignmentSimulator


def generate_random_grid(n_particles, simulator_type, weighted_particle_types, size=None):
    # weighted particle types is a list of particle types in (single-param initializer, weight) format

    if n_particles <= 0:
        raise ValueError("At least 1 particle needs to be generated.")

    if size is None:
        width_height = int(n_particles ** 0.5) * 4
        size = (width_height, width_height)

    grid = Grid(size)
    print "Initialized a grid of size %d, %d" % size

    total_weight = float(sum(wp[1] for wp in weighted_particle_types))

    # Choose the classes for our particles:
    particle_types = list(np.random.choice([wt[0] for wt in weighted_particle_types], n_particles, True,
                                           [wt[1] / total_weight for wt in weighted_particle_types]))

    # Make a list of valid positions:
    valid_x = xrange(grid.min[0], grid.max[0] + 1)
    valid_y = xrange(grid.min[0], grid.max[0] + 1)
    valid_positions = [x for x in itertools.product(valid_x, valid_y) if grid.is_position_in_bounds(x)]

    i = 0
    for particle_type in particle_types:
        while True:
            # Choose a random position for the particle
            coords = random.choice(list(valid_positions))

            if grid.get_particle(coords) is not None:
                continue

            particle = particle_type(coords, i)

            grid.add_particle(particle)

            try:
                simulator_type.validate_grid(grid)
            except ValueError:
                grid.remove_particle(particle)
                continue

            print "Successfully inserted %s #%d" % (type(particle).__name__, i)
            i += 1
            break

    print "Random grid generation successful"
    return grid


def generate_random_alignment_grid(n_particles, size=None, simulator_type=AlignmentSimulator, base_class=Particle):
    classes = [(base_class, 1)]

    return generate_random_grid(n_particles, simulator_type, classes, size)
