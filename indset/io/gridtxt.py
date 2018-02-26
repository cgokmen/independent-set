# coding=utf-8

from indset.simulate import Grid, Particle


def alignment_simulator_grid_loader(filename, particle_types=(Particle,)):
    f = open(filename, "r")

    size = tuple(map(int, f.readline().split()))
    grid = Grid(size)

    if sum(s % 2 for s in size) > 0:
        raise ValueError("Width and height need to be even.")

    num_particles = int(f.readline())

    for n in range(num_particles):
        entry = map(int, f.readline().split())

        position = (entry[0], entry[1])
        ptype = 0 if len(entry) < 3 else entry[2]

        particle = particle_types[ptype](position, n)

        grid.add_particle(particle)

    # print("Loaded %s successfully" % filename)

    return grid


def alignment_simulator_grid_saver(filename, grid):
    with open(filename, 'w') as f:
        particles = list(grid.get_all_particles())

        f.write("%d %d\n" % tuple(grid.size))
        f.write("%d\n" % len(particles))

        for particle in particles:
            coords = particle.axial_coordinates

            f.write("%d %d\n" % (coords[0], coords[1]))
