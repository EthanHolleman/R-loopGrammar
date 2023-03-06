import openpyxl
import openpyxl.chart
import glob
import collections
import pathlib
import matplotlib.pyplot as pyplot
import re
import os
import math
import statistics
import prettytable

import scipy.stats

from typing import *

import warnings

# ignore warnings about transparency with eps file
warnings.filterwarnings("ignore")


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
    print(len(exp), len(pred))
    assert len(exp) == len(pred)

    mse = statistics.mean(((x[0] - x[1]) ** 2 for x in zip(exp, pred)))

    return mse


def graph_rlooper_full_seq(plasmid_type, plasmid, expected):
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

            pyplot.plot(
                list(range(1, len(gene_region_probability) + 1)),
                gene_region_probability,
                label="Rlooper (Full)",
            )

            mse = calculate_mse(expected, gene_region_probability)
            rmsd = calculate_rmsd(expected, gene_region_probability)
            rsquared = calculate_rsquared(expected, gene_region_probability)
            kstest = scipy.stats.ks_2samp(expected, gene_region_probability)

            return dict(mse=mse, rmsd=rmsd, rsquared=rsquared, kstest=kstest)


def graph_rlooper_gene(plasmid_type, plasmid, expected):
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

            pyplot.plot(
                list(range(1, len(gene_region_probability) + 1)),
                gene_region_probability,
                label="Rlooper (Gene)",
            )

            mse = calculate_mse(expected, gene_region_probability)
            rmsd = calculate_rmsd(expected, gene_region_probability)
            rsquared = calculate_rsquared(expected, gene_region_probability)
            kstest = scipy.stats.ks_2samp(expected, gene_region_probability)

            return dict(mse=mse, rmsd=rmsd, rsquared=rsquared, kstest=kstest)


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


def aggregate_graph(
    plasmid_type, plasmid, folder, avg_only: bool = False, rlooper: bool = False
) -> None:
    print(folder)
    subfolders = [f for f in pathlib.Path(folder).iterdir() if f.is_dir()]
    files = []

    for subfolder in subfolders:
        files.extend(
            glob.glob(f"{subfolder}/{plasmid}*{plasmid_type}*base_in_loop.xlsx")
        )

    average_probabilities_list = None
    print(plasmid_type, plasmid, files)

    for file in files:
        wb = openpyxl.load_workbook(file)
        ws = wb.active

        m = re.match(r"^.*_w\d_(\d*)_", str(file))
        run_number = int(m[1])

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
            average_probabilities_list = probabilities_list
        else:
            average_probabilities_list = [
                sum(value)
                for value in zip(average_probabilities_list, probabilities_list)
            ]

        if not avg_only:
            pyplot.plot(
                list(range(1, len(probabilities_list) + 1)),
                probabilities_list,
                label=f"Run {run_number}",
            )

    div_by_file_len = lambda x: x / len(files)
    average_probabilities_list = list(map(div_by_file_len, average_probabilities_list))

    wb = openpyxl.load_workbook(
        pathlib.Path("experimental") / f"{plasmid}_{plasmid_type}_experimental.xlsx"
    )
    ws = wb.active

    row_value_iter = iter(ws.values)
    next(row_value_iter)  # Skip the column header

    probabilities = collections.defaultdict(lambda: 0)
    for row in row_value_iter:
        base_position, probability = row
        base_position = int(base_position)
        probability = float(probability)

        probabilities[base_position] = probability

    probabilities_list = [
        probabilities[k] for k in range(1, len(probabilities.keys()) + 1)
    ]

    print("MAX", max(probabilities_list), max(average_probabilities_list))
    print("SUM", sum(probabilities_list), sum(average_probabilities_list))
    mse = calculate_mse(probabilities_list, average_probabilities_list)
    rmsd = calculate_rmsd(probabilities_list, average_probabilities_list)
    rsquared = calculate_rsquared(probabilities_list, average_probabilities_list)
    kstest = scipy.stats.ks_2samp(probabilities_list, average_probabilities_list)

    pyplot.plot(
        list(range(1, len(probabilities_list) + 1)),
        probabilities_list,
        label=f"Experimental",
    )

    rlooper_full_dict = None
    if rlooper:
        rlooper_full_dict = graph_rlooper_full_seq(
            plasmid_type, plasmid, probabilities_list
        )

    rlooper_gene = None
    if rlooper:
        rlooper_gene = graph_rlooper_gene(plasmid_type, plasmid, probabilities_list)

    pyplot.plot(
        list(range(1, len(average_probabilities_list) + 1)),
        average_probabilities_list,
        "--",
        label=f"Average",
    )

    row_value_iter = iter(ws.values)
    next(row_value_iter)  # Skip the column header

    pyplot.plot()

    m = re.search(r"p(\d*)_w(\d*)", str(folder))

    padding = m[1]
    width = m[2]

    # pyplot.figtext(.75, .2, f"Width = {width}\nPadding = {padding}")
    pyplot.legend()
    pyplot.title(
        f"{plasmid_type if 'CR' not in plasmid_type else plasmid_type[:-2]} Prediction on {plasmid} (pFC8 $\cup$ pFC53; $n={width}$, $p={padding}$)"
    )
    pyplot.xlabel("Base Position")
    pyplot.ylabel("Probability")

    pyplot.gca().set_ylim(0, 1.0)

    pyplot.savefig(
        f'union_{plasmid_type}_{plasmid}_p{padding}_w{width}{"" if not avg_only else "_avg"}.eps'
    )

    fig = pyplot.figure()
    pyplot.figure().clear()
    pyplot.close()
    pyplot.cla()
    pyplot.clf()

    return (
        dict(mse=mse, rmsd=rmsd, rsquared=rsquared, kstest=kstest),
        rlooper_full_dict,
        rlooper_gene,
    )


WIDTH = 4

GRAPH_RLOOPER = True
GRAPH_AVG_ONLY = True

if __name__ == "__main__":
    plasmid_types = ["GYRASECR", "SUPERCOILEDCR", "LINEARIZED"]
    table = prettytable.PrettyTable()
    table.field_names = [
        "Plasmid Type",
        "Plasmid",
        "Width",
        "Padding",
        "MSE",
        "RMSD",
        "RSQUARED",
        "KS_2SAMP",
    ]
    table.align = "l"

    for padding in [13]:
        for plasmid_type in plasmid_types:
            union_folder_name = glob.glob(f"*{plasmid_type}*{plasmid_type}*")
            print(union_folder_name)
            folders = [union_folder_name[0]]
            plasmids = ["pFC8", "pFC53"]

            print(folders)
            for plasmid in plasmids:
                for folder in folders:
                    stats = aggregate_graph(
                        plasmid_type,
                        plasmid,
                        folder,
                        avg_only=GRAPH_AVG_ONLY,
                        rlooper=GRAPH_RLOOPER,
                    )

                    row = [plasmid_type, plasmid, WIDTH, padding]
                    row.extend(list(map(lambda x: x, stats[0].values())))
                    table.add_row(row)

                    if stats[1]:
                        row = [plasmid_type + " (Rlooper)", plasmid, WIDTH, padding]
                        row.extend(list(map(lambda x: x, stats[1].values())))
                        table.add_row(row)

                    if stats[2]:
                        row = [
                            plasmid_type + " (Rlooper Gene)",
                            plasmid,
                            WIDTH,
                            padding,
                        ]
                        row.extend(list(map(lambda x: x, stats[2].values())))
                        table.add_row(row)

                    # aggregate_graph(plasmid_type, plasmid, folder, avg_only=True)

    print(table)
