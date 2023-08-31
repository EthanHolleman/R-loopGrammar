import openpyxl
import openpyxl.chart
import glob
import collections
import pathlib
import matplotlib.pyplot as pyplot
import re
import math
import statistics
import numpy
import json
import numpy as np

import scipy.stats

from typing import *

import warnings

# ignore warnings about transparency with eps file
warnings.filterwarnings("ignore")


def normalize_data(exp, pred):
    area_under_exp = numpy.trapz(exp)
    area_under_pred = numpy.trapz(pred)

    data = list(map(lambda x: x * (area_under_pred / area_under_exp), exp))

    return list(data)


def calculate_pearsonr(exp, pred):
    return scipy.stats.pearsonr(exp, pred).statistic


def calculate_rsquared(exp: List[float], pred: List[float]):
    assert len(exp) == len(pred)

    mean = statistics.mean(exp)

    sum_of_squares_residuals = sum(((x[0] - x[1]) ** 2 for x in zip(exp, pred)))
    sum_of_squares_total = sum(((x - mean) ** 2 for x in exp))

    return 1 - (sum_of_squares_residuals / sum_of_squares_total)


def calculate_rmsd(exp: List[float], pred: List[float]):
    assert len(exp) == len(pred)

    return math.sqrt(calculate_mse(exp, pred))


def calculate_mse(exp: List[float], pred: List[float]):
    assert len(exp) == len(pred), f"exp({len(exp)}) != pred({len(pred)})"

    mse = statistics.mean(((x[0] - x[1]) ** 2 for x in zip(exp, pred)))

    return mse


def graph_rlooper_full_seq(axis, plasmid_type, plasmid, expected, normalize=False):
    filename = pathlib.Path("rlooper_results") / RLOOPER_FILE_FULL_SEQ_MAP.get(
        (plasmid, plasmid_type), None
    )
    if filename:
        with open(filename) as rlooper_probability_file:
            lines = rlooper_probability_file.readlines()
            lines = list(
                map(float, lines[4:])
            )  # Remove metadata and parse all as floats
            gene_region_probability = (
                lines[0:1749] if plasmid == "pFC53" else lines[0:1432]
            )

            if normalize:
                gene_region_probability = normalize_data(
                    gene_region_probability, expected
                )

            """
            axis.plot(
                list(range(1, len(gene_region_probability) + 1)),
                gene_region_probability,
                label="R-looper (full)",
                color="tan",
            )
            """

            mse = calculate_mse(expected, gene_region_probability)
            rmsd = calculate_rmsd(expected, gene_region_probability)
            rsquared = calculate_rsquared(expected, gene_region_probability)
            kstest = scipy.stats.ks_2samp(expected, gene_region_probability)
            pearsonr = calculate_pearsonr(expected, gene_region_probability)

            return dict(rmsd=rmsd, pearsonr=pearsonr)


def graph_rlooper_gene(axis, plasmid_type, plasmid, expected, normalize=False):
    filename = pathlib.Path("rlooper_results") / RLOOPER_FILE_GENE_MAP.get(
        (plasmid, plasmid_type), None
    )
    if filename:
        with open(filename) as rlooper_probability_file:
            lines = rlooper_probability_file.readlines()
            lines = list(
                map(float, lines[4:])
            )  # Remove metadata and parse all as floats
            gene_region_probability = lines

            print("graph_rlooper_gene", plasmid_type, plasmid)
            print(len(lines), len(expected))

            if normalize:
                gene_region_probability = normalize_data(
                    gene_region_probability, expected
                )

            """
            axis.plot(
                list(range(1, len(gene_region_probability) + 1)),
                gene_region_probability,
                label="R-looper (gene)",
                color="tab:orange",
            )
            """

            mse = calculate_mse(expected, gene_region_probability)
            rmsd = calculate_rmsd(expected, gene_region_probability)
            rsquared = calculate_rsquared(expected, gene_region_probability)
            kstest = scipy.stats.ks_2samp(expected, gene_region_probability)
            pearsonr = calculate_pearsonr(expected, gene_region_probability)

            return dict(rmsd=rmsd, pearsonr=pearsonr)


REPLACE_PLASMID_TYPE_NAME = {
    "SUPERCOILEDCR": "supercoiled",
    "GYRASECR": "hyper-negatively supercoiled (gyrase)",
    "LINEARIZED": "linear",
}

RLOOPER_FILE_FULL_SEQ_MAP = {
    (
        "pFC53",
        "SUPERCOILEDCR",
    ): "pfc53_supercoiled_full_coding_gene_start_output_bpprob.wig",
    ("pFC53", "GYRASECR"): "pfc53_gyrase_full_coding_gene_start_output_bpprob.wig",
    (
        "pFC53",
        "LINEARIZED",
    ): "pfc53_linearized_full_coding_gene_start_output_bpprob.wig",
    ("pFC8", "GYRASECR"): "pfc8_gyrase_full_coding_gene_start_output_bpprob.wig",
    (
        "pFC8",
        "SUPERCOILEDCR",
    ): "pfc8_supercoiled_full_coding_gene_start_output_bpprob.wig",
    ("pFC8", "LINEARIZED"): "pfc8_linearized_full_coding_gene_start_output_bpprob.wig",
}

RLOOPER_FILE_GENE_MAP = {
    ("pFC53", "GYRASECR"): "pfc53_gene_gyrase_output_bpprob.wig",
    ("pFC53", "SUPERCOILEDCR"): "pfc53_gene_supercoiled_output_bpprob.wig",
    ("pFC53", "LINEARIZED"): "pfc53_gene_linearized_output_bpprob.wig",
    ("pFC8", "GYRASECR"): "pfc8_gene_gyrase_output_bpprob.wig",
    (
        "pFC8",
        "SUPERCOILEDCR",
    ): "pfc8_gene_supercoiled_output_bpprob.wig",
    ("pFC8", "LINEARIZED"): "pfc8_gene_linearized_output_bpprob.wig",
}


def get_experimental(bed_file, gene_location):
    seq_len = sum(gene_location)

    with open(bed_file, "r") as fin:
        lines = fin.readlines()
        rloops = tuple(map(lambda x: tuple(map(int, x.split()[1:3])), lines))

    summary = np.zeros(seq_len)

    for start, end in rloops:
        # switch to right to left
        new_start = seq_len - end
        new_end = seq_len - start

        loop_vector = np.zeros(seq_len)

        # fill in vector with 1's
        for index in range(seq_len):
            if index >= new_start and index < new_end:
                loop_vector[index] = 1

        summary += loop_vector

    probabilities = summary[gene_location[0] : gene_location[1]] / len(rloops)
    intervals = [
        (
            (x / len(rloops) + scipy.stats.sem([0] * (len(rloops) - x) + [1] * x)),
            (x / len(rloops) - scipy.stats.sem([0] * (len(rloops) - x) + [1] * x)),
        )
        for x in map(int, summary[gene_location[0] : gene_location[1]])
    ]

    return probabilities, intervals


def grouped_bar_chart(
    axis,
    all_statistics,
    plasmid_type,
    plasmid,
    graph_statistic: str = "rmsd",
    left_title="RMSD",
):
    groups = []
    model_specific_statistics = {
        "R-looper (full)": [],
        "R-looper (gene)": [],
        "R-loop grammar (deterministic)": [],
        "R-loop grammar (stochastic)": [],
    }

    color_matching = {
        "R-loop grammar (stochastic)": "tab:pink",
        "R-loop grammar (deterministic)": "tab:red",
        "R-looper (full)": "tan",
        "R-looper (gene)": "tab:orange",
    }

    plasmid_type_replaced = REPLACE_PLASMID_TYPE_NAME[plasmid_type]
    groups.append(f"{plasmid} {plasmid_type_replaced}")

    model_specific_statistics["R-loop grammar (deterministic)"].append(
        all_statistics["rloop-grammar-statistics-deterministic"][graph_statistic]
    )
    model_specific_statistics["R-loop grammar (stochastic)"].append(
        all_statistics["rloop-grammar-statistics-stochastic"][graph_statistic]
    )
    model_specific_statistics["R-looper (full)"].append(
        all_statistics["rlooper-full-statistics"][graph_statistic]
    )
    model_specific_statistics["R-looper (gene)"].append(
        all_statistics["rlooper-gene-statistics"][graph_statistic]
    )

    x = numpy.arange(len(groups))
    width = 0.20
    multiplier = 0

    for attribute, measurement in model_specific_statistics.items():
        offset = width * multiplier
        rects = axis.bar(
            x + offset,
            measurement,
            width,
            label=attribute,
            color=color_matching[attribute],
        )
        axis.bar_label(rects, padding=3, fmt="%.4f")
        multiplier += 1

    axis.set_ylabel(left_title)
    axis.set_xlabel(groups[0])
    axis.set_xticks([])
    axis.legend(loc="upper left", fontsize=9)
    axis.set_ylim(0, 1 if graph_statistic == "rmsd" else 2)


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


def graph_correlation(plasmid_type, plasmid, expected, predicted, data_type, index=[3]):
    figure = pyplot.figure(index[0])
    index[0] += 1
    axes = figure.subplots(1)

    axes.scatter(expected, predicted)
    axes.set_xlabel("Expected")
    axes.set_ylabel("Prediction")
    axes.set_title(f"{plasmid_type} {plasmid} {data_type} correlation")
    figure.savefig(f"{plasmid_type}-{plasmid}-{data_type}-correlation.png")
    pyplot.figure(1)


def aggregate_graph(
    plasmid_type,
    plasmid,
    deterministic_folder,
    stochastic_folder,
    axis,
    avg_only: bool = False,
    rlooper: bool = False,
    normalize: bool = False,
) -> None:
    (
        deterministic_probabilities_avg,
        deterministic_intervals,
    ) = get_average_probabilities(deterministic_folder)
    stochastic_probabilities_avg, stochastic_intervals = get_average_probabilities(
        stochastic_folder
    )

    probabilities_list, experimental_intervals = get_experimental(
        f"{plasmid}_{plasmid_type}_training.bed",
        (80, 1512) if plasmid == "pFC8" else (80, 1829),
    )

    if normalize:
        deterministic_probabilities_avg = normalize_data(
            deterministic_probabilities_avg, probabilities_list
        )
        stochastic_probabilities_avg = normalize_data(
            stochastic_probabilities_avg, probabilities_list
        )

    deterministic_mse = calculate_mse(
        probabilities_list, deterministic_probabilities_avg
    )
    deterministic_rmsd = calculate_rmsd(
        probabilities_list, deterministic_probabilities_avg
    )
    deterministic_pearsonr = calculate_pearsonr(
        probabilities_list, deterministic_probabilities_avg
    )

    stochastic_mse = calculate_mse(probabilities_list, stochastic_probabilities_avg)
    stochastic_rmsd = calculate_rmsd(probabilities_list, stochastic_probabilities_avg)
    stochastic_pearsonr = calculate_pearsonr(
        probabilities_list, stochastic_probabilities_avg
    )

    axis.plot(
        list(range(1, len(probabilities_list) + 1)),
        probabilities_list,
        "--",
        color="tab:blue",
        label=f"Experimental",
    )

    """
    axis.fill_between(
        list(range(1, len(probabilities_list) + 1)),
        [interval[0] for interval in experimental_intervals],
        [interval[1] for interval in experimental_intervals],
        color="tab:blue",
        alpha=0.5,
    )
    """

    rlooper_full_dict = None
    if rlooper:
        rlooper_full_dict = graph_rlooper_full_seq(
            axis, plasmid_type, plasmid, probabilities_list, normalize=normalize
        )

    rlooper_gene = None
    if rlooper:
        rlooper_gene = graph_rlooper_gene(
            axis, plasmid_type, plasmid, probabilities_list, normalize=normalize
        )

    """
    axis.plot(
        list(range(1, len(deterministic_probabilities_avg) + 1)),
        deterministic_probabilities_avg,
        color="tab:red",
        label=f"R-loop grammar (deterministic)",
    )

    axis.fill_between(
        list(range(1, len(deterministic_probabilities_avg) + 1)),
        [interval[0] for interval in deterministic_intervals],
        [interval[1] for interval in deterministic_intervals],
        color="tab:red",
        alpha=0.5,
    )
    """

    axis.plot(
        list(range(1, len(deterministic_probabilities_avg) + 1)),
        stochastic_probabilities_avg,
        color="tab:pink",
        label=f"R-loop grammar (stochastic)",
    )

    axis.fill_between(
        list(range(1, len(deterministic_probabilities_avg) + 1)),
        [interval[0] for interval in stochastic_intervals],
        [interval[1] for interval in stochastic_intervals],
        color="tab:pink",
        alpha=0.5,
    )

    padding = 13
    width = 4

    def draw_arrow(ax, connectionstyle):
        x1, y1 = len(probabilities_list) * 0.1, 0.4
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

    # pyplot.figtext(0.695, 0.6, f"pFC8 $\cup$ pFC53\n $n={width}$, $p={padding}$")
    axis.legend(title=f"pFC8 $\cup$ pFC53\n $n={width}$, $p={padding}$")

    axis.set_title(
        f"TRAIN R-loop prediction in {REPLACE_PLASMID_TYPE_NAME[plasmid_type]} {plasmid} based on the union of dictionaries",
        fontsize=9 if plasmid_type == "GYRASECR" else 12,
    )

    axis.set_xlabel("Nucleotide position in gene")
    axis.set_ylabel("Probability")

    axis.set_ylim(0, 1.0)

    return {
        "rloop-grammar-statistics-deterministic": dict(
            rmsd=deterministic_rmsd, pearsonr=deterministic_pearsonr
        ),
        "rloop-grammar-statistics-stochastic": dict(
            rmsd=stochastic_rmsd, pearsonr=stochastic_pearsonr
        ),
        "rlooper-full-statistics": rlooper_full_dict,
        "rlooper-gene-statistics": rlooper_gene,
    }


WIDTH = 4

GRAPH_RLOOPER = True
GRAPH_AVG_ONLY = True


def main():
    pyplot.rcParams["font.family"] = "Times New Roman"

    plasmid_types = ["SUPERCOILEDCR", "GYRASECR", "LINEARIZED"]
    plasmids = ["pFC53", "pFC8"]
    paddings = [13]

    all_statistics = {}

    plasmid_type_main_figures = {}
    plasmid_type_right_figure = {}

    for padding in paddings:
        for plasmid_type in plasmid_types:
            fig = pyplot.figure(1, layout="constrained", figsize=(15, 5))
            subfigs = fig.subfigures(1, 2, width_ratios=[6 / 8, 2 / 8])
            left_axes = subfigs[0].subplots(nrows=1, ncols=2, sharey=True)

            plasmid_type_main_figures[plasmid_type] = fig
            plasmid_type_right_figure[plasmid_type] = subfigs[1]

            plasmids = ["pFC53", "pFC8"]
            for plasmid, axis in zip(plasmids, left_axes):
                print(f"{plasmid_type}")
                deterministic_folder = glob.glob(
                    f"deterministic_UnionCollection_{plasmid_type}*on_{plasmid}"
                )[0]

                stochastic_folder = glob.glob(
                    f"stochastic_UnionCollection_{plasmid_type}*on_{plasmid}"
                )[0]

                stats = aggregate_graph(
                    plasmid_type,
                    plasmid,
                    deterministic_folder,
                    stochastic_folder,
                    axis,
                    avg_only=GRAPH_AVG_ONLY,
                    rlooper=GRAPH_RLOOPER,
                    normalize=False,
                )

                all_statistics[f"{plasmid} {plasmid_type}"] = stats

            right_axes = subfigs[1].subplots(2, 1)

            right_axes[0].set_title(
                "RMSD comparison of model predictions",
                fontsize=9,
            )

            for axis, plasmid in zip(right_axes, plasmids):
                grouped_bar_chart(
                    axis,
                    all_statistics[f"{plasmid} {plasmid_type}"],
                    plasmid_type,
                    plasmid,
                    left_title="RMSD",
                    graph_statistic="rmsd",
                )

            fig.savefig(plasmid_type + "_rmsd.png")

    with open("results.json", "w") as results_file:
        results_file.write(
            json.dumps(all_statistics, sort_keys=True, indent=4, separators=(",", ": "))
        )


if __name__ == "__main__":
    main()
