import os
import re
import matplotlib.pyplot as pyplot
import matplotlib.colors as mcolors
import json

from matplotlib.patches import Patch
from matplotlib.lines import Line2D

from pathlib import Path

RUNS = 10


def collect_probabilities(parent_folder: str):
    import pathlib

    parent_folder = pathlib.Path(parent_folder)
    print(list(os.walk(parent_folder))[0])

    run_folders = enumerate(
        sorted([x[1] for x in os.walk(parent_folder)][0], key=lambda x: int(x[-1]))
    )

    S_data = []
    R_data = []
    Q_data = []

    for run, folder in run_folders:
        model_files = next(os.walk(parent_folder / folder))[2]

        model_files_find = lambda y: list(filter(lambda x: y in x, model_files))[0]

        probs_lang_filename = model_files_find("union_probabilities")

        print(folder, probs_lang_filename)
        with open(parent_folder / folder / probs_lang_filename, "r") as probs_file:
            probs = json.load(probs_file)

            S_data.append(probs["S_probabilities"])
            R_data.append(probs["R_probabilities"])
            Q_data.append(probs["Q_probabilities"])

    import collections
    import functools
    import operator

    with open("out_averaged_probabilities.json", "w") as outfile:
        avg_s_probabilities = dict(
            functools.reduce(operator.add, map(collections.Counter, S_data))
        )
        avg_r_probabilities = dict(
            functools.reduce(operator.add, map(collections.Counter, R_data))
        )
        avg_q_probabilities = dict(
            functools.reduce(operator.add, map(collections.Counter, Q_data))
        )
        json.dump(
            {
                "S_probabilities": {
                    k: v / len(S_data) for k, v in avg_s_probabilities.items()
                },
                "R_probabilities": {
                    k: v / len(R_data) for k, v in avg_r_probabilities.items()
                },
                "Q_probabilities": {
                    k: v / len(Q_data) for k, v in avg_q_probabilities.items()
                },
            },
            outfile,
            indent=4,
        )

    return (S_data, R_data, Q_data)


# REPLACING THESE FOR GRAPH
REPLACE = {"GYRASE": "Gyrase", "SUPERCOILEDCR": "Supercoiled", "LINEARIZED": "Linear"}

if __name__ == "__main__":
    colors = ["orange", "blue", "black"]

    folder_names = [
        "UnionCollection_GYRASECR_runs_10",
        "UnionCollection_SUPERCOILEDCR_runs_10",
        "UnionCollection_LINEARIZED_runs_10",
    ]

    collected_probabilities = []

    for folder in folder_names:
        collected_probabilities.append(collect_probabilities(folder))

    folder_names = list(map(lambda x: x.split("_")[2], folder_names))
    for i in range(len(folder_names)):
        for k, v in REPLACE.items():
            if k in folder_names[i]:
                folder_names[i] = v

    title_names = ", ".join(folder_names)
    TITLE = f"Production rule probabilities for the union of dictionaries"

    legend_elements = [
        Patch(facecolor=colors[i], label=folder_names[i]) for i in range(len(colors))
    ]
    legend_elements.reverse()

    pyplot.rcParams["font.family"] = "Times New Roman"

    fig = pyplot.figure(figsize=(18, 6))

    pyplot.title(TITLE, fontsize=20)
    pyplot.legend(
        loc="best",
        handles=legend_elements,
        fontsize=12,
        title=f"pFC8 $\cup$ pFC53\n $n={4}$, $p={13}$",
        title_fontsize=13,
    )

    pyplot.ylabel("Probability", fontsize=20)
    pyplot.xticks(fontsize=16)
    pyplot.yticks(fontsize=16)
    pyplot.xlabel("Production rule", fontsize=20)

    # remove hard coded values
    # pyplot.figtext(0.905, 0.130, f"pFC8 $\cup$ pFC53\n $n={4}$, $p={13}$", fontsize=14)

    """
    for i, col_p in enumerate(collected_probabilities):
        pyplot.boxplot(col_p[0][0], showfliers=False, showmeans=True, patch_artist=True, whiskerprops=dict(alpha=0), showcaps=False, labels=[
            r'$S \rightarrow \sigma \; P \; | \; \hat{\sigma} \; P \; | \; \delta \; P \; | \; \gamma \; P$'
        ] if i == 0 else [''])
    """

    pyplot.margins(x=0)

    xposition = [1.75, 3.25, 4.75, 4.75 + 1.5, 4.75 + 3]
    for xc in xposition:
        pyplot.axvline(x=xc, color="k", linestyle="--", alpha=0.3)

    s_bplots = []
    for i, col_p in enumerate(collected_probabilities):
        print("p_bplots", len(col_p[0]))
        positions = list(
            map(
                lambda x: (x + (((0.8 / len(col_p) + 0.05) * (i - 1)) * (-(1**i)))),
                [1, 2.5],
            )
        )
        s_bplots.append(
            pyplot.boxplot(
                [
                    [entry["S_gamma_S"] for entry in col_p[0]],
                    [entry["S_delta_S"] for entry in col_p[0]],
                ],
                widths=0.8 / len(col_p),
                positions=positions,
                showfliers=False,
                whiskerprops=dict(linestyle="dashed"),
                patch_artist=True,
                labels=[
                    r"$S \rightarrow \gamma \; S$",
                    r"$S \rightarrow \delta \; S$",
                ]
                if i == 1
                else [""] * 2,
            )
        )

    for bplot, color in zip(s_bplots, colors):
        for patch in bplot["boxes"]:
            patch.set_facecolor(color)

    # axes[0][1].legend([bp["boxes"][0] for bp in p_bplots], folder_names, loc='upper right')

    r_bplots = []
    for i, col_p in enumerate(collected_probabilities):
        positions = list(
            map(
                lambda x: (x + (((0.8 / len(col_p) + 0.05) * (i - 1)) * (-(1**i)))),
                [4, 5.5],
            )
        )
        r_bplots.append(
            pyplot.boxplot(
                [
                    [entry["R_rho_R"] for entry in col_p[1]],
                    [entry["R_beta_R"] for entry in col_p[1]],
                ],
                widths=0.8 / len(col_p),
                positions=positions,
                showfliers=False,
                whiskerprops=dict(linestyle="dashed"),
                patch_artist=True,
                labels=[
                    r"$R \rightarrow \rho \; R$",
                    r"$R \rightarrow \beta \; R$",
                ]
                if i == 1
                else [""] * 2,
            )
        )

    for bplot, color in zip(r_bplots, colors):
        for patch in bplot["boxes"]:
            patch.set_facecolor(color)

    q_bplots = []
    for i, col_p in enumerate(collected_probabilities):
        positions = list(
            map(
                lambda x: (x + (((0.8 / len(col_p) + 0.05) * (i - 1)) * (-(1**i)))),
                [7, 8.5],
            )
        )
        q_bplots.append(
            pyplot.boxplot(
                [
                    [entry["Q_gamma_Q"] for entry in col_p[2]],
                    [entry["Q_delta_Q"] for entry in col_p[2]],
                ],
                widths=0.8 / len(col_p),
                positions=positions,
                showfliers=False,
                whiskerprops=dict(linestyle="dashed"),
                patch_artist=True,
                labels=[
                    r"$Q \rightarrow \gamma \; Q$",
                    r"$Q \rightarrow \delta \; Q$",
                ]
                if i == 1
                else [""] * 2,
            )
        )

    for bplot, color in zip(q_bplots, colors):
        for patch in bplot["boxes"]:
            patch.set_facecolor(color)

    pyplot.subplots_adjust(left=0.065, right=0.9875)
    pyplot.show()

    fig.savefig(f'{"_".join(folder_names)}_single_trunc.eps', format="eps")
