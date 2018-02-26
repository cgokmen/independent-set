# coding=utf-8
import threading

import numpy as np
import os
import time
import imageio
import errno
from PIL import Image, ImageDraw, ImageFont

axial_to_pixel_mat = np.array([[1, 0], [0, 1]])

# Circles in 24x24 bounding boxes
CIRCLE_BOUNDING = np.array([24, 24])

# Circles 24 apart
CIRCLE_DIST = 24

# Edges 4px wide
EDGE_WIDTH = 4

# Text size as a multiple of the screen height
TEXT_FACTOR = 100.0


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def save_plt(plot, filename):
    plot.save(filename)
    plot.close()


class RasterPlotter(object):
    def __init__(self, compression_simulator, path=None, gif_path=None):
        self.compression_simulator = compression_simulator

        self.min_pos = axial_to_pixel_mat.dot(compression_simulator.grid.min - np.array([1, 1])) * CIRCLE_DIST
        self.max_pos = axial_to_pixel_mat.dot(compression_simulator.grid.max + np.array([1, 1])) * CIRCLE_DIST

        self.size = (self.max_pos - self.min_pos).astype(int)
        self.center = self.size / 2
        # self.font = FONT
        self.font = ImageFont.truetype(os.path.join(os.path.dirname(os.path.realpath(__file__)), "cmunorm.ttf"),
                                       int(self.size[1] / TEXT_FACTOR))

        if path is None:
            path = os.path.join("output", type(self.compression_simulator).__name__, str(int(time.time())))

        if gif_path is None:
            gif_path = os.path.join(path, "result.gif")

        if callable(path):
            self.path = path()
        else:
            self.path = path
        mkdir_p(self.path)

        self.gif_path = gif_path
        self.gif_writer = imageio.get_writer(self.gif_path, mode="I", duration=0.5)

        self.closed = False

    def get_position_from_axial(self, axial_coordinates):
        return axial_to_pixel_mat.dot(axial_coordinates) * CIRCLE_DIST + self.center

    def draw_plot(self):
        if self.closed:
            raise ValueError("This plotter has been closed.")

        plt = Image.new('RGB', tuple(self.size), (255, 255, 255))

        draw = ImageDraw.Draw(plt)

        drawn_hexagons = {}

        for key in xrange(len(self.compression_simulator.grid.extrema)):
            extremum = self.compression_simulator.grid.extrema[key]
            pos = self.get_position_from_axial(extremum)
            draw.ellipse([tuple(pos - (CIRCLE_BOUNDING / 2)), tuple(pos + (CIRCLE_BOUNDING / 2))], (255, 0, 0))

            neighbor_extremum = self.compression_simulator.grid.extrema[key - 1]
            neighbor_pos = self.get_position_from_axial(neighbor_extremum)
            draw.line([tuple(pos), tuple(neighbor_pos)], (255, 0, 0), EDGE_WIDTH)

        if True:
            # This part draws the particles & their links
            for particle in self.compression_simulator.grid.get_all_particles():
                position = self.get_position_from_axial(particle.axial_coordinates)

                # Draw lines to neighbors
                neighbors_positions = [self.get_position_from_axial(neighbor.axial_coordinates) for neighbor in
                                       self.compression_simulator.grid.get_neighbors(particle.axial_coordinates) if
                                       neighbor not in drawn_hexagons]

                tuple_position = tuple(position)

                for neighbor_position in neighbors_positions:
                    draw.line([tuple_position, tuple(neighbor_position)], (100, 100, 100), EDGE_WIDTH)

                draw.ellipse([tuple(position - (CIRCLE_BOUNDING / 2)), tuple(position + (CIRCLE_BOUNDING / 2))],
                             particle.get_color())
                # draw.text(tuple(position), "%.2f" % particle.bias if hasattr(particle, "bias") else "N/A", (0,0,0), self.font)

                drawn_hexagons[particle] = True

        start = self.get_position_from_axial(self.compression_simulator.grid.max)
        start = np.array([self.size[0] - start[0], start[1]])
        shift = (np.array([0, self.size[1]]) * 1.1 / TEXT_FACTOR).astype(int)

        metrics = self.compression_simulator.get_metrics()
        metric_count = len(metrics)
        for key in xrange(metric_count):
            metric = metrics[key]
            metrictext = metric[0] + ": " + (metric[1] % metric[2])
            draw.text(tuple(start - shift * (metric_count - key)), metrictext, (0, 0, 0), self.font)

        start = self.get_position_from_axial(self.compression_simulator.grid.min)
        start = np.array([self.size[0] - start[0], start[1]])
        text = "Algorithm: %s" % type(self.compression_simulator).__name__
        w, h = draw.textsize(text, self.font)
        draw.text(start - np.array([w, 0]), text, (0, 0, 0), self.font)

        start += shift
        text = "Start time: %s" % self.compression_simulator.start_time
        w, h = draw.textsize(text, self.font)
        draw.text(start - np.array([w, 0]), text, (0, 0, 0), self.font)

        return plt

    def plot(self, filename):
        plt = self.draw_plot()
        self.gif_writer.append_data(np.array(plt))

        # threading.Thread(target=save_plt, args=(plt, os.path.join(self.path, filename))).start()
        save_plt(plt, os.path.join(self.path, filename))

    def close(self):
        plt = self.draw_plot()

        for x in xrange(9):
            self.gif_writer.append_data(np.array(plt))

        self.gif_writer.close()
        self.closed = True

        # imageio.mimsave(self.gif_path, [np.asarray(x) for x in self.gif_writer], duration=0.5)
        # for img in self.gif_writer:
        #    img.close()
