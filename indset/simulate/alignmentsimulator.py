# coding=utf-8
import datetime
import random

from . import Directions


class AlignmentSimulator(object):
    def __init__(self, grid, bias):
        self.validate_grid(grid)

        self.grid = grid
        self.bias = float(bias)
        self.start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.rounds = 0
        self.movements = 0
        self.visited = {}

        self.iterations_run = 0

        self.probability_series = []

    @staticmethod
    def validate_grid(grid):
        for particle in grid.get_all_particles():
            if grid.neighbor_count(particle.axial_coordinates) != 0:
                raise ValueError("AlignmentSimulator conditions not met: particles cannot be adjacent.")

    def run_iterations(self, iterations, classes_to_move=None):
        particles = list(self.grid.get_all_particles(classes_to_move))
        directions = Directions.ALL

        moves_made = 0
        for n in xrange(iterations):
            if self.move(random.choice(particles), random.choice(directions), random.random()):
                moves_made += 1
            self.iterations_run += 1

        return moves_made

    def get_bias(self, particle):
        return self.bias

    def get_move_probability(self, particle, current_location, new_location):
        current_neighbors = self.grid.second_degree_neighbor_count(current_location)
        new_neighbors = self.grid.second_degree_neighbor_count(new_location)

        return self.get_bias(particle) ** (new_neighbors - current_neighbors)

    def move(self, random_particle, random_direction, probability, classes_to_move=None):
        # Check if new location is empty
        current_location = random_particle.axial_coordinates
        new_location = self.grid.get_position_in_direction(current_location, random_direction)

        if not self.grid.is_position_in_bounds(new_location):
            # New location out of board bounds
            # print("Bounds")
            return False

        if self.grid.get_particle(new_location) is not None:
            # There already is a particle at this new position
            # print("Existing", current_location, random_direction, new_location)
            return False

        if not self.valid_move(random_particle, current_location, new_location,
                               random_direction):  # TODO: Check classes to move?
            # print("Invalid")
            return False

        prob_move = self.get_move_probability(random_particle, current_location, new_location)
        # print("Prob: " + str(prob_move))
        self.probability_series.append(prob_move)

        if not probability < prob_move:  # Choose with probability
            # print probability
            return False

        self.grid.move_particle(current_location, new_location)

        # Movement counting
        self.movements += 1

        # Round checking
        self.visited[random_particle] = True
        for particle in self.grid.get_all_particles(classes_to_move):
            if not self.visited.get(particle, False):
                return True

        # If this point is reached, a round has completed
        self.rounds += 1
        self.visited = {}

        return True

    def valid_move(self, particle, old_position, new_position, direction):
        # Check if the new position has any existing neighbors other than this one
        nbr_cnt = self.grid.neighbor_count(new_position)

        if nbr_cnt < 1:
            return ValueError("How can a particle not be in the neighborhood of its own neighbor?")

        elif nbr_cnt > 1:
            return False

        return True

    def get_metrics(self, classes_to_move=None):
        metrics = [("Bias", "%.2f", self.bias),
                   ("Iterations", "%d", self.iterations_run),
                   ("Movements made", "%d", self.movements),
                   ("Rounds completed:", "%d", self.rounds),
                   #("Perimeter", "%d", self.grid.calculate_perimeter(classes_to_move)),
                   #("Center of mass", "x = %.2f, y = %.2f", tuple(self.grid.find_center_of_mass(classes_to_move)))
        ]

        return metrics
