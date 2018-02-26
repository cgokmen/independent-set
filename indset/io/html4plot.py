# coding=utf-8
import os
from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader('indset.io', 'templates'))
template = env.get_template('template.html')


class ResultSet(object):
    def __init__(self, title, lambdas, alphas, rules, url_root, last_iteration, animated):
        self.title = title

        self.lambdas = ["%.2f" % x for x in sorted(list(lambdas))]
        self.alphas = ["%.2f" % x for x in sorted(list(alphas))]
        self.rules = list(rules)

        self.url_root = url_root
        self.last_iteration = last_iteration

        self.animated = animated

        folder = "lambda-%s--alpha-%s" % (self.lambdas[0], self.alphas[0])
        self.original = os.path.join(self.rules[0], folder, "0.jpg")

    def get(self, lambd, alpha, rule):
        folder = "lambda-%s--alpha-%s" % (lambd, alpha)
        directory = os.path.join(rule, folder)

        filename = "animation.gif" if self.animated else "%d.jpg" % self.last_iteration
        return os.path.join(directory, filename)


def render_html(result_set, fn):
    output = template.render(results=result_set)
    with open(os.path.join(result_set.url_root, "%s.html" % fn), "wb") as fh:
        fh.write(output)


if __name__ == "__main__":
    # Produce our resultset for the interclass one now
    lambdas = [1.0, 4.0]
    alphas = [0.25, 4.0]
    rules = [""]

    t = "NewSeparationSimulator-3-spread-smallf"
    url_root = "/Users/cgokmen/research/CompressionSimulator/output/NewSeparationSimulator/1-12-with-swaps/3-spread-smallf/"
    last_iteration = 5000000

    result_set = ResultSet(title, lambdas, alphas, rules, url_root, last_iteration, False)
    render_html(result_set, "static")

    result_set2 = ResultSet(title, lambdas, alphas, rules, url_root, last_iteration, True)
    render_html(result_set2, "animated")
