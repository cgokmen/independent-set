# coding=utf-8
import threading

import numpy as np
import os
import time
import imageio
import errno
import gizeh
import cairocffi as cairo

axial_to_pixel_mat = np.array([[1, 0], [0, 1]])

EMPTY_POSITION_RADIUS = 3
EMPTY_POSITION_COLOR = (0.75, 0.75, 0.75)

# Circles in 24x24 bounding boxes
LONG_EDGE = 18
SHORT_EDGE = 14

EVEN_COLOR = (1, 0, 0)
ODD_COLOR = (0, 1, 0)

# Circles 24 apart
CIRCLE_DIST = 24

# Circle stroke size
STROKE_COLOR = (0, 0, 0)
CIRCLE_STROKE = 2

# Edges 4px wide
EDGE_WIDTH = 4

# Text size as a multiple of the screen height
TEXT_FACTOR = 100.0

BORDER_COLOR = (0.1, 0.1, 0.1)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class PDFS(object):
    """Simple class to allow gizeh to create pdf figures"""

    def __init__(self, name, width, height):
        self.width = width
        self.height = height
        self._cairo_surface = cairo.PDFSurface(name, width, height)

    def get_new_context(self):
        """ Returns a new context for drawing on the surface."""
        return cairo.Context(self._cairo_surface)

    def flush(self):
        """Write the file"""
        self._cairo_surface.flush()

    def finish(self):
        """Close the surface"""
        self._cairo_surface.finish()


class VectorPlotter(object):
    def __init__(self, compression_simulator, path=None):
        self.compression_simulator = compression_simulator

        self.min_pos = axial_to_pixel_mat.dot(compression_simulator.grid.min - np.array([1, 1])) * CIRCLE_DIST
        self.max_pos = axial_to_pixel_mat.dot(compression_simulator.grid.max + np.array([1, 1])) * CIRCLE_DIST

        self.size = (self.max_pos - self.min_pos).astype(int)
        self.center = self.size / 2

        if path is None:
            path = os.path.join("output", type(self.compression_simulator).__name__, str(int(time.time())))

        if callable(path):
            self.path = path()
        else:
            self.path = path
        mkdir_p(self.path)

        self.closed = False

    def get_position_from_axial(self, axial_coordinates):
        return axial_to_pixel_mat.dot(axial_coordinates) * CIRCLE_DIST + self.center

    def draw_plot(self, path):
        if self.closed:
            raise ValueError("This plotter has been closed.")

        surface = PDFS(name=path, width=self.size[0], height=self.size[1])

        # Here we populate the isometric grid
        for x in xrange(self.compression_simulator.grid.min[0] + 1,
                        self.compression_simulator.grid.max[0]):
            for y in xrange(self.compression_simulator.grid.min[1] + 1,
                            self.compression_simulator.grid.max[1]):
                axial_position = np.array([x, y])

                position = self.get_position_from_axial(axial_position)
                circle = gizeh.circle(r=EMPTY_POSITION_RADIUS, xy=position, fill=EMPTY_POSITION_COLOR)
                circle.draw(surface)

        boundary_positions = [tuple(self.get_position_from_axial(e)) for e in self.compression_simulator.grid.extrema]
        boundary_positions.append(boundary_positions[0])

        boundary = gizeh.polyline(points=boundary_positions, stroke_width=EDGE_WIDTH, stroke=BORDER_COLOR)
        boundary.draw(surface)

        drawn_particles = {}

        # This part draws the particles & their links
        for particle in self.compression_simulator.grid.get_all_particles():
            position = tuple(self.get_position_from_axial(particle.axial_coordinates))

            is_even = (sum(particle.axial_coordinates) % 2 == 0)
            width = LONG_EDGE if is_even else SHORT_EDGE
            height = SHORT_EDGE if is_even else LONG_EDGE
            color = EVEN_COLOR if is_even else ODD_COLOR

            vertices = [
                (position[0] - width, position[1]),
                (position[0], position[1] + height),
                (position[0] + width, position[1]),
                (position[0], position[1] - height),
                (position[0] - width, position[1])
            ]

            particle = gizeh.polyline(points=vertices, stroke_width=CIRCLE_STROKE, stroke=STROKE_COLOR, fill=color)
            particle.draw(surface)

            #gizeh.text("%d" % self.compression_simulator.grid.neighbor_count(particle.axial_coordinates), fontfamily="Impact", fontsize=CIRCLE_RADIUS,
            #           fill=(1, 1, 1), xy=tuple_position).draw(surface)

            drawn_particles[particle] = True

        # start = self.get_position_from_axial(self.compression_simulator.grid.max)
        # start = np.array([self.size[0] - start[0], start[1]])
        # shift = (np.array([0, self.size[1]]) * 1.1 / TEXT_FACTOR).astype(int)
        #
        # metrics = self.compression_simulator.get_metrics()
        # metric_count = len(metrics)
        # for key in xrange(metric_count):
        #     metric = metrics[key]
        #     metrictext = metric[0] + ": " + (metric[1] % metric[2])
        #     draw.text(tuple(start - shift * (metric_count - key)), metrictext, (0, 0, 0), self.font)
        #
        # start = self.get_position_from_axial(self.compression_simulator.grid.min)
        # start = np.array([self.size[0] - start[0], start[1]])
        # text = "Algorithm: %s" % type(self.compression_simulator).__name__
        # w, h = draw.textsize(text, self.font)
        # draw.text(start - np.array([w, 0]), text, (0, 0, 0), self.font)
        #
        # start += shift
        # text = "Start time: %s" % self.compression_simulator.start_time
        # w, h = draw.textsize(text, self.font)
        # draw.text(start - np.array([w, 0]), text, (0, 0, 0), self.font)

        return surface

    def plot(self, filename):
        plt = self.draw_plot(os.path.join(self.path, filename))
        plt.flush()
        plt.finish()

    def close(self):
        self.closed = True
