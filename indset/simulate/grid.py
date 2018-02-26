# coding=utf-8
import itertools

from .storage import ListMap, ClassBasedList


class Particle(object):
    COLOR = (0, 0, 0)

    def __init__(self, axial_coordinates, identifier):
        self.axial_coordinates = tuple(int(x) for x in axial_coordinates)
        self.id = identifier

    def get_color(self):
        return Particle.COLOR

    def move(self, new_axial_coordinates):
        self.axial_coordinates = tuple(int(x) for x in new_axial_coordinates)


class Directions(object):
    class Direction(object):
        def __init__(self, number, vector):
            self.number = number
            self.vector = vector

        def axial_vector(self):
            return self.vector

    E = Direction(0, (1, 0))
    N = Direction(1, (0, 1))
    W = Direction(2, (-1, 0))
    S = Direction(3, (0, -1))

    ALL = [E, N, W, S]

    @staticmethod
    def shift_counterclockwise_by(d, by):
        return Directions.ALL[(d.number + by) % 4]


class Grid(object):
    def __init__(self, size):
        self.size = tuple(size)
        self.width = size[0]
        self.height = size[1]

        self.min = tuple(x / -2 for x in self.size)
        self.max = tuple(x / 2 for x in self.size)

        self.extrema = [self.min, (self.min[0], self.max[1]), self.max,
                        (self.max[0], self.min[1])]

        self._map_backend = ListMap(size)

        self._particle_list = ClassBasedList()

    @staticmethod
    def is_position_between_positions(p, min_pos, max_pos):
        return not (p[0] <= min_pos[0] or p[1] <= min_pos[1] or p[0] >= max_pos[0] or p[1] >= max_pos[1])

    def is_position_in_bounds(self, axial_coordinates):
        return Grid.is_position_between_positions(axial_coordinates, self.min, self.max)

    def get_valid_coordinates(self):
        x_range = range(self.min[0], self.max[0] + 1)
        y_range = range(self.min[1], self.max[1] + 1)
        return itertools.product(x_range, y_range)

    def add_particle(self, particle):
        if not isinstance(particle, Particle):
            raise ValueError("Grid only supports subclasses of Particle")

        if particle in self._particle_list:
            raise ValueError("This particle already exists")

        if not self.is_position_in_bounds(particle.axial_coordinates):
            raise ValueError("Coordinates out of bounds")

        if self.get_particle(particle.axial_coordinates) is not None:
            raise ValueError("There already is a particle at the position %d, %d" % particle.axial_coordinates)

        self._map_backend[particle.axial_coordinates] = particle
        self._particle_list.add(particle)

    def move_particle(self, old_position, new_position):
        particle = self.get_particle(old_position)

        if particle is None:
            raise ValueError("No particle to move.")

        existing_particle = self.get_particle(new_position)
        if existing_particle is not None:
            raise ValueError("There is an existing particle at the move destination.")

        if not self.is_position_in_bounds(new_position):
            raise ValueError("Destination is out of bounds.")

        self._map_backend[particle.axial_coordinates] = None
        particle.move(new_position)
        self._map_backend[particle.axial_coordinates] = particle

    def remove_particle(self, particle):
        del self._map_backend[particle.axial_coordinates]
        self._particle_list.remove(particle)

    def get_particle(self, axial_coordinates, classes_to_consider=None):
        particle = self._map_backend[axial_coordinates]

        if particle is None:
            return None

        if classes_to_consider is None or isinstance(particle, classes_to_consider):
            return particle

        return None

    def get_all_particles(self, classes_to_consider=None):
        if classes_to_consider is None:
            return self._particle_list.get_all()

        result = []
        for particle_type, particles in self._particle_list.get_class_list_pairs():
            if issubclass(particle_type, classes_to_consider):
                result += particles

        return result

    def get_all_particles_by_direct_class(self, class_to_consider):
        particles = self._particle_list.get_by_class(class_to_consider)

        return particles

    def particles_connected(self, classes_to_consider=None):
        def has_eligible_particle(position):
            return (self.is_position_in_bounds(position)) and (
                self.get_particle(position, classes_to_consider) is not None)

        return self.check_connected(has_eligible_particle)

    def particle_holes(self, classes_to_consider=None):
        def is_empty(position):
            return (self.is_position_in_bounds(position)) and (
                self.get_particle(position, classes_to_consider) is None)

        return self.check_connected(is_empty)

    def check_connected(self, position_include_fn):
        def bfs(start):
            visited, queue = set(), [start]
            while queue:
                vertex = queue.pop(0)
                if vertex not in visited:
                    visited.add(vertex)

                    # We dont use the neighbor position method here - it doesn't support outside-the-box positions
                    next_set = set(tuple(c) for c in self.get_neighbor_positions(vertex) if position_include_fn(c))
                    queue.extend(next_set - visited)

            return visited

        num_eligible = 0
        start_spot = None

        for axial_coordinates in self.get_valid_coordinates():
            if position_include_fn(axial_coordinates):
                num_eligible += 1
                start_spot = axial_coordinates

        # If no positions match the criteria
        if num_eligible == 0:
            return True

        # Does a breadth-first search reach all eligible particles?
        searched = len(bfs(tuple(start_spot)))
        return searched == num_eligible

    def neighbor_count(self, axial_coordinates, classes_to_consider=None):
        return len(list(self.get_neighbors(axial_coordinates, classes_to_consider)))

    def get_neighbors(self, axial_coordinates, classes_to_consider=None, include_none=False):
        neighbors = (self.get_particle(neighbor_position, classes_to_consider) for neighbor_position in
                     self.get_neighbor_positions(axial_coordinates))

        if not include_none:
            neighbors = (x for x in neighbors if x is not None)

        return neighbors

    def get_second_degree_neighbors(self, axial_coordinates, degree, classes_to_consider=None):
        nbrs = self.get_neighbors(axial_coordinates, classes_to_consider)

        result = set()

        for nbr in nbrs:
            result |= {x for x in self.get_neighbors(nbr.axial_coordinates, classes_to_consider)}

        p = self.get_particle(axial_coordinates, classes_to_consider)
        if p is not None:
            result -= {p}

        return result

    def second_degree_neighbor_count(self, axial_coordinates, degree, classes_to_consider=None):
        return len(self.get_second_degree_neighbors(axial_coordinates, degree, classes_to_consider=None))

    def get_neighbor_in_direction(self, axial_coordinates, direction, classes_to_consider=None):
        return self.get_particle(self.get_position_in_direction(axial_coordinates, direction), classes_to_consider)

    @staticmethod
    def is_neighbor(axial_coordinates, neighbor_axial):
        return ((axial_coordinates[0] - neighbor_axial[0]) ** 2) + (
            (axial_coordinates[0] - neighbor_axial[0]) ** 2) <= 2

    @staticmethod
    def get_position_in_direction(axial_coordinates, direction):
        axial_vector = direction.axial_vector()
        return axial_coordinates[0] + axial_vector[0], axial_coordinates[1] + axial_vector[1]

    def get_neighbor_positions(self, axial_coordinates):
        return (self.get_position_in_direction(axial_coordinates, d) for d in Directions.ALL)

    def find_center_of_mass(self, classes_to_consider=None):
        center_of_mass = (0, 0)
        num_particles = 0

        for particle in self.get_all_particles(classes_to_consider):
            center_of_mass = particle.axial_coordinates
            num_particles += 1

        return center_of_mass if num_particles == 0 else center_of_mass / num_particles

    def count_neighborhoods(self, classes_to_consider=None):
        return sum(self.neighbor_count(p.axial_coordinates, classes_to_consider) for p in
                   self.get_all_particles(classes_to_consider)) / 2

    def count_neighborhoods_between_classes(self, class1, class2):
        particles1 = self.get_all_particles_by_direct_class(class1)

        result = sum(self.neighbor_count(p.axial_coordinates, class2) for p in particles1)

        return result

    def count_heterogeneous_neighborhoods(self, classes_to_consider=None):
        particles = self.get_all_particles(classes_to_consider)
        return sum(
            sum(1 for n in self.get_neighbors(p.axial_coordinates, classes_to_consider) if not isinstance(n, type(p)))
            for p in particles) / 2

    def count_homogeneous_neighborhoods(self, classes_to_consider):
        particles = self.get_all_particles(classes_to_consider=None)
        return sum(
            sum(1 for n in self.get_neighbors(p.axial_coordinates, classes_to_consider) if isinstance(n, type(p))) for p
            in particles) / 2
