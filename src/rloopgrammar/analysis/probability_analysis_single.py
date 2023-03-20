import os
import re
import matplotlib.pyplot as pyplot
import matplotlib.colors as mcolors

from matplotlib.patches import Patch
from matplotlib.lines import Line2D

from pathlib import Path

RUNS = 10

def collect_probabilities(folder: str):
    print(folder)
    m = re.search(r'p(\d*)_w(\d*)', folder)

    padding = m[1]
    width = m[2]

    run_folders = [(r, Path(folder) / Path('_'.join(map(str, ["UNION", f'p{padding}', f'w{width}', r])))) for r in range(RUNS)]

    S_data = [[] for _ in range(4)]
    P_data = [[] for _ in range(5)]
    R_data = [[] for _ in range(4)]
    L_data = [[] for _ in range(5)]
    Q_data = [[] for _ in range(4)]
    T_data = [[] for _ in range(5)]

    for run, folder in run_folders:
        probs_lang_filename = Path('_'.join(map(str, 
            ['SHANNON', f'p{padding}', f'w{width}', f'{run}', 'union', 'probabilities.py']))
        )

        print(folder, probs_lang_filename)
        with open(folder / probs_lang_filename, 'r') as probs_file:
            probs = list(map(lambda x: float(x.split('=')[1]), probs_file.readlines()))

            S = probs[0:4]

            for i, prob in enumerate(S):
                S_data[i].append(prob)

            P = probs[4:9]

            for i, prob in enumerate(P):
                P_data[i].append(prob)

            R = probs[9:13]

            for i, prob in enumerate(R):
                R_data[i].append(prob)

            L = probs[13:18]
            for i, prob in enumerate(L):
                L_data[i].append(prob)

            Q = probs[18:22]
            for i, prob in enumerate(Q):
                Q_data[i].append(prob)

            T = probs[22:28]
            for i, prob in enumerate(T):
                T_data[i].append(prob)

    return (S_data, P_data, R_data, L_data, Q_data, T_data)


if __name__ == "__main__":
    colors = ['orange', 'blue', 'black']

    folder_names = ["UNION_GYRASECR_p13_w4", "UNION_SUPERCOILEDCR_p13_w4", "UNION_LINEARIZED_p13_w4_FIXED"]
    collected_probabilities = []

    for folder in folder_names:
        collected_probabilities.append(collect_probabilities(folder))
    
    folder_names = list(map(lambda x: x.split('_')[1], folder_names))
    title_names = ', '.join(folder_names)
    TITLE = f"(pFC8 $\cup$ pFC53) [{title_names}] Production Rule Probabilities ($4$-tuple, padding=13)"

    legend_elements = [Patch(facecolor=colors[i], label=folder_names[i]) for i in range(len(colors))]
    legend_elements.reverse()

    fig = pyplot.figure(figsize=(18,6))

    pyplot.suptitle(TITLE, fontsize=12)
    pyplot.legend(loc='best', handles=legend_elements)
    pyplot.xticks(fontsize=6)
    pyplot.ylabel('Probability')
    pyplot.xlabel('Production Rules')

    for i, col_p in enumerate(collected_probabilities):
        pyplot.boxplot(col_p[0][0], showfliers=False, showmeans=True, patch_artist=True, whiskerprops=dict(alpha=0), showcaps=False, labels=[
            r'$S \rightarrow \sigma \; P \; | \; \hat{\sigma} \; P \; | \; \delta \; P \; | \; \gamma \; P$'
        ] if i == 0 else [''])


    p_bplots = []
    for i, col_p in enumerate(collected_probabilities):
        positions = list(map(lambda x: (x + (((0.8 / len(col_p) + 0.05) * (i - 1)) * (-1 ** i))), [2, 3, 4, 5, 6]))
        p_bplots.append(pyplot.boxplot(col_p[1], widths=0.8 / len(col_p), positions=positions, showfliers=False, whiskerprops=dict(linestyle='dashed'), patch_artist=True, labels=[
            r'$P \rightarrow \sigma \; P$',
            r'$P \rightarrow \hat{\sigma} \; P$',
            r'$P \rightarrow \gamma \; P$',
            r'$P \rightarrow \delta \; P$',
            r'$P \rightarrow \alpha \; R$'
        ] if i == 1 else [''] * 5))

    for bplot, color in zip(p_bplots, colors):
        for patch in bplot['boxes']:
            patch.set_facecolor(color)

    #axes[0][1].legend([bp["boxes"][0] for bp in p_bplots], folder_names, loc='upper right')

    r_bplots = []
    for i, col_p in enumerate(collected_probabilities):
        positions = list(map(lambda x: (x + (((0.8 / len(col_p) + 0.05) * (i - 1)) * (-1 ** i))), [7, 8, 9, 10]))
        r_bplots.append(pyplot.boxplot(col_p[2], widths=0.8 / len(col_p), positions=positions, showfliers=False, whiskerprops=dict(linestyle='dashed'), patch_artist=True, labels=[
            r'$R \rightarrow \tau \; L$',
            r'$R \rightarrow \hat{\tau} \; L$',
            r'$R \rightarrow \rho \; L$',
            r'$R \rightarrow \beta \; L$'
        ] if i == 1 else [''] * 4))

    for bplot, color in zip(r_bplots, colors):
        for patch in bplot['boxes']:
            patch.set_facecolor(color)


    l_bplots = []
    for i, col_p in enumerate(collected_probabilities):
        positions = list(map(lambda x: (x + (((0.8 / len(col_p) + 0.05) * (i - 1)) * (-1 ** i))), [11, 12, 13, 14, 15]))
        l_bplots.append(pyplot.boxplot(col_p[3], widths=0.8 / len(col_p), positions=positions, showfliers=False, whiskerprops=dict(linestyle='dashed'), patch_artist=True, labels=[
            r'$L \rightarrow \tau \; L$',
            r'$L \rightarrow \hat{\tau} \; L$',
            r'$L \rightarrow \rho \; L$',
            r'$L \rightarrow \beta \; L$',
            r'$L \rightarrow \omega \; Q$'
        ] if i == 1 else [''] * 5))

    for bplot, color in zip(l_bplots, colors):
        for patch in bplot['boxes']:
            patch.set_facecolor(color)


    q_bplots = []
    for i, col_p in enumerate(collected_probabilities):
        positions = list(map(lambda x: (x + (((0.8 / len(col_p) + 0.05) * (i - 1)) * (-1 ** i))), [16, 17, 18, 19]))
        q_bplots.append(pyplot.boxplot(col_p[4], widths=0.8 / len(col_p), positions=positions, showfliers=False, whiskerprops=dict(linestyle='dashed'), patch_artist=True, labels=[
            r'$Q \rightarrow \sigma \; T$',
            r'$Q \rightarrow \hat{\sigma} \; T$',
            r'$Q \rightarrow \gamma \; T$',
            r'$Q \rightarrow \delta \; T$'
        ] if i == 1 else [''] * 4))

    for bplot, color in zip(q_bplots, colors):
        for patch in bplot['boxes']:
            patch.set_facecolor(color)

    t_bplots = []
    for i, col_p in enumerate(collected_probabilities):
        positions = list(map(lambda x: (x + (((0.8 / len(col_p) + 0.05) * (i - 1)) * (-1 ** i))), [20, 21, 22, 23, 24]))
        t_bplots.append(pyplot.boxplot(col_p[5], widths=0.8 / len(col_p), positions=positions, showfliers=False, whiskerprops=dict(linestyle='dashed'), patch_artist=True, labels=[
            r'$T \rightarrow \sigma \; T$',
            r'$T \rightarrow \hat{\sigma} \; T$',
            r'$T \rightarrow \gamma \; T$',
            r'$T \rightarrow \delta \; T$',
            r'$T \rightarrow \epsilon$'
        ] if i == 1 else [''] * 5))

    for bplot, color in zip(t_bplots, colors):
        for patch in bplot['boxes']:
            patch.set_facecolor(color)


    pyplot.subplots_adjust(left=0.045, right=0.9875)
    pyplot.show()

    fig.savefig(f'{"_".join(folder_names)}_single.png', dpi=1200)
