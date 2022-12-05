import os
import re
import matplotlib.pyplot as pyplot
import matplotlib.colors as mcolors
import json

from matplotlib.patches import Patch
from matplotlib.lines import Line2D

from pathlib import Path

RUNS = 10


def collect_probabilities(folder: str):
    print(folder)
    m = re.search(r"p(\d*)_w(\d*)", folder)

    padding = m[1]
    width = m[2]

    run_folders = [
        (
            r,
            Path(folder)
            / Path("_".join(map(str, ["UNION", f"p{padding}", f"w{width}", r]))),
        )
        for r in range(RUNS)
    ]

    S_data = []
    R_data = []
    Q_data = []

    for run, folder in run_folders:
        probs_lang_filename = Path(
            "_".join(
                map(
                    str,
                    [
                        "SHANNON",
                        f"p{padding}",
                        f"w{width}",
                        f"{run}",
                        "union",
                        "probabilities.json",
                    ],
                )
            )
        )

        print(folder, probs_lang_filename)
        with open(folder / probs_lang_filename, "r") as probs_file:
            probs = json.load(probs_file)

            S_data.append(probs["S_probabilities"])
            R_data.append(probs["R_probabilities"])
            Q_data.append(probs["Q_probabilities"])

    return (S_data, R_data, Q_data)


# REPLACING THESE FOR GRAPH
REPLACE = {"GYRASECR": "GYRASE", "SUPERCOILEDCR": "SUPERCOILED"}

if __name__ == "__main__":
    colors = ["orange", "blue", "black"]

    folder_names = [
        "UNION_GYRASECR_p13_w4",
        "UNION_SUPERCOILEDCR_p13_w4",
        "UNION_LINEARIZED_p13_w4",
    ]
    collected_probabilities = []

    for folder in folder_names:
        collected_probabilities.append(collect_probabilities(folder))

    folder_names = list(map(lambda x: x.split("_")[1], folder_names))
    for i in range(len(folder_names)):
        for k, v in REPLACE.items():
            if k in folder_names[i]:
                folder_names[i] = v

    title_names = ", ".join(folder_names)
    TITLE = f"Production Rule Probabilities for the Union (pFC8 $\cup$ pFC53; $n=4$, $p=13$)"

    legend_elements = [
        Patch(facecolor=colors[i], label=folder_names[i]) for i in range(len(colors))
    ]
    legend_elements.reverse()

    fig = pyplot.figure(figsize=(18, 6))

    pyplot.suptitle(TITLE, fontsize=20)
    pyplot.legend(loc="best", handles=legend_elements)
    pyplot.ylabel("Probability", fontsize=20)
    pyplot.xticks(fontsize=16)
    pyplot.yticks(fontsize=16)
    pyplot.xlabel("Production Rules", fontsize=20)

    """
    for i, col_p in enumerate(collected_probabilities):
        pyplot.boxplot(col_p[0][0], showfliers=False, showmeans=True, patch_artist=True, whiskerprops=dict(alpha=0), showcaps=False, labels=[
            r'$S \rightarrow \sigma \; P \; | \; \hat{\sigma} \; P \; | \; \delta \; P \; | \; \gamma \; P$'
        ] if i == 0 else [''])
    """

    s_bplots = []
    for i, col_p in enumerate(collected_probabilities):
        print("p_bplots", len(col_p[0]))
        positions = list(
            map(
                lambda x: (x + (((0.8 / len(col_p) + 0.05) * (i - 1)) * (-(1**i)))),
                [2, 3],
            )
        )
        s_bplots.append(
            pyplot.boxplot(
                [
                    [entry["S_sigma_S"] for entry in col_p[0]],
                    [entry["S_sigma_hat_S"] for entry in col_p[0]],
                ],
                widths=0.8 / len(col_p),
                positions=positions,
                showfliers=False,
                whiskerprops=dict(linestyle="dashed"),
                patch_artist=True,
                labels=[
                    r"$S \rightarrow \sigma \; S$",
                    r"$S \rightarrow \hat{\sigma} \; S$",
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
                [4, 5],
            )
        )
        r_bplots.append(
            pyplot.boxplot(
                [
                    [entry["R_tau_R"] for entry in col_p[1]],
                    [entry["R_tau_hat_R"] for entry in col_p[1]],
                ],
                widths=0.8 / len(col_p),
                positions=positions,
                showfliers=False,
                whiskerprops=dict(linestyle="dashed"),
                patch_artist=True,
                labels=[
                    r"$R \rightarrow \tau \; R$",
                    r"$R \rightarrow \hat{\tau} \; R$",
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
                [6, 7],
            )
        )
        q_bplots.append(
            pyplot.boxplot(
                [
                    [entry["Q_sigma_Q"] for entry in col_p[2]],
                    [entry["Q_sigma_hat_Q"] for entry in col_p[2]],
                ],
                widths=0.8 / len(col_p),
                positions=positions,
                showfliers=False,
                whiskerprops=dict(linestyle="dashed"),
                patch_artist=True,
                labels=[
                    r"$Q \rightarrow \sigma \; Q$",
                    r"$Q \rightarrow \hat{\sigma} \; Q$",
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
