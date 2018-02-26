# coding=utf-8
import csv


class MetricsIO(object):
    def __init__(self, compression_simulator, filename):
        self.compression_simulator = compression_simulator
        self.file = open(filename, "wb")
        self.csv_writer = csv.writer(self.file, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)

        # Write the metric header:
        metrics = self.compression_simulator.get_metrics()
        self.csv_writer.writerow(["Iterations"] + [metric[0] for metric in metrics])

    def save_metric(self):
        metrics = self.compression_simulator.get_metrics()
        self.csv_writer.writerow(
            [self.compression_simulator.iterations_run] + [metric[1] % metric[2] for metric in metrics])

    def close(self):
        self.file.close()
