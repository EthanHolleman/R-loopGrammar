import os
import re
import matplotlib.pyplot as pyplot
import matplotlib.colors as mcolors

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
    colors = ['black'] * 4

    folder_names = ["UNION_SUPERCOILED_p13_w4", "UNION_SUPERCOILEDCR_p13_w4," "UNION_GYRASE_p13_w4", "UNION_GYRASECR_p13_w4"]
    collected_probabilities = []

    for folder in folder_names:
        collected_probabilities.append(collect_probabilities(folder))
    
    title_names = '\n'.join(folder_names)
    TITLE = f"(pFC8 $\cup$ pFC53) [{title_names}] Union"

    fig1, ax1 = pyplot.subplots()
    ax1.set_title(f'{TITLE} $S$ Transitions')
    fig1.subplots_adjust(top=1.0 - 0.05 * len(collected_probabilities))

    for i, col_p in enumerate(collected_probabilities):
        ax1.boxplot(col_p[0], showfliers=False, showmeans=True, patch_artist=True, whiskerprops=dict(alpha=0), showcaps=False, labels=[
            r'$S \rightarrow \sigma \; P$',
            r'$S \rightarrow \hat{\sigma} \; P$',
            r'$S \rightarrow \delta \; P$',
            r'$S \rightarrow \gamma \; P$'
        ] if i == 0 else [''] * 4)

    fig2, ax2 = pyplot.subplots()
    ax2.set_title(f'{TITLE} $P$ Transitions')
    fig2.subplots_adjust(top=1.0 - 0.05 * len(collected_probabilities))

    p_bplots = []
    for i, col_p in enumerate(collected_probabilities):
        p_bplots.append(ax2.boxplot(col_p[1], showfliers=False, showmeans=False, whiskerprops=dict(alpha=0), showcaps=False, patch_artist=True, labels=[
            r'$P \rightarrow \sigma \; P$',
            r'$P \rightarrow \hat{\sigma} \; P$',
            r'$P \rightarrow \gamma \; P$',
            r'$P \rightarrow \delta \; P$',
            r'$P \rightarrow \alpha \; R$'
        ] if i == 0 else [''] * 5))

    for bplot, color in zip(p_bplots, colors):
        for patch in bplot['boxes']:
            patch.set_facecolor(color)
            patch.set_alpha(1.0 / len(collected_probabilities))

    ax2.legend([bp["boxes"][0] for bp in p_bplots], folder_names, loc='upper right')

    fig3, ax3 = pyplot.subplots()
    ax3.set_title(f'{TITLE} $R$ Transitions')
    fig3.subplots_adjust(top=1.0 - 0.05 * len(collected_probabilities))

    r_bplots = []
    for i, col_p in enumerate(collected_probabilities):
        r_bplots.append(ax3.boxplot(col_p[2], showfliers=False, showmeans=False, whiskerprops=dict(alpha=0), showcaps=False, patch_artist=True, labels=[
            r'$R \rightarrow \tau \; L$',
            r'$R \rightarrow \hat{\tau} \; L$',
            r'$R \rightarrow \rho \; L$',
            r'$R \rightarrow \beta \; L$'
        ] if i == 0 else [''] * 4))

    for bplot, color in zip(r_bplots, colors):
        for patch in bplot['boxes']:
            patch.set_facecolor(color)
            patch.set_alpha(1.0 / len(collected_probabilities))

    ax3.legend([bp["boxes"][0] for bp in r_bplots], folder_names, loc='upper right')

    fig4, ax4 = pyplot.subplots()
    ax4.set_title(f'{TITLE} $L$ Transitions')
    fig4.subplots_adjust(top=1.0 - 0.05 * len(collected_probabilities))

    l_bplots = []
    for i, col_p in enumerate(collected_probabilities):
        l_bplots.append(ax4.boxplot(col_p[3], showfliers=False, showmeans=False, whiskerprops=dict(alpha=0), showcaps=False, patch_artist=True, labels=[
            r'$L \rightarrow \tau \; L$',
            r'$L \rightarrow \hat{\tau} \; L$',
            r'$L \rightarrow \rho \; L$',
            r'$L \rightarrow \beta \; L$',
            r'$L \rightarrow \omega \; Q$'
        ] if i == 0 else [''] * 5))

    for bplot, color in zip(l_bplots, colors):
        for patch in bplot['boxes']:
            patch.set_facecolor(color)
            patch.set_alpha(1.0 / len(collected_probabilities))

    ax4.legend([bp["boxes"][0] for bp in l_bplots], folder_names, loc='upper right')


    fig5, ax5 = pyplot.subplots()
    ax5.set_title(f'{TITLE} $Q$ Transitions')
    fig5.subplots_adjust(top=1.0 - 0.05 * len(collected_probabilities))

    q_bplots = []
    for i, col_p in enumerate(collected_probabilities):
        q_bplots.append(ax5.boxplot(col_p[4], showfliers=False, showmeans=False, whiskerprops=dict(alpha=0), showcaps=False, patch_artist=True, labels=[
            r'$Q \rightarrow \sigma \; T$',
            r'$Q \rightarrow \hat{\sigma} \; T$',
            r'$Q \rightarrow \gamma \; T$',
            r'$Q \rightarrow \delta \; T$'
        ] if i == 0 else [''] * 4))

    for bplot, color in zip(q_bplots, colors):
        for patch in bplot['boxes']:
            patch.set_facecolor(color)
            patch.set_alpha(1.0 / len(collected_probabilities))

    ax5.legend([bp["boxes"][0] for bp in q_bplots], folder_names, loc='upper right')

    fig6, ax6 = pyplot.subplots()
    ax6.set_title(f'{TITLE} $T$ Transitions')
    fig6.subplots_adjust(top=1.0 - 0.05 * len(collected_probabilities))

    t_bplots = []
    for i, col_p in enumerate(collected_probabilities):
        t_bplots.append(ax6.boxplot(col_p[5], showfliers=False, showmeans=False, whiskerprops=dict(alpha=0), showcaps=False, patch_artist=True, labels=[
            r'$T \rightarrow \sigma \; T$',
            r'$T \rightarrow \hat{\sigma} \; T$',
            r'$T \rightarrow \gamma \; T$',
            r'$T \rightarrow \delta \; T$',
            r'$T \rightarrow \epsilon$'
        ] if i == 0 else [''] * 5))

    for bplot, color in zip(t_bplots, colors):
        for patch in bplot['boxes']:
            patch.set_facecolor(color)
            patch.set_alpha(1.0 / len(collected_probabilities))

    ax6.legend([bp["boxes"][0] for bp in t_bplots], folder_names, loc='upper right')

    """
    fig1.savefig(f'{os.path.basename(os.getcwd())}_s_transitions.png', dpi=1200)
    fig2.savefig(f'{os.path.basename(os.getcwd())}_p_transitions.png', dpi=1200)
    fig3.savefig(f'{os.path.basename(os.getcwd())}_r_transitions.png', dpi=1200)
    fig4.savefig(f'{os.path.basename(os.getcwd())}_l_transitions.png', dpi=1200)
    fig5.savefig(f'{os.path.basename(os.getcwd())}_q_transitions.png', dpi=1200)
    fig6.savefig(f'{os.path.basename(os.getcwd())}_t_transitions.png', dpi=1200)
    """

    pyplot.show()
