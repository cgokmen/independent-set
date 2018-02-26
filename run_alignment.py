import numpy as np
import os
import itertools
import threading

from indset.simulate import AlignmentSimulator
from indset.plot import RasterPlotter, VectorPlotter
from indset.io import alignment_simulator_grid_loader, alignment_simulator_grid_saver, MetricsIO

thread = False

def run_simulation(input_file, root_dir, c, model_name):
    grid = alignment_simulator_grid_loader(input_file)
    sim = AlignmentSimulator(grid, c)

    sim_name = "lambda-%.2f" % sim.bias

    print "Starting new simulation: %s. %d simulations currently running." % (sim_name, threading.activeCount() - 1)
    total_iterations = 100000000
    i = 0
    unit_iterations = 10000000
    plot_iterations = 1 * unit_iterations

    path = os.path.join(root_dir, model_name, sim_name)

    plotter = VectorPlotter(sim, path)

    plotter.plot("%d.pdf" % i)

    if True:
        while i < total_iterations:
            sim.run_iterations(unit_iterations)
            i += unit_iterations
            print "%s: %d iterations run" % (sim_name, i)

            if i % plot_iterations == 0:
                plotter.plot("%d.pdf" % i)
                #alignment_simulator_grid_saver(os.path.join(path, "%d.txt" % i), grid)

    plotter.close()

    print "Simulation completed: %s. %d simulations still running." % (sim_name, threading.activeCount() - 1)

if __name__ == "__main__":
    input_dir = "input/alignment/generated/"
    root_dir = "output/alignment/2-25/"

    input_files = ["300particles.txt"]

    for f in input_files:
        input_file = os.path.join(input_dir, f)
        model_name = os.path.splitext(os.path.basename(input_file))[0]

        alignment_constants = {20}

        print "Now starting model %s" % model_name

        for c in alignment_constants:
            if thread:
                    threading.Thread(target=run_simulation, args=(input_file, root_dir, c, model_name)).start()
            else:
                    run_simulation(input_file, root_dir, c, model_name)

        print "Successfully completed model %s" % model_name
