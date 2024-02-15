import openpyxl
import openpyxl.chart
import glob
import collections
import pathlib
import matplotlib.pyplot as pyplot
import re
import argparse
import sys
import numpy
import scipy
import scipy.stats

from typing import *

import warnings

PROGRAM_NAME = pathlib.Path(sys.argv[0]).parts[-1][:-4]
DESCRIPTION = "Graph a r-loop grammar prediction."

parser = argparse.ArgumentParser(prog=PROGRAM_NAME, description=DESCRIPTION)
parser.add_argument("prediction_folder")
parser.add_argument("-n", "--name", type=str, default=None)


def get_average_probabilities(folder):
    subfolders = [f for f in pathlib.Path(folder).iterdir() if f.is_dir()]
    files = []

    for subfolder in subfolders:
        files.extend(glob.glob(f"{subfolder}/*base_in_loop.xlsx"))

    average_probabilities_list = None

    for file in files:
        wb = openpyxl.load_workbook(file)
        ws = wb.active

        m = re.match(r"^.*_w\d_(\d*)_", str(file))
        run_number = 0

        row_value_iter = iter(ws.values)
        next(row_value_iter)  # Skip the column header

        probabilities = collections.defaultdict(lambda: 0)
        for row in row_value_iter:
            base_position, probability = row
            base_position = int(base_position)
            probability = float(probability)

            probabilities[base_position] = probabilities[base_position] + probability

        probabilities_list = [
            probabilities[k] for k in range(1, len(probabilities.keys()) + 1)
        ]

        if not average_probabilities_list:
            average_probabilities_list = [
                list() for i in range(len(probabilities_list))
            ]
        else:
            for i in range(len(average_probabilities_list)):
                average_probabilities_list[i].append(probabilities_list[i])

    return [numpy.mean(p) for p in average_probabilities_list], [
        (numpy.mean(p) + scipy.stats.sem(p), numpy.mean(p) - scipy.stats.sem(p))
        for p in average_probabilities_list
    ]


def aggregate_graph(name, prediction_folder, axis) -> None:
    prediction_probabilities_avg, prediction_intervals = get_average_probabilities(
        prediction_folder
    )

    axis.plot(
        list(range(1, len(prediction_probabilities_avg) + 1)),
        prediction_probabilities_avg,
        color="deeppink",
        label=f"R-loop grammar",
    )

    axis.fill_between(
        list(range(1, len(prediction_probabilities_avg) + 1)),
        [interval[0] for interval in prediction_intervals],
        [interval[1] for interval in prediction_intervals],
        color="hotpink",
        alpha=0.5,
    )

    axis.tick_params(axis="both", which="major", labelsize=18)
    axis.tick_params(axis="both", which="minor", labelsize=18)

    padding = 13
    width = 4

    def draw_arrow(ax, connectionstyle):
        x1, y1 = len(prediction_probabilities_avg) * 0.1, 0.4
        x2, y2 = 0, 0

        ax.annotate(
            "",
            xy=(x1, y1),
            xycoords="data",
            xytext=(x2, y2),
            textcoords="data",
            arrowprops=dict(
                arrowstyle="->",
                color="black",
                shrinkA=5,
                shrinkB=5,
                patchA=None,
                patchB=None,
                connectionstyle=connectionstyle,
            ),
        )

    draw_arrow(axis, "angle,angleA=90,angleB=180,rad=0")

    axis.legend(fontsize=18)

    axis.set_title(
        f"R-loop prediction in {name}",
        fontsize=18,
    )

    axis.set_xlabel("Nucleotide position in gene", fontsize=18)
    axis.set_ylabel("Probability", fontsize=18)

    axis.set_ylim(0, 1.0)


def main():
    pyplot.rcParams["font.family"] = "Times New Roman"

    args = parser.parse_args()

    prediction_folder = args.prediction_folder
    name = prediction_folder if not args.name else args.name

    fig, axis = pyplot.subplots()

    aggregate_graph(
        name,
        prediction_folder,
        axis,
    )

    pyplot.subplots_adjust(bottom=0.15)
    fig.savefig(f"{name}.pdf")


if __name__ == "__main__":
    main()
