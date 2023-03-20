import os
import matplotlib.pyplot as pyplot

from collections import defaultdict
from pathlib import Path

PLASMIDS = ["pFC8_LINEARIZED", "pFC53_LINEARIZED"]
RUNS = 10
PADDING = 7
WIDTH = 4

class RLoop:
    def __init__(self, plasmid, start: int, end: int, expr_number: int):
        self.plasmid = plasmid
        self.start = int(start)
        self.end = int(end)
        self.expr_number = expr_number

    def __eq__(self, other: "RLoop"):
        return self.plasmid == other.plasmid and self.start == other.start \
            and self.end == other.end and self.expr_number == other.expr_number

    def __repr__(self):
        return f"R<{self.plasmid}, {self.start}, {self.end}>"

    def __hash__(self):
        return hash((self.plasmid, self.start, self.end, self.expr_number))


def read_all_rloops(bed_file):
    return [RLoop(*t.split()[0:3] + [i]) for i, t in enumerate(bed_file.readlines())]

if __name__ == "__main__":
    run_folders = [
        (r, Path('_'.join(map(str, ['UNION', f'p{PADDING}', f'w{WIDTH}', r])))) for r in range(RUNS)
    ]

    original_bed_filenames = [Path(f'{plasmid}.bed') for plasmid in PLASMIDS]

    coverage_freq = defaultdict(lambda: 0)
    coverage = set()

    for run, folder in run_folders:
        training_set_filenames = [Path('_'.join(map(str, 
            [plasmid, f'p{PADDING}', f'w{WIDTH}', f'{run}.bed_extra_training-set.bed']))
        ) for plasmid in PLASMIDS]

        for tsf in training_set_filenames:
            with open(folder / tsf, 'r') as training_set:
                locations = read_all_rloops(training_set)
                coverage |= set(locations)
                for loc in locations:
                    coverage_freq[loc] += 1

    reversed_order_coverage_frequency = {
        k : v for k, v in sorted(coverage_freq.items(), key=lambda x: x[1], reverse=True)
    }

    print("LEN", len(reversed_order_coverage_frequency.items()))

    total_rloops = set()
    for obf in original_bed_filenames:
        with open(obf, 'r') as bed_file:
            total_rloops |= set(read_all_rloops(bed_file))

    print("COVERAGE", len(coverage) / len(total_rloops))
    print("SIZES", len(coverage), len(total_rloops))

    sizes = [int(len(coverage) / len(total_rloops) * 100)]
    explode = (0, 0, 0, 0)

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.show()

    """
    pfc8_rloops_filename = original_bed_filenames[0]
    pfc8_rloops = []
    pfc8_coverage_freq = defaultdict(lambda: 0)

    with open(pfc8_rloops_filename, 'r') as pfc8_bedfile:
        pfc8_rloops = read_all_rloops(pfc8_bedfile)
        for rloop in pfc8_rloops:
            pfc8_coverage_freq[rloop] += 1

    reversed_order_coverage_frequency_pfc8 = {
        k : v for k, v in sorted(pfc8_coverage_freq.items(), key=lambda x: x[1], reverse=True)
    }


    pfc53_rloops_filename  = original_bed_filenames[1]
    pfc53_rloops = []
    pfc53_coverage_freq = defaultdict(lambda: 0)

    with open(pfc53_rloops_filename, 'r') as pfc53_bedfile:
        pfc53_rloops = read_all_rloops(pfc53_bedfile)
        for rloop in pfc53_rloops:
            pfc53_coverage_freq[rloop] += 1

    reversed_order_coverage_frequency_pfc53 = {
        k : v for k, v in sorted(pfc53_coverage_freq.items(), key=lambda x: x[1], reverse=True)
    }

    print(
        len(reversed_order_coverage_frequency_pfc8.items()) + \
        len(reversed_order_coverage_frequency_pfc53.items())
    )

    print(list(reversed_order_coverage_frequency_pfc8.items())[0:10])
    """

            


